sd_CpuCont95_list = [x for x in sd_CpuCont95_list if not np.isnan(x)]
sd_CpuDemand95_list = [x for x in sd_CpuDemand95_list if not np.isnan(x)]
sd_MemUsage95_list = [x for x in sd_MemUsage95_list if not np.isnan(x)]
sd_CpuUsage95_list = [x for x in sd_CpuUsage95_list if not np.isnan(x)]

from flask import Flask, render_template
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

# Initialize Flask app
app = Flask(__name__)

# Initialize Dash app
dash_app = Dash(__name__, server=app, url_base_pathname='/dashboard/')

# Load your data
df = pd.read_csv('data/data_file.csv')  # Modify to load your actual data

# Example data
cluster_options = df['cluster'].unique()

# Dash layout
dash_app.layout = html.Div([
    dcc.Dropdown(
        id='cluster-dropdown',
        options=[{'label': i, 'value': i} for i in cluster_options],
        value=cluster_options[0]
    ),
    dcc.Graph(id='graph')
])

# Dash callback to update graph
@dash_app.callback(
    Output('graph', 'figure'),
    [Input('cluster-dropdown', 'value')]
)
def update_graph(selected_cluster):
    filtered_df = df[df['cluster'] == selected_cluster]
    fig = px.line(filtered_df, x='date', y='value', color='metric',
                  title='30-day Utilization Chart')
    return fig

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)


<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/static/style.css">
    <title>Cluster Visualization</title>
</head>
<body>
    <h1>Cluster Visualization</h1>
    <iframe src="/dashboard/" width="100%" height="600px" frameborder="0"></iframe>
</body>
</html>

body {
    font-family: Arial, sans-serif;
}

h1 {
    text-align: center;
}

iframe {
    border: none;
}


