import networkx as nx
import numpy as np
from random import randint

class SupplyChain():
    def __init__(self, n_tiers, avg_n_sups, avg_decay=0, ubound_add_edges = 0, lbound_add_edges = 0):
        self.graph = nx.Graph()
        self.graph.add_node(0, tier="TIER0")
        self.n_tiers = n_tiers
        
        self.tier_names = ["TIER"+str(i) for i in range(self.n_tiers)]
        
        # create the supply side
        a = lbound_add_edges
        b = ubound_add_edges

        comp_id = 1
        for i, tier_name in enumerate(self.tier_names[:-1]):
            avg_n_sups -= avg_decay
            # search for companies in that tier
            nodes_in_tier = [node for node in self.graph.nodes(data=True) if node[1]["tier"] == tier_name]
            
            # for every company in the tier create suppliers.
            for node in nodes_in_tier:
                n_sups = np.random.poisson(avg_n_sups)
                

                self.graph.add_nodes_from(range(comp_id, n_sups+comp_id), tier="TIER" + str(i+1))
                
                to_add = [(node[0], j, {"inf_sharing":np.random.random()}) for j in range(comp_id, n_sups+comp_id)]
        
                self.graph.add_edges_from(to_add)
                
                comp_id += n_sups
            
            # add additional cross edges.
            if b > 0:
                for node in nodes_in_tier:
                    # extra_conns = np.random.randint(a,b)
                    extra_conns = randint(a,b)
                    extra_nodes = np.random.choice(list(set(list(self.graph.nodes())) - set([node[0]])), extra_conns)

                    self.graph.add_edges_from([(node[0], j) for j in extra_nodes])
                    comp_id += extra_conns

        # also add edges for the last layer
        if b > 0:
            last_tier_nodes = [node for node in self.graph.nodes(data=True) if node[1]["tier"] == tier_name]
            # last_tier_nodes = list(filter(lambda x: x[1]["tier"] == sc.tier_names[-1], list(sc.graph.nodes(data=True))))
            for node in last_tier_nodes:
                # extra_conns = np.random.randint(a,b)
                extra_conns = randint(a,b)
                extra_nodes = np.random.choice(list(set(list(self.graph.nodes())) - set([node[0]])), extra_conns)
                self.graph.add_edges_from([(node[0], j) for j in extra_nodes])
                comp_id += extra_conns
            
        # self.graph.remove_edges_from(nx.selfloop_edges(self.graph))

def trend(time, slope=0):
    return slope * time

def seasonal_pattern(season_time):
    """An arbitrary pattern that repeats every season"""
    return np.where(season_time < 0.3,
                    np.cos(season_time * 2 * np.pi),
                    1 / np.exp(3 * season_time) + np.sin(season_time*2*np.pi))

def seasonality(time, period, amplitude=1, phase=0):
    """Repeats the same pattern at each period"""
    season_time = ((time + phase) % period) / period
    return amplitude * seasonal_pattern(season_time)

def noise(time, noise_level=1, seed=None):
    rnd = np.random.RandomState(seed)
    return rnd.randn(len(time)) * noise_level