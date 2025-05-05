import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd

app = dash.Dash(__name__)
app.title = "BTC Trades Dashboard"

# Define layout
app.layout = html.Div([
    html.H1("Live BTC/USDT Trades"),
    dcc.Interval(id='interval-component', interval=5000, n_intervals=0),
    html.Div(id='trade-table')
])

# Define callback to update the table every 5 seconds
@app.callback(
    Output('trade-table', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_table(n):
    try:
        df = pd.read_csv("btc_trades.csv")
        rows = []
        for i in range(len(df) - 1, max(len(df) - 21, -1), -1):
            row = df.iloc[i]
            color = "#d4f8d4" if row["side"].lower() == "buy" else "#f8d4d4"
            rows.append(
                html.Tr(
                    [html.Td(row[col]) for col in df.columns],
                    style={"backgroundColor": color}
                )
            )
        table = html.Table([
            html.Thead(html.Tr([html.Th(col) for col in df.columns])),
            html.Tbody(rows)
        ])
        return table
    except Exception as e:
        return html.Div(f"Error reading file: {e}")


if __name__ == '__main__':
    app.run(debug=True)
