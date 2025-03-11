from flask import Flask
import dash
from dash import dcc, html  # Updated import
import psycopg2
import pandas as pd
from sklearn.cluster import KMeans
import plotly.express as px
from sklearn.ensemble import IsolationForest
from dash.dependencies import Input, Output


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
    cursor.execute("SELECT transaction_id, date, customer_id, amount, type FROM transactions;")
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    df = pd.DataFrame(data, columns=["transaction_id", "date", "customer_id", "amount", "type"])
    return df


# Create Flask server
server = Flask(__name__)

# Create Dash app
app = dash.Dash(__name__, server=server, routes_pathname_prefix='/')

# Fetch data
df = fetch_data()



# Compute Customer Segmentation
customer_summary = df.groupby("customer_id").agg(
    total_transactions=("customer_id", "count"),
    total_spent=("amount", "sum")
).reset_index()

# Normalize data for clustering
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
customer_summary["cluster"] = kmeans.fit_predict(customer_summary[["total_transactions", "total_spent"]])

# Scatter Plot for Customer Segmentation
segmentation_fig = px.scatter(
    customer_summary,
    x="total_transactions",
    y="total_spent",
    color=customer_summary["cluster"].astype(str),
    title="Customer Segmentation (Spending Clusters)",
    labels={"cluster": "Spending Cluster"}
)



# Train Isolation Forest for Anomaly Detection
iso_forest = IsolationForest(contamination=0.05, random_state=42)
df["anomaly"] = iso_forest.fit_predict(df[["amount"]])

# Convert anomaly labels: 1 = Normal, -1 = Anomaly
df["anomaly_status"] = df["anomaly"].map({1: "Normal", -1: "Anomaly"})

# Bar Chart: Anomalies vs. Normal Transactions
anomaly_counts = df["anomaly_status"].value_counts().reset_index()
anomaly_counts.columns = ["Status", "Count"]
anomaly_fig = px.bar(
    anomaly_counts, x="Status", y="Count", title="Anomalous vs. Normal Transactions"
)

# Table of flagged anomalies
anomaly_table = df[df["anomaly_status"] == "Anomaly"][
    ["transaction_id", "customer_id", "amount", "anomaly_status"]
]


# Prepare customer-level summary for search
customer_summary = df.groupby("customer_id").agg(
    total_transactions=("customer_id", "count"),
    total_spent=("amount", "sum"),
    credit_ratio=("type", lambda x: (x == "credit").mean()),  # Percentage of credit transactions
    anomaly_status=("anomaly_status", lambda x: "Anomaly" if "Anomaly" in x.values else "Normal")
).reset_index()





# Compute Overview Metrics
total_transactions = len(df)
total_spent = df['amount'].sum()
credit_count = df[df['type'] == 'credit'].shape[0]
debit_count = df[df['type'] == 'debit'].shape[0]

# Pie chart for Credit vs Debit
type_counts = df['type'].value_counts().reset_index()
type_counts.columns = ['Transaction Type', 'Count']

pie_chart = px.pie(type_counts, names='Transaction Type', values='Count', title='Credit vs Debit Distribution')

# Layout Structure
app.layout = html.Div([
    html.H1("Financial Transaction Dashboard"),

    # Overview Panel
    html.Div([
        html.H2("Overview Panel"),
        html.P(f"Total Transactions: {total_transactions}"),
        html.P(f"Total Amount Spent: ${total_spent:,.2f}"),
        dcc.Graph(figure=pie_chart)
    ], id='overview-panel'),


    # Customer Segmentation Panel
    html.Div([
        html.H2("Customer Segmentation Panel"),
        dcc.Graph(figure=segmentation_fig)
    ], id='customer-segmentation-panel'),


    # Anomaly Detection Panel
    html.Div([
        html.H2("Anomaly Detection Panel"),
        dcc.Graph(figure=anomaly_fig),

        html.Div([
            html.Table([
                html.Thead(html.Tr([html.Th(col) for col in anomaly_table.columns])),
                html.Tbody([
                    html.Tr([html.Td(row[col]) for col in anomaly_table.columns])
                    for _, row in anomaly_table.iterrows()
                ])
            ])
        ], style={"max-height": "400px", "overflow-y": "scroll", "display": "block", "border": "1px solid black"})
    ], id='anomaly-detection-panel'),

    # Interactive Customer Search Panel
    html.Div([
        html.H2("Customer Search Panel"),

        # Search Input
        html.Label("Enter Customer ID:"),
        dcc.Input(id='customer-id-input', type='number', placeholder="Enter customer ID", debounce=True),

        # Output display
        html.Div(id='customer-info-output')
    ], id='customer-search-panel'),

])


@app.callback(
    Output('customer-info-output', 'children'),
    [Input('customer-id-input', 'value')]
)
def update_customer_info(customer_id):
    if customer_id is None or customer_id not in customer_summary["customer_id"].values:
        return "No data available for this customer."

    customer_data = customer_summary[customer_summary["customer_id"] == customer_id].iloc[0]

    return html.Div([
        html.P(f"Total Transactions: {customer_data['total_transactions']}"),
        html.P(f"Total Amount Spent: ${customer_data['total_spent']:,.2f}"),
        html.P(f"Credit Ratio: {customer_data['credit_ratio']:.2%}"),
        html.P(f"Anomaly Status: {customer_data['anomaly_status']}")
    ])

if __name__ == "__main__":
    app.run_server(debug=True)