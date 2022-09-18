from plotly import subplots
import dash
import dash_cytoscape as cyto  
from dash import dcc, html
from dash.dependencies import Output, Input, State
import pandas as pd  
import numpy as np
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import yfinance as yf


def RSI(x, n=14):
    delta = x.diff()


    gains = pd.Series(np.where(delta > 0, delta, 0))
    losses = pd.Series(np.abs(np.where(delta < 0, delta, 0)))

    gains_ewm = gains.ewm(n-1).mean()
    losses_ewm = losses.ewm(n-1).mean()
    rsi = 100 - (100 / (1 + gains_ewm/losses_ewm))

    return rsi


def SMA(x, n):
    return x.rolling(n).mean()


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], assets_folder="assets\\assets_financial_db")

companies = ['HON', 'WMT', 'TRV', 'JPM', 'NKE', 'CRM', 'BA', 
            'PG', 'CAT', 'HD', 'MSFT', 'INTC', 'DOW', 'UNH', 
            'AMGN', 'DIS', 'MCD', 'MRK', 'JNJ', 'AXP', 'KO', 
            'MMM', 'GS', 'CSCO', 'V', 'VZ', 'AAPL', 'WBA', 'IBM', 'CVX']

dataframes = {}

for idx, symbol in (enumerate(companies[:2])):
    company = yf.Ticker(symbol)
    hist = company.history(period="max", start="1986-03-13", end="2022-01-01")
    hist["SMA50"] = SMA(hist["Close"], 50)
    hist["SMA200"] = SMA(hist["Close"], 200)
    dataframes[symbol] = hist



app.layout = html.Div([
    
    dbc.Row([
        dbc.Col("Choose a Dow Jones company"),
        dbc.Col(dcc.Dropdown(id="stock-selection", options=companies, value="HON")),
    ]),

    dcc.Graph(id="chart"),

])

@app.callback(
    Output("chart", "figure"),
    Input("stock-selection", "value"),
)
def update_app(stock):

    fig = subplots.make_subplots(
        rows=2, 
        cols=1,
        shared_xaxes=True,
        row_heights=[0.7,0.3],
        )

    data = dataframes[stock].iloc[:1000]

    print(data)

    pos = data.loc[data["Close"] > data["Open"]]
    neg = data.loc[data["Close"] < data["Open"]]


    fig.add_trace(go.Candlestick(x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close']),
                    row=1,col=1)

    fig.add_trace(go.Bar(
        x=neg.index,
        y=neg["Volume"],
        marker_color='red'  
    ),
    col=1,
    row=2)

    fig.add_trace(go.Bar(
        x=pos.index,
        y=pos["Volume"],
        marker_color='green'  
    ),
    col=1,
    row=2)

    fig.add_trace(go.Scatter(
                    x=data.index,
                    y=data.SMA200,
                    name="SMA200"
                ), row=1, col=1)
    fig.add_trace(go.Scatter(
                    x=data.index,
                    y=data.SMA50,
                    name="SMA50"
                ), row=1, col=1)

    fig.update_layout(
    
        

        height=800,
        plot_bgcolor = 'white',
        paper_bgcolor = 'white',

        xaxis = dict(
            showgrid = True,
            showticklabels = True,
            gridwidth=0.5, 
            gridcolor='#ede9e8',
            autorange=True),
        
        yaxis = dict(
            showgrid = True,
            showticklabels = True,
            gridwidth=0.5, 
            gridcolor='#ede9e8',
            autorange=True)
    )

    fig.update_layout(xaxis_rangeslider_visible=False)

    fig['layout']['yaxis']['title']='Price ($)'
    fig['layout']['yaxis2']['title']='Volume'

    return fig

if __name__ == "__main__":
    app.run_server(debug=False)