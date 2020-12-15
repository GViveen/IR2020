import numpy as np
from scipy import stats
from collections import defaultdict
import operator
import warnings

from general_utils import utils
from graph.graph_comparators.InformalGraphComparatorInterface import InformalGraphComparatorInterface


class DCoreComparator(InformalGraphComparatorInterface):
    def type_distribution(self, nodes):
        distribution = defaultdict(float)
        for node in nodes.values():
            distribution[node.node_type] += 1
        return distribution

    def similarity(self, nodes_a, edges_a, nodes_b, edges_b, common_nodes, common_edges, node_edge_l) -> float:
        l = node_edge_l  # node over edge importance
        sum_nodes_a = sum([node.weight for node in nodes_a.values()])
        sum_nodes_b = sum([node.weight for node in nodes_b.values()])

        sum_edges_a = sum([weight for weight in edges_a.values()])
        sum_edges_b = sum([weight for weight in edges_b.values()])

        nodes = l * (sum(common_nodes.values(), 0)) / max(sum_nodes_a, sum_nodes_b, 1)
        edges = (1 - l) * sum(common_edges.values(), 0) / max(sum_edges_a, sum_edges_b, 1)

        return nodes + edges

    def novelty(self, que_graph, can_graph, common_nodes) -> float:
        # determine weight threshold! to be important node
        # for edge in candidate graph sum all weights
        # sum indegrees of novel nodes
        new_info = {}

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            weight_threshold = np.mean(list(can_graph.edges.values()))

        i = 0
        added_nodes = []
        for edge, weight in can_graph.edges.items():
            # overlap should be 1, meaning there is exactly 1 node in common nodes.
            if len(set(edge) & set(common_nodes)) == 1 and weight > weight_threshold:
                new_node = np.setdiff1d(edge, common_nodes)[0]
                if new_node not in added_nodes:
                    i += 1
                    new_info[new_node] = can_graph.nodes[new_node]
                    added_nodes.append(new_node)

        additional_distributions = self.type_distribution(new_info)

        not_matching_candidate_node_weights = [can_graph.nodes[key].weight for key in
                                               set(can_graph.nodes) - set(common_nodes)]
        if len(not_matching_candidate_node_weights) == 0:
            return 0.0, utils.get_keys_max_values(additional_distributions)

        total_weight = sum(list(can_graph.edges.values()))
        total_indegree = sum([can_graph.indegree(can_graph.nodes[node]) for node in added_nodes])
        novelty = total_indegree / total_weight
        return novelty, utils.get_keys_max_values(additional_distributions)

    def compare(self, graph_a, graph_b, novelty_percentage, node_edge_l=0.5, similarity_weight=0.1) -> (float, float):
        """ Compare graph A with graph B and calculate similarity score.

        Returns
        -------
        (float, float)
            node similarity, edge similarity
        """
        nodes_a = graph_a.nodes
        edges_a = graph_a.edges
        nodes_b = graph_b.nodes
        edges_b = graph_b.edges

        common_nodes = {node_name: node_obj.weight for node_name, node_obj in nodes_a.items() if
                        node_name in nodes_b.keys()}
        common_edges = {edge: weight for edge, weight in edges_a.items() if edge in edges_b.keys()}

        similarity_score = self.similarity(nodes_a, edges_a, nodes_b, edges_b, common_nodes,
                                                                      common_edges, node_edge_l)

        novelty_score, diversity_type = self.novelty(graph_b, graph_a, common_nodes)
        novelty_score = float(novelty_percentage * novelty_score)
        # print("result of comparison", similarity_weight * similarity_score + novelty_weight * novelty_score)
        return similarity_weight * similarity_score + novelty_score, diversity_type
