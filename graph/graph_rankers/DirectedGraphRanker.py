import numpy as np
from collections import defaultdict

from general_utils import utils
from graph.graph_rankers.InformalGraphRankerInterface import InformalGraphRankerInterface
from tqdm import tqdm
# Modified from https://github.com/BrambleXu/news-graph

class DirectedGraphRanker(InformalGraphRankerInterface):
    score_dict = {}
    step_dict = {}
    def rank(self, nodes, edges) -> dict:   
        d = 0.85  # damping coefficient, usually is .85
        min_diff = 1e-2  # convergence threshold
        steps = 1000  # iteration steps
        self.weight_default = 1.0 / (len(nodes.keys()) or 1.0)
        self.score_dict = {k: self.weight_default for k in list(nodes)}
        self.indegree_dict = {k: self.indegree_nodes(k, edges) for k in list(nodes)}
        self.outdegree_dict = {k: len(self.outdegree_nodes(k, edges)) for k in list(nodes)}
        nodeweight_dict = defaultdict(float)   # store weight of node
        step_tuple = (1000, 0)

        for step in range(steps):
            for node in list(nodes):
                self.score(node, d)
            new_tuple = (step_tuple[1], sum(self.score_dict.values()))
            step_tuple = new_tuple
            if abs(step_tuple[1] - step_tuple[0]) <= min_diff:
                break
       # Normalize and Standardization
        if len(self.score_dict.values())>0:
            self.score_dict = utils.standardize_dict(self.score_dict)
            self.score_dict = utils.normalize_dict(self.score_dict)

            assert np.min(list(self.score_dict.values())) >= 0
            
        for node in nodes.values():
            node.weight = self.score_dict[node.name]
        #return nodeweight_dict

    def score(self, node, d):
        nodes_in = self.indegree_dict[node]
        if nodes_in:
            self.score_dict[node] = 1 - d + d * sum([1 / self.outdegree_dict[node_in] * self.score_dict[node_in] for node_in in nodes_in])

    def outdegree(self, node, edges):
        """Return the number of edges where start == node"""
        return len([n for n in edges if n[0] == node])

    def outdegree_nodes(self, node, edges):
        """Return the number of edges where start == node"""
        return [n[1] for n in edges if n[0] == node]

    def indegree(self, node, edges):
        """Return the number of edges where end == node"""
        return len([n for n in edges if n[1] == node])

    def indegree_nodes(self, node, edges):
        """Return the number of edges where end == node"""
        return [n[0] for n in edges if n[1] == node]