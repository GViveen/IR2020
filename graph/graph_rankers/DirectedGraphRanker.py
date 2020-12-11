import numpy as np
from collections import defaultdict

from general_utils import utils
from graph.graph_rankers.InformalGraphRankerInterface import InformalGraphRankerInterface

# Modified from https://github.com/BrambleXu/news-graph

class DirectedGraphRanker(InformalGraphRankerInterface):
    score_dict = {}
    step_dict = {}
    def rank(self, nodes, edges) -> dict:   
        d = 0.85 # damping coefficient, usually is .85
        min_diff = 1e-5 # convergence threshold
        steps = 1000 # iteration steps
        weight_default = 1.0 / (len(nodes.keys()) or 1.0)

        self.score_dict = {k: 0 for k in list(nodes)}
        nodeweight_dict = defaultdict(float) # store weight of node
        sum_node_dict = defaultdict(float) # store weight of out nodes
        step_list = []

        for step in range(steps):
            for node in list(nodes):
                self.score(node, edges, step, steps)
                step_list.append(sum(nodeweight_dict.values()))
                if abs(step_list[step] - step_list[step - 1]) <= min_diff:
                    break

        # Normalize and Standardization
        if len(list(nodeweight_dict.values()))>0:
            nodeweight_dict = utils.standardize_dict(nodeweight_dict)
            nodeweight_dict = utils.normalize_dict(nodeweight_dict)

            assert np.min(list(nodeweight_dict.values()))>=0, nodeweight_dict
            
        for node in nodes.values():
            node.weight = nodeweight_dict[node.name]

        #return nodeweight_dict

    def score(self, node, edges, step, steps):
        if self.score_dict[node] == 0 and step < steps:
            step += 1
            nodes_in = self.indegree_nodes(node, edges)
            self.score_dict[node] = sum([1 / len(self.outdegree_nodes(node_in, edges)) * self.score(node_in, edges, step, steps) for node_in in list(nodes_in)])
        elif step >= steps:
            return self.score_dict[node]


    def outdegree(self, node, edges):
        """Return the number of edges where start == node"""
        return len([n for n in edges if n[0] == node])

    def outdegree_nodes(self, node, edges):
        """Return the number of edges where start == node"""
        return [n for n in edges if n[0] == node]

    def indegree(self, node, edges):
        """Return the number of edges where end == node"""
        return len([n for n in edges if n[1] == node])

    def indegree_nodes(self, node, edges):
        """Return the number of edges where end == node"""
        return [n for n in edges if n[1] == node]