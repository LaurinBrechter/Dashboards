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
    noise_level = 11

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
tier_selected = st.sidebar.multiselect("Please select one or more Tiers of the Network", sc.tier_names, default=sc.tier_names)


opacity_list = np.where(np.isin(df_tier[0], tier_selected), 1, 0.3)

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
    line=dict(width=0.5, color='#ffffcc'),
    hoverinfo='none',
    mode='lines',
    )


node_x = []
node_y = []
for node in sc.graph.nodes():
    x, y = layout[node]
    node_x.append(x)
    node_y.append(y)
    
degrees = dict(sc.graph.degree)

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers',
    hoverinfo='text',
    marker = dict(
        size = 10,
        opacity = opacity_list,
        color = tier_num,
        colorscale = "earth"),
    text = [str(i) + " Number of Links: " + str(degrees[i]) for i in degrees]
    )

    #         colorbar=dict(
    #             thickness=15,
    #             title='Node Connections',
    #             xanchor='left',
    #             titleside='right'
    #         ),
    #         line_width=2))
    
st.markdown("### Supply Chain Network Graph")


graph_fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )

def ttr_curve():
    service_level = np.array([0.93] * len(dt))
    service_level -= np.random.normal(0, 0.03, size=len(service_level))
    service_level = np.where(service_level >= 1, 0.97, service_level)
    df = pd.DataFrame(service_level,index=dt, columns=["service level"])

    th = 0.93
    fig = go.Figure()

    line_trace = go.Scatter(x=df.index, y=df["service level"], 
                             mode="lines", name="service level")
    point_trace = go.Scatter(x=df.index,  y=df["service level"].where(df["service level"] <= th), 
                             mode="lines", name="below for >= 2 days")

    fig = go.Figure(data=[line_trace, point_trace])

    fig.add_hline(y=0.93, line_dash="dash", line_color="red", annotation_text="93% service level")
    fig.update_layout(yaxis_range=[0,1],
                      title="Service Level of company X",
                      xaxis_title="Date",
                      yaxis_title="Service Level (%order fullfilled on time)")
    
    return fig

ttr_fig = ttr_curve()

st.write(ttr_fig)

st.write(graph_fig)

st.markdown("### Customer Demand")

demand = pd.DataFrame(series, index=dt, columns=["Demand"])
demand_fig = px.line(x=demand.index, y=demand["Demand"])
demand_fig.update_layout(
    xaxis_title = "Date",
    yaxis_title ="Demand"
)

st.write(demand_fig)