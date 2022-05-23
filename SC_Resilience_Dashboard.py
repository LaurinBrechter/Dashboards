import dash
import dash_cytoscape as cyto  
from dash import dcc, html
from dash.dependencies import Output, Input
import pandas as pd  
import plotly.express as px
import networkx as nx
import numpy as np
from sc_time_series_creator import SupplyChain, trend, trend, seasonal_pattern, seasonality, noise
import dash_bootstrap_components as dbc
import plotly.graph_objects as go


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

g = SupplyChain(5,3).graph
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
    # "background-color": "#f8f9fa"
}

HEADER_STYLE = {
    "color": "#adafae",
    "textAlign": "center"
}

GRAPH_STYLE = go.Layout(title="First Graph", 
              margin={"b": 0, "l":10, "r": 10, "t":20},
              font={"color": "#adafae"},
              paper_bgcolor="#0B243B",
              plot_bgcolor="#0B243B"
    )
    

fig1 = go.Figure(data=go.Scatter(y=[1,2,3,4]), 
                layout=GRAPH_STYLE
)

fig2 = go.Figure(data=go.Scatter(y=[1,2,3,4]), 
                layout=GRAPH_STYLE
)


app.layout = html.Div(
    [
        html.Div(html.Br()),

        dbc.Row([

            dbc.Col([
                html.H1("Network", style=HEADER_STYLE),
                dcc.Graph(figure=fig1),
                dcc.Graph(figure=fig2)

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
                                    html.P("This is the content of the first section")
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
    Input('org-chart','tapNodeData'),
)
def update_nodes(data):
    print(data)
    if data:
        node = int(data["id"])
        return ["Node Degree: {}".format(nx.degree(g)[node]), 
                html.P("This is nice"),
                ]
    else:
        return [html.Div("Select a Node to see Degree")]


if __name__ == "__main__":
    app.run_server(debug=True)