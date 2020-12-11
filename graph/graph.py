import sys
from collections import defaultdict
import numpy as np
from bglinking.general_utils import utils

from bglinking.graph.graph_builders.DefaultGraphBuilder import DefaultGraphBuilder
from bglinking.graph.graph_builders.DirectedBuilder import DirectedBuilder
from bglinking.graph.graph_rankers.DefaultGraphRanker import DefaultGraphRanker
from bglinking.graph.graph_rankers.DirectedGraphRanker import DirectedGraphRanker
from bglinking.graph.graph_comparators.GMCSComparator import GMCSComparator
from bglinking.graph.graph_comparators.DCoreComparator import DCoreComparator
# [modified] MIT license bramblu


class Graph:
    """Graph that represents a single news article."""

    def __init__(self, docid, fname):
        self.__nodes = {}  # {name: NodeObj1, name: NodeObj2, ...]
        self.__edges = defaultdict(float)  # {(A, B): weight}

        self.graph_builder = DirectedBuilder()
        self.graph_ranker = DirectedGraphRanker()
        self.graph_comparator = DCoreComparator()

        self.docid = docid
        self.fname = fname

    def build(self, **kwargs):
        # Append local docid to kwargs.
        kwargs['docid'] = self.docid
        self.graph_builder.build(self, **kwargs)

    def trim(self, k, l):
        self.graph_builder.trim(self, k, l)

    def rank(self):
        self.graph_ranker.rank(self.__nodes, self.__edges)

    def compare(self, graph, novelty_percentage, node_edge_l):
        return self.graph_comparator.compare(self, graph, novelty_percentage, node_edge_l)

    @property
    # @utils.limit_set
    def edges(self):
        return self.__edges

    @property
    # @utils.limit_set
    def nodes(self):
        return self.__nodes

    @staticmethod
    def same_paragraph(node, other_node):
        """Return true if other node is in same paragraph"""
        return any(np.intersect1d(np.array(node.locations), np.array(other_node.locations)))

    @staticmethod
    def subsequent_paragraph(node, other_node):
        """Return true if other node is in subsequent paragraph"""
        return any([any(i > np.array(node.locations)) for i in other_node.locations])

    def outdegree(self, node):
        """Return the number of edges where ending edge == node"""
        return len([n for n in self.__edges if n[0] == node.name])

    def indegree(self, node):
        """Return the number of edges where ending edge == node"""
        return len([n for n in self.__edges if n[1] == node.name])

    def get_degree(self, node):
        """Get indegree, outdegree tuple of node"""
        return self.indegree(node), self.outdegree(node)

    def add_node(self, node):
        """add node to nodes"""
        self.__nodes[node.name] = node

    def remove_node(self, node):
        """Remove a node from the graph"""
        for edge_key in list(self.edges.keys()):
            if node.name in edge_key:
                del self.edges[edge_key]
        del self.nodes[node.name]

    def add_edge(self, start, end, weight):
        """Add edge between node"""
        # Store edge with nodes in alphabetical order.
        if start[0] < end[0]:
            self.__edges[(start, end)] = weight
        else:
            self.__edges[(end, start)] = weight

    def set_graph_builder(self, graph_builder):
        self.graph_builder = graph_builder

    def set_graph_ranker(self, graph_ranker):
        self.graph_ranker = graph_ranker

    def set_graph_comparator(self, graph_comparator):
        self.graph_comparator = graph_comparator

    def has_edge(self, edge) -> bool:
        return edge in self.edges.keys()

    def has_node(self, node) -> bool:
        return node in self.nodes.keys()

    def nr_nodes(self) -> int:
        return len(list(self.nodes.keys()))
