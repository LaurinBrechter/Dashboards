import pandas as pd
import plotly.express as px
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc


data = pd.read_excel("Dashboards\\Data\\supermarkt_sales.xlsx", sheet_name="Sales", usecols="B:R", skiprows=3)
dropdown_data = data["Branch"].unique()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("Sidebar", className="display-4"),
        html.Hr(),
        html.P(
            "Please select a branch", className="lead"
        ),
    
        dcc.Dropdown(id="select_branch",
                 options=[{"label": i, "value":i} for i in dropdown_data],
                 multi=False,
                 value = "A",
                 style={"width":"100%"}),

        html.Div(id="output_container", children=[]),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

app.layout = dbc.Container([

    # html.H1("Sales Dashboard with Python Dash", style={"text-align": "center"}),

    html.Div([
        dbc.Col(dbc.Col(dcc.Graph(id="sales_history", figure = {},
              style={"width":"100%"})))
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id="cust_type_pie", figure = {},
              style={"width":"100%"})),
        dbc.Col(dcc.Graph(id="sales_distribution", figure={},
              style={"width":"100%"}))
    ]),
 
    sidebar
])

# need to have a function under each callback, one input -> one argument for the function, the argument always refers to the component property/input.
@app.callback(
    [Output(component_id="output_container", component_property="children"),
     Output(component_id="sales_distribution", component_property="figure"),
     Output(component_id="sales_history", component_property="figure"),
     Output(component_id="cust_type_pie", component_property="figure")],
    [Input(component_id="select_branch", component_property="value")]
)
def update_graph(option_selected):
    print(option_selected)

    container = "The branch chosen was: {}".format(option_selected)
    
    data_sel = data.copy()
    data_sel = data_sel.loc[data_sel["Branch"] == option_selected]

    sales_dist = px.histogram(data_sel, x="gross income")

    data_agg = data_sel.groupby("Date").agg({"gross income":"sum"})
    sales_hist = px.line(data_agg, x=data_agg.index, y="gross income")

    cust_type_pie = px.pie(data_sel, values="gross income", names="Product line")

    # have to mind the order in which things are returned.
    # the things returned here are going into the output.
    return container, sales_dist, sales_hist, cust_type_pie


if __name__ == "__main__":
    app.run_server(debug=True)