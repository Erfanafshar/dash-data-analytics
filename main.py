from flask import Flask
import dash
import dash_core_components as dcc
import dash_html_components as html

# Create Flask app
server = Flask(__name__)

# Create Dash app
app = dash.Dash(__name__, server=server, routes_pathname_prefix='/')

# Dash Layout
app.layout = html.Div([
    html.H1("Welcome to My Dash App"),
    dcc.Graph(
        id="example-graph",
        figure={
            "data": [{"x": [1, 2, 3], "y": [4, 1, 2], "type": "line"}],
            "layout": {"title": "Sample Graph"}
        }
    )
])

if __name__ == "__main__":
    app.run_server(debug=True)
