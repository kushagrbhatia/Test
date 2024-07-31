import pandas as pd

# Load your data
df = pd.read_csv('path_to_your_data_file.csv')  # Replace with the actual path to your data file

# Rename the columns based on the provided indices
df.rename(columns={
    df.columns[9]: 'CpuUsage95',
    df.columns[12]: 'CpuDemand95',
    df.columns[15]: 'CpuContention95',
    df.columns[18]: 'MemUsage95'
}, inplace=True)

# Melt the DataFrame to long format
df_melted = df.melt(id_vars=['Date', 'Cluster'], 
                    value_vars=['CpuUsage95', 'CpuDemand95', 'CpuContention95', 'MemUsage95'],
                    var_name='metric', 
                    value_name='value')

# Save the transformed data to a CSV for use in the Dash app
df_melted.to_csv('data/transformed_data.csv', index=False)

print("Transformed DataFrame")
print(df_melted.head())



#flask app

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
metric_options = ['CpuUsage95', 'CpuDemand95', 'CpuContention95', 'MemUsage95']

# Dash layout
dash_app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='cluster-dropdown',
            options=[{'label': i, 'value': i} for i in cluster_options],
            value=cluster_options[0]
        )
    ]),
    html.Div([
        dcc.Checklist(
            id='metric-checklist',
            options=[{'label': i, 'value': i} for i in metric_options],
            value=metric_options,
            inline=True
        )
    ]),
    dcc.Graph(id='graph')
])

# Dash callback to update graph
@dash_app.callback(
    Output('graph', 'figure'),
    [Input('cluster-dropdown', 'value'),
     Input('metric-checklist', 'value')]
)
def update_graph(selected_cluster, selected_metrics):
    filtered_df = df[(df['cluster'] == selected_cluster) & (df['metric'].isin(selected_metrics))]
    fig = px.line(filtered_df, x='date', y='value', color='metric',
                  title='30-day Utilization Chart')
    return fig

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)


