import os
import argparse
from tqdm import tqdm
import json
import numpy as np
from operator import attrgetter
import sys

from pyserini import search
from pyserini import index
from pyserini import analysis

from general_utils import utils
from database_utils import db_utils
from graph.graph import Graph
from graph.graph_comparators.DCoreComparator import DCoreComparator


parser = argparse.ArgumentParser()
parser.add_argument('--index', dest='index', default='lucene-index.core18.pos+docvectors+rawdocs_all',
                    help='specify the corpus index')

parser.add_argument('--db', dest='db', default='entity_database_19.db',
                    help='specify the database')

parser.add_argument('--embedding', dest='embedding', default='',
                    help='specify the embeddings to use')

parser.add_argument('--stats', dest='stats', default=False,
                    help='Show index stats')

parser.add_argument('--year', dest='year', default=19, type=int,
                    help='TREC year 18, 19 or 20')

parser.add_argument('--topics', dest='topics', default='topics.backgroundlinking19.txt',
                    help='specify qrels file')

parser.add_argument('--candidates', dest='candidates', default='run.backgroundlinking19.bm25+rm3.topics.backgroundlinking19.txt',
                    help='Results file that carries candidate docs')

parser.add_argument('--qrels', dest='qrels', default='qrels.backgroundlinking19.txt',
                    help='specify qrels file')

parser.add_argument('--output', dest='output', default='output_graph.txt',
                    help='specify output file')

parser.add_argument('--run-tag', dest='run_tag', default='unspecified_run_tag',
                    help='specify run tag')

parser.add_argument('--anserini', dest='anserini', default='/Volumes/Samsung_T5/anserini',
                    help='path to anserini')

parser.add_argument('--textrank', dest='textrank', default=True, action='store_true',
                    help='Apply TextRank')

parser.add_argument('--use-entities', dest='use_entities', default=False, action='store_true',
                    help='Use named entities as graph nodes')

parser.add_argument('--nr-terms', dest='nr_terms', default=100, type=int,
                    help='Number of tfidf terms to include in graph')

parser.add_argument('--term-tfidf', dest='term_tfidf', default=0.0, type=float,
                    help='Weight that should be assigned to tfidf score of terms (for node initialization)')

parser.add_argument('--term-position', dest='term_position', default=0.0, type=float,
                    help='Weight for term position in initial node weight')

parser.add_argument('--term-embedding', dest='term_embedding', default=0.0, type=float,
                    help='Weight for word embeddings in edge creation')

parser.add_argument('--text-distance', dest='text_distance', default=0.0, type=float,
                    help='Weight for text distance in edge creation')

parser.add_argument('--l', dest='node_edge_l', default=0.5, type=float,
                    help='Weight for importance nodes over edges')

parser.add_argument('--novelty', dest='novelty', default=0.5, type=float,
                    help='Weight for novelty in relevance score')

parser.add_argument('--diversify', dest='diversify', default=False, action='store_true',
                    help='Diversify the results according to entity types')

parser.add_argument('--d-core-k', dest='d_core_k', default = 0.5, type=float, help="Set d-core parameter k")

parser.add_argument('--d-core-l', dest='d_core_l', default = 0.5, type=float, help="Set d-core parameter l")

parser.add_argument('--direction', dest='direction', default = 'forward', help="Set edge direction between paragraphs")

args = parser.parse_args()
#utils.write_run_arguments_to_log(**vars(args))

if args.diversify and not args.use_entities:
    parser.error("--diversify requires --use-entities.")

if args.year is not None:
    if args.year == 20:
        args.index = 'lucene-index.core18.pos+docvectors+rawdocs_all_v3'
    args.db = f'entity_database_{args.year}.db'
    args.topics = f'topics.backgroundlinking{args.year}.txt'
    args.candidates = f'run.backgroundlinking{args.year}.bm25+rm3.topics.backgroundlinking{args.year}.txt'
    args.qrels = f'qrels.backgroundlinking{args.year}.txt'


print(f'\nIndex: resources/Index/{args.index}')
print(f'Topics were retrieved from resources/topics-and-qrels/{args.topics}')
print(f'Results are stored in resources/output/runs/{args.output}\n')
utils.create_new_file_for_sure(f'resources/output/{args.output}')

# '../database_utils/db/rel_entity_reader.db'
conn, cursor = db_utils.connect_db(f'resources/db/{args.db}')

# load word embeddings
if args.term_embedding > 0 and args.embedding != '':
    embeddings = utils.load_word_vectors(
        f'resources/embeddings/{args.embedding}')
    print('Embeddings sucessfully loaded!')
else:
    embeddings = {}

# Load index
index_utils = index.IndexReader(f'resources/Index/{args.index}')

# Configure graph options.
comparator = DCoreComparator()

# Build kwargs for graph initialization:
build_arguments = {'index_utils': index_utils,
                   'cursor': cursor,
                   'embeddings': embeddings,
                   'use_entities': args.use_entities,
                   'nr_terms': args.nr_terms,
                   'term_tfidf': args.term_tfidf,
                   'term_position': args.term_position,
                   'text_distance': args.text_distance,
                   'term_embedding': args.term_embedding,
                   'direction': args.direction}

# Calculate absolute k and l
d_core_k = round(args.d_core_k * args.nr_terms)
d_core_l = round(args.d_core_l * args.nr_terms)

# Read in topics via Pyserini.
topics = utils.read_topics_and_ids_from_file(
    f'resources/topics-and-qrels/{args.topics}')

for topic_num, topic in tqdm(topics):  # tqdm(topics.items()):
    query_num = str(topic_num)
    query_id = topic  # ['title']

    query_graph = Graph(query_id, f'query_article_{query_num}')
    query_graph.build(**build_arguments)
    query_graph.trim(d_core_k, d_core_l)       # Vary trim parameter here
    # recalculate node weights using TextRank
    if args.textrank:
        query_graph.rank()

    # Create new ranking.
    ranking = {}
    addition_types = {}

    # Loop over candidate documents and calculate similarity score.
    qid_docids = utils.read_docids_from_file(
        f'resources/candidates/{args.candidates}')
    for docid in qid_docids[query_num]:

        # Create graph object.
        fname = f'candidate_article_{query_num}_{docid}'
        candidate_graph = Graph(docid, fname)
        candidate_graph.set_graph_comparator(comparator)

        # Build (initialize) graph nodes and edges.
        candidate_graph.build(**build_arguments)
        candidate_graph.trim(d_core_k, d_core_l)
        # recalculate node weights using TextRank
        if args.textrank:
            candidate_graph.rank()
        relevance, diversity_type = candidate_graph.compare(
            query_graph, args.novelty, args.node_edge_l)
        ranking[docid] = relevance
        addition_types[docid] = diversity_type

    # Sort retrieved documents according to new similarity score.
    sorted_ranking = utils.normalize_dict({k: v for k, v in sorted(
        ranking.items(), key=lambda item: item[1], reverse=True)})

    # Diversify
    if args.diversify:
        nr_types = len(
            np.unique([item for sublist in addition_types.values() for item in sublist]))
        present_types = []
        to_delete_docids = []
        for key in sorted_ranking.keys():
            if len(present_types) == nr_types:
                break
            if len(addition_types[key]) > 1:
                new_types = utils.not_in_list_2(
                    addition_types[key], present_types)
                if len(new_types) > 0:
                    present_types.append([new_types[0]])
                else:
                    to_delete_docids.append(key)
            else:
                if addition_types[key] not in present_types:
                    present_types.append(addition_types[key])
                else:
                    to_delete_docids.append(key)
        for key in to_delete_docids[:85]:  # delete max 85 documents per topic.
            del sorted_ranking[key]

    # Store results in txt file.
    utils.write_to_results_file(
        sorted_ranking, query_num, args.run_tag, f'resources/output/{args.output}')

if args.year != 20:
    # Evaluate performance with trec_eval.
    os.system(
        r"D:\Desktop\Study\Information_Retrieval\anserini\tools\eval\trec_eval.9.0.4\trec_eval.exe -c -M1000 -m map -m ndcg_cut -m P.10 resources/topics-and-qrels/{} resources/output/{}".format(args.qrels, args.output))
