from flask import Flask
import dash
from dash import dcc, html  # Updated import
import psycopg2
import pandas as pd

# PostgreSQL Connection Details
DB_HOST = "localhost"
DB_NAME = "my_dash_db"
DB_USER = "myuser"
DB_PASSWORD = "mypassword"

def fetch_data():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute("SELECT date, amount FROM transactions;")
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    df = pd.DataFrame(data, columns=["date", "amount"])
    return df

# Create Flask server
server = Flask(__name__)

# Create Dash app
app = dash.Dash(__name__, server=server, routes_pathname_prefix='/')

# Fetch data
df = fetch_data()

# Limit to first 100 rows
df = df.head(100)  # Select the first 100 rows

# Dash Layout
app.layout = html.Div([
    html.H1("Live Data from PostgreSQL"),
    dcc.Graph(
        id="database-graph",
        figure={
            "data": [
                {"x": df["date"], "y": df["amount"], "type": "line", "name": "Transaction Amount"}
            ],
            "layout": {"title": "Transaction Amount Over Time"}
        }
    )
])

if __name__ == "__main__":
    app.run_server(debug=True)
