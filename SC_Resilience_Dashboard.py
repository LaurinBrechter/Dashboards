import dash
import dash_cytoscape as cyto  
from dash import dcc, html
from dash.dependencies import Output, Input
import pandas as pd  
import plotly.express as px
import networkx as nx
import numpy as np
from sc_time_series_creator import SupplyChain, trend, seasonal_pattern, seasonality, noise
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

g = SupplyChain(n_tiers=5, avg_n_sups=4, avg_decay=0.5, lbound_add_edges=1, ubound_add_edges=2).graph

positions = nx.spring_layout(g)

node_data = [{"data": {"id": str(i), "label": str(i)}, 
              "position": {"x": positions[i][0]*1000, "y": positions[i][1]*1000}, 
              "locked":True,
              'classes': 'red',
              "style": {"shape": "circle",
                        'width': 30,
                        'height': 30,
                        "color": "white",
                        }
              } 
              for i in list(g.nodes())]

edge_data = [{'data': {'source': str(i[0]), 'target': str(i[1])},
              "style": {'line-color': '#f2f20d', 
                        'width': 2}} 
              for i in g.edges()]

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

SIDEBAR_STYLE = {
    "textAlign":"left"
}

HEADER_STYLE = {
    "color": "#adafae",
    "textAlign": "center"
}

GRAPH_STYLE = go.Layout( 
    margin={"b": 0, "l":10, "r": 10, "t":20},
    font={"color": "#adafae"},
    paper_bgcolor="#0B243B",
    plot_bgcolor="#0B243B",
    height=400
    )
    
SPARKLINE_STYLE = go.Layout(
    paper_bgcolor="#060606", # #060606
    plot_bgcolor="#060606", # #060606
    margin={"b": 0, "l":0, "r": 0, "t":0},
    height=100,
    yaxis={"visible":False},
    xaxis={"visible":False}
)

# color_discrete_map={'Thur':'lightcyan',
#                                  'Fri':'cyan',
#                                  'Sat':'royalblue',
#                                  'Sun':'darkblue'})

fig1 = go.Figure(
    data=go.Scatter(y=[1,2,3,4]), 
    layout=GRAPH_STYLE
)

grah_data = pd.DataFrame([[i[0], i[1]["tier"]] for i in list(g.nodes(data=True))])[1].value_counts(normalize=True)

# create a random spark line with a random walk ending at the average clustering of the network.
avg_clust = nx.average_clustering(g)
spark_data = [avg_clust]
for i in range(10):
    spark_data.append(spark_data[-1] + np.random.normal(loc=0, scale=avg_clust/8))

spark_intercon = go.Figure(
    data=go.Scatter(y=spark_data[::-1]),
    layout=SPARKLINE_STYLE
)


app.layout = html.Div(
    [
        html.Div(html.Br()),

        dbc.Row([

            dbc.Col([
                html.H1("Network", style=HEADER_STYLE),
                dcc.Graph(figure=fig1),
                dcc.Graph(id="tier-distribution-pie")

            ], width=3),

            dbc.Col([
                
                dbc.Row([
                    html.Div(),
                    html.H1("Supply Chain Monitoring", style=HEADER_STYLE),
                    
                ]),
                
                cyto.Cytoscape(
                    id='org-chart',
                    layout={'name': 'preset'},
                    style={'width': '100%', 'height': '700px', "background-color":"#0B243B"},
                    elements=[
        
                        *node_data, *edge_data
                
                    ]
                    
                )], width=6),

            dbc.Col([
                
                html.Div([

                    html.H1("Node", style=HEADER_STYLE),
                    
                    html.Div(id="node-info"),

                    
                    html.Hr(),

                    html.Div(id="network-info", children=["The following indicators help monitor the state of the network. They were split amongst 5 different dimensions"]),

                    html.Br(),
                    
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    html.Div([
                                        html.P("Network Clustering Coefficient: {}".format(np.round(nx.average_clustering(g), 3))), 
                                        dcc.Graph(figure=spark_intercon)
                                    ])
                                    
                                ], 
                                title="Interconnectivity"
                            ),

                            dbc.AccordionItem(
                                [
                                    html.P("Network Diameter: {}".format(nx.diameter(g)))
                                ], 
                                title="Depth"
                            ),

                            dbc.AccordionItem(
                                [
                                    html.P("This is the content of the first section")
                                ], 
                                title="Substitutability"
                            ),

                            dbc.AccordionItem(
                                [
                                    html.P("This is the content of the first section")
                                ], 
                                title="Concentraction"
                            ),

                            dbc.AccordionItem(
                                [
                                    html.P("This is the content of the first section")
                                ], 
                                title="Visibility"
                            )
                        ]
                    )
                    ], style=SIDEBAR_STYLE
                )], width=3)
        ])
    ]
)


@app.callback(
    Output('node-info','children'),
    Output('tier-distribution-pie','figure'),
    Input('org-chart','tapNodeData'),
)
def update_nodes(data):
    print(data)

    pull = [0] * len(grah_data)
    
    if data:
        node = int(data["id"])
        tier = g.nodes(data=True)[node]["tier"]
        pull[int(tier[-1])] = 0.3

        # pull out a piece of the pie of the node belonging to that tier is selected.
        
        return_data = ["Node Degree: {}".format(nx.degree(g)[node]), 
                html.P("Node Clustering {}".format(nx.clustering(g, node))),
                html.P("Node Tier: {}".format(g.nodes(data=True)[node]["tier"]))
        ]
    else:
        return_data = [html.Div("Select a Node to see Degree")]

    pie_fig = go.Figure(data=[go.Pie(
                        values=grah_data.values[::-1], 
                        labels=grah_data.index[::-1], 
                        hole=.4,
                        pull = pull
                    )], 
                layout=GRAPH_STYLE)

    return return_data, pie_fig

if __name__ == "__main__":
    app.run_server(debug=True)