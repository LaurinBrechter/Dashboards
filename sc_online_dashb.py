import streamlit as st
import numpy as np
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt


class SupplyChain():
    def __init__(self, n_tiers, avg_n_sups):
        self.graph = nx.Graph()
        self.graph.add_node(0, tier="TIER0")
        self.n_tiers = n_tiers
        
        self.tier_names = ["TIER"+str(i) for i in range(self.n_tiers)]
        
        # create the supply side
        comp_id = 1
        for i, tier_name in enumerate(self.tier_names[:-1]):
            
            # search for companies in that tier
            nodes_in_tier = [node for node in self.graph.nodes(data=True) if node[1]["tier"] == tier_name]
            
            # for every company in the tier create suppliers.
            for node in nodes_in_tier:
                n_sups = np.random.poisson(avg_n_sups)
                
                self.graph.add_nodes_from(range(comp_id, n_sups+comp_id), tier="TIER" + str(i+1))
                    
                to_add = [(node[0], j) for j in range(comp_id, n_sups+comp_id)]
        
                self.graph.add_edges_from(to_add)
                
                comp_id += n_sups

    
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

@st.cache(persist=True, allow_output_mutation=True) 
def create_sc_time_series(n_tiers, poisson_exp):
    sc = SupplyChain(n_tiers, poisson_exp)

    dt = pd.date_range(start='1/1/2020', end='1/08/2022')
    time = np.arange(len(dt), dtype="float32")
    baseline = 10
    series = trend(time, 0.1)  
    baseline = 100
    amplitude = 40
    slope = 0.20
    noise_level = 20

    # Create the series
    series = baseline + trend(time, slope) + seasonality(time, period=183, amplitude=amplitude)
    # Update with noise
    series += noise(time, noise_level, seed=42)
    
    layout = nx.spring_layout(sc.graph)
    
    return sc, dt, series, layout

sc, dt, series, layout = create_sc_time_series(4,3)

tiers = nx.get_node_attributes(sc.graph, "tier")
df_tier = pd.DataFrame(tiers.values(), index=tiers.keys())
tier_num = pd.factorize(df_tier[0])[0]

company_selected = st.sidebar.selectbox("Please select a Company in the Network", list(range(len(sc.graph.nodes))))

# tier_selected = st.sidebar.selectbox("Please select a Tier of the Network", sc.tier_names)
tier_selected = st.sidebar.multiselect("Please select one or more Tiers of the Network", sc.tier_names, default=sc.tier_names)

st.write(tier_selected)

opacity_list = np.where(np.isin(df_tier[0], tier_selected), 1, 0.5)

st.write(np.isin(tiers, tier_selected))

edge_x = []
edge_y = []

for edge in sc.graph.edges():
    x0, y0 = layout[edge[0]]
    x1, y1 = layout[edge[1]]
    
    edge_x.append(x0)
    edge_x.append(x1)
    edge_x.append(None)
    edge_y.append(y0)
    edge_y.append(y1)
    edge_y.append(None)
    
edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=0.5, color='#25488e'),
    hoverinfo='none',
    mode='lines')


node_x = []
node_y = []
for node in sc.graph.nodes():
    x, y = layout[node]
    node_x.append(x)
    node_y.append(y)
    
node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers',
    hoverinfo='text'
    )


node_trace.marker.colorscale = 'earth'    
node_trace.marker.color = tier_num
node_trace.marker.opacity = opacity_list

degrees = dict(sc.graph.degree)
node_trace.text = [str(i) + " Number of Links: " + str(degrees[i]) for i in degrees]
    # marker=dict(
    #         showscale=True,
    #         colorscale='YlGnBu',
    #         reversescale=True,
    #         size=10,
    #         colorbar=dict(
    #             thickness=15,
    #             title='Node Connections',
    #             xanchor='left',
    #             titleside='right'
    #         ),
    #         line_width=2))
    


graph_fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title='<br>Supply Chain',
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
st.write(graph_fig)


demand = pd.DataFrame(series, index=dt, columns=["Demand"])
demand_fig = px.line(x=demand.index, y=demand["Demand"], title="Customer Demand")
demand_fig.update_layout(
    xaxis_title = "Date",
    yaxis_title ="Demand"
)

st.write(demand_fig)