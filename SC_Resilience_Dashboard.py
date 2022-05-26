import dash
import dash_cytoscape as cyto  
from dash import dcc, html
from dash.dependencies import Output, Input, State
import pandas as pd  
import networkx as nx
import numpy as np
from sc_time_series_creator import SupplyChain
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

g = SupplyChain(n_tiers=5, avg_n_sups=2, avg_decay=0.3, lbound_add_edges=0, ubound_add_edges=1).graph

positions = nx.spring_layout(g)

print(g.nodes(data=True))

node_data = [{"data": {"id": str(i), "label": str(i)}, 
              "position": {"x": positions[i][0]*1000, "y": positions[i][1]*1000}, 
              "locked":False,
              'classes': 'red',
              "style": {"shape": "circle",
                        'width': 30,
                        'height': 30,
                        "color": "white",
                        }
              } 
              for i in list(g.nodes())]

edge_df = pd.DataFrame([{"from":i[0], "to":i[1], "production":i[2]["production"]} for i in g.edges(data=True)])

edge_data = [{'data': {'source': str(i[0]), 'target': str(i[1])},
              "style": {'line-color': '#9e9e26', # 
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
    margin={"b": 10, "l":10, "r": 10, "t":10},
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

GRAPH_STYLE_SHEET = [
    # Group selectors
    {
        'selector': 'node',
        'style': {
            'content': 'data(label)'
        }
    },

    # Class selectors
    {
        'selector': '.red',
        'style': {
            'background-color': '#990000',
            'line-color': '#990000'
        }
    },
    # {
    #     'selector': '.triangle',
    #     'style': {
    #         'shape': 'triangle'
    #     }
    # },
    {
        "selector": "edge",
        "style": {
            "target-arrow-color": "#C5D3E2", #Arrow color
            "target-arrow-shape": "triangle", #Arrow shape
            "line-color": "#C5D3E2", #edge color
            'arrow-scale': 2, #Arrow size
            'curve-style': 'bezier' #Default curve-If it is style, the arrow will not be displayed, so specify it
        }
    }
]

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
                    stylesheet=GRAPH_STYLE_SHEET,
                    elements=[
        
                        *node_data, *edge_data
                
                    ]
                    
                )], width=6, style={"padding": "0rem 0rem"}),
            dbc.Col([
                html.Div([

                    html.H1("Node", style=HEADER_STYLE),
                    
                    html.Hr(),
                    html.Br(),
                    
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    html.Div([
                                        html.Div(id="network-info", children=["The following indicators help monitor the state of the network. They were split amongst 5 different dimensions"]),
                                    ])
                                ], 
                                title="about indicators"
                            ),

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
                                    html.P("Network Diameter: ")# {}".format(nx.diameter(g)))
                                ], 
                                title="Depth"
                            ),

                            dbc.AccordionItem(
                                [
                                    html.Div(id="node-info"),
                                ], 
                                title="Substitutability"
                            ),

                            dbc.AccordionItem(
                                [
                                    dcc.Graph(id="supplier-incoming"),
                                    dcc.Graph(id="supplier-outgoing"),
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
                )], width=3, style={"margin-right": "0", "padding": "0rem 0rem"}),

                
        ]),

        dbc.Row([
            dcc.Dropdown(
                id='dropdown-update-layout',
                value='spring',
                clearable=False,
                options=[
                    {'label': name, 'value': name} for name in ['planar', 'random', 'spectral', 'spring', 'shell']
                ])
     ]) 
    ]
)

print(g.nodes())


@app.callback(
    Output('node-info','children'),
    Output('tier-distribution-pie','figure'),
    Output("supplier-incoming", "figure"),
    Output("supplier-outgoing", "figure"),
    Input('org-chart','tapNodeData'),
)
def update_data(data):
    """
    tapNode: give back information about node being tapped by user
    mouseoverNodeData : data dict of edge that was most recently hovered over by user
    https://dash.plotly.com/cytoscape/reference
    """

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
        node = 0

    pie_fig = go.Figure(data=[go.Pie(
                        values=grah_data.values[::-1], 
                        labels=grah_data.index[::-1], 
                        hole=.4,
                        pull = pull
                    )], 
                layout=GRAPH_STYLE)

    inc = edge_df.loc[edge_df["from"] == node]
    inc["prod_norm"] = inc["production"]/sum(inc["production"])

    out = edge_df.loc[edge_df["to"] == node]
    out["prod_norm"] = out["production"]/sum(out["production"])
    # dist_fig = px.pie(names="from", values="production", data_frame=inc)

    if True:
        in_fig = go.Figure(data=[go.Bar(
                            y=inc["to"],
                            x=inc["prod_norm"],
                            orientation="h"
                        )], 
                    layout=GRAPH_STYLE)

        in_fig.update_layout({"height": 200})

        print(out["prod_norm"])

    if len(out) > 0:
        out_fig = go.Figure(data=[go.Bar(
                            x=out["prod_norm"],
                            y=[str(i) for i in out["from"]],
                            orientation="h"
                            # hole=.4
                        )], 
                    layout=GRAPH_STYLE)

        out_fig.update_layout({"height": 200})
    else:
        out_fig = {}

    return return_data, pie_fig, in_fig, out_fig 


@app.callback(Output('org-chart', 'elements'),
              Input('dropdown-update-layout', 'value'))
def update_layout(layout):

    print(layout)

    positions = getattr(nx, layout + "_layout")(g)

    node_data = [{"data": {"id": str(i), "label": str(i)}, 
          "position": {"x": positions[i][0]*1000, "y": positions[i][1]*1000}, 
          "locked":False,
          'classes': 'red',
          "style": {"shape": "circle",
                    'width': 30,
                    'height': 30,
                    "color": "white",
                    }
          } 
          for i in list(g.nodes())]


    return [

        *node_data,
        *edge_data
        
    ]


if __name__ == "__main__":
    app.run_server(debug=True)