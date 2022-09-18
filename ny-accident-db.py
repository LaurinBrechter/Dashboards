from plotly.subplots import make_subplots
import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import pandas as pd  
import numpy as np
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], assets_folder="assets\\assets_accident_db")

df = pd.read_csv(
            "Data\\Motor_Vehicle_Collisions_-_Crashes.csv", 
            usecols=["LATITUDE", "LONGITUDE", "CRASH DATE", "CRASH TIME", "BOROUGH", "NUMBER OF PERSONS INJURED", "NUMBER OF PERSONS KILLED"], 
            nrows=500_000
        )


df = df.dropna(subset=["LATITUDE", "LONGITUDE", "NUMBER OF PERSONS INJURED", "NUMBER OF PERSONS KILLED"])
df = df.loc[(df["LATITUDE"] != 0) & (df["LONGITUDE"]) != 0]
df["CRASH TIME"] = pd.to_datetime(df["CRASH TIME"]).dt.hour

token = "pk.eyJ1IjoibGF1cmluYnJlY2h0ZXIiLCJhIjoiY2w1eTJha3gwMDA3czNvcnlnaDFlMmJhMCJ9.NjtQ8ujSN7307Hj4M9S_DA"


# df_sample = df.sample(10_000, replace=False)
# fig = px.scatter_mapbox(
#     df_sample, 
#     lat="LATITUDE", 
#     lon="LONGITUDE",
#     size=df_sample["NUMBER OF PERSONS INJURED"]*5,
#     color=df_sample["NUMBER OF PERSONS KILLED"].astype(str)
#     )
# fig.update_layout(mapbox_style="dark", mapbox_accesstoken=token)
# fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})



app.layout = html.Div([
    
    dbc.Row([

        dbc.Col([
            html.Div("Number of Samples to plot"),
            dcc.Slider(
                min=0,
                max=len(df),
                step=len(df)//10,
                id="point-slider",
                value=len(df)//5,
                
                
                )
        ], width=4),

        dbc.Col([
            html.Div("Please Select a Borough"),
            dcc.Dropdown(
                options=list(df["BOROUGH"].dropna().unique()),
                id="borough-select"
            )
        ], id="borough-col", width=4),

        dbc.Col([
            dbc.Label("Select hours betweeen which Accidents occurred", html_for="range-slider"),
            dcc.RangeSlider(
                id="hour-slider", 
                min=0, max=24, 
                value=[0, 24],
                ),
        ], width=4),

        # dbc.Col([
 
        # ], width=2)
    
    ], style={
        "margin-top":"2%",
        "background-color":"black",
        "color":"#d6d6d6"
        }),

    html.Br(),

    dbc.Row([
    
        dcc.Graph(
            id="map", style={"height":"50%"})
    
    ]),

    dbc.Row([

        dbc.Col([
            dcc.Graph(id="accidents-history")
        ])


    ])
])

@app.callback(
    # Output("accidents-by-hour", "figure"),
    Output("accidents-history", "figure"),
    Input("point-slider", "value"),
    Input("borough-select", "value")
)

def update_graph(n_to_sample, borough):
    print(borough, n_to_sample)

    if borough:
        query_res = df.loc[(df["BOROUGH"] == borough)]
        n_to_sample = min(n_to_sample, len(query_res))

        df_selected = query_res.sample(n_to_sample, replace=False)
    else:
        df_selected = df.sample(n_to_sample)

    fig = make_subplots(
            rows=1, 
            cols=2, 
            subplot_titles=(
                "Number of people injured by hour",
                "Number of people injured by date"
                )
            )

    hourly = df_selected.groupby("CRASH TIME").agg(n_inj=("NUMBER OF PERSONS INJURED", "sum"))
    trend = df_selected.groupby("CRASH DATE").agg(n_inj=("NUMBER OF PERSONS INJURED", "sum")).rolling(10).mean()

    fig.add_trace(
        go.Scatter(
            x=hourly.index,
            y=hourly["n_inj"],
            name="Injuries by Hour"
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=trend.index,
            y=trend["n_inj"],
            name="Injuries by Date"
        ),
        row=1,
        col=2,
        
    )

    # hourly = px.histogram(
    #             data_frame=df.sample(10_000),
    #             x="CRASH TIME",
    #             y="NUMBER OF PERSONS INJURED",
    #             title="Number of people injured by hour"
    #         ) 
    # hourly.update_layout(
    #     xaxis_title="Hour of day",
    #     yaxis_title="Number of people injured",
    #     plot_bgcolor = '#191a1a',
    #     paper_bgcolor = '#191a1a',
    #     width=200
    # )


    fig.update_xaxes(title_text="Hour of Day", showgrid=False, row=1, col=1)
    fig.update_xaxes(title_text="N Injured", showgrid=False, row=1, col=1)
    
    fig.update_yaxes(title_text="Date", showgrid=False, row=1, col=2)
    fig.update_yaxes(title_text="N injured", showgrid=False, row=1, col=2)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor = '#191a1a',
        font=dict(
            color="#d6d6d6"
        ),
        margin=dict(
        l=5,
        r=5,
        b=10,
        t=30,
        pad=0
        )
    )


    return fig




@app.callback(
    Output("map", "figure"),
    Input("borough-select", "value"),
    Input("point-slider", "value"),
    Input("hour-slider", "value")
)

def update_map(borough, n_to_sample, hours):
    # df_sample = df.sample(n_to_sample, replace=False)
    print(hours)


    if borough:
        query_res = df.loc[(df["BOROUGH"] == borough) & (df["CRASH TIME"] > hours[0]) & (df["CRASH TIME"] < hours[1])]
        n_to_sample = min(n_to_sample, len(query_res))

        df_selected = query_res.sample(n_to_sample, replace=False)
    else:
        df_selected = df.sample(n_to_sample)

    print(len(df_selected))

    print(n_to_sample)

    print(borough)
    fig = px.scatter_mapbox(
        df_selected, 
        lat="LATITUDE", 
        lon="LONGITUDE",
        size=df_selected["NUMBER OF PERSONS INJURED"]*5,
        color=df_selected["NUMBER OF PERSONS KILLED"].astype(str),
        color_discrete_sequence=px.colors.qualitative.T10,   # Antique
    )

    fig.update_layout(mapbox_style="dark", mapbox_accesstoken=token)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    fig.update_layout(legend=dict(
        title="Number of Deaths",
        bgcolor="rgba(25,26,26,0.3)",
        # bgcolor="#191a1a",
        font=dict(
            color="#d6d6d6"
        ),
        x=0.01,
        y=0.01,
        ),
        height=370,
    )

    return fig


if __name__ == "__main__":
    app.run_server(port="8080")