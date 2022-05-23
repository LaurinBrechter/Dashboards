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


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

g = SupplyChain(5,3).graph
positions = nx.spring_layout(g)
node_data = [{"data": {"id": str(i), "label": str(i)}, 
              "position": {"x": positions[i][0]*1000, "y": positions[i][1]*1000}, 
              "locked":True,
              "style": {"shape": "rectangle"}} 
              for i in list(g.nodes())]

edge_data = [{'data': {'source': str(i[0]), 'target': str(i[1])}} 
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


app.layout = html.Div(
    [
        dbc.Row([

            

            dbc.Col([

                html.Br(),

                html.H1("Supply Chain Graph", style=HEADER_STYLE),

                html.Hr(),

                cyto.Cytoscape(
                    id='org-chart',
                    layout={'name': 'preset'},
                    style={'width': '100%', 'height': '700px'},
                    elements=[
        
                        *node_data, *edge_data
                
                    ]
                    # stylesheet=[
                    #     {
                    #         'selector': 'node',
                    #         'style': {
                    #             'label': 'data(firstname)'
                    #         }
                    #     },
                    #     {
                    #         'selector': '[firstname !*= "ert"]',
                    #         'style': {
                    #             'background-color': '#FF4136',
                    #             'shape': 'rectangle'
                    #         }
                    #     }
                    # ]

                )], width=9),

            dbc.Col([
                
                html.Br(),

                html.Div([

                    
                    html.H1("Node Info", style=HEADER_STYLE),
                    html.Hr(),

                    html.Div(id="node-info"),

                    html.H1("Network Info", style=HEADER_STYLE),
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
                
                )], width=3, style={"background-color": "#303030"}),
        ])
    ]
)


@app.callback(
    Output('node-info','children'),
    Input('org-chart','tapNodeData'),
)
def update_nodes(data):
    print(data)
    return ["Hello"]


if __name__ == "__main__":
    app.run_server(debug=True)