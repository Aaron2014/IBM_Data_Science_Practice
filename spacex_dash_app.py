# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np
import io
import js

# Read the spacex data into pandas dataframe
URL = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv'
#resp = await js.fetch(URL)
#spacex_csv_file = io.BytesIO((await resp.arrayBuffer()).to_py())

spacex_df = pd.read_csv(URL)
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
launch_site = spacex_df['Launch Site'].unique()
launch_site = np.insert(launch_site, 0, 'All Sites')

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                        options=[{'label': i, 'value': i} for i in launch_site],
                                        value='All Sites',
                                        placeholder="Select a launch site",
                                        searchable=True,
                                        style={'width':'80%', 'padding':'3px', 'font-size': '20px', 'text-align-last' : 'center'}),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',value=[min_payload, max_payload], 
                                    marks={0: '0', 2000: '2000', 4000: '4000', 6000: '6000', 8000: '8000', 10000: '10000'},
                                    min=0, max=10000, step=1000),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback( Output(component_id='success-pie-chart', component_property='figure'),
               Input(component_id='site-dropdown', component_property='value')
               )

def get_pie_chart(entered_site):
    
    if entered_site == 'All Sites':
        pie_fig = px.pie(spacex_df, values='class',
                        names='Launch Site',
                        title='Total Success Launch by all Launch Sites')
        return pie_fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site']==entered_site]
        filtered_df = filtered_df.groupby(['Launch Site', 'class']).size().reset_index(name='class count')
        pie_fig = px.pie(filtered_df, values='class count',
        names='class',
        title='Total Success Launch by' +  entered_site + 'Launch Sites')

        return pie_fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id="payload-slider", component_property="value")]
              )
def get_scatter_plot(entered_site, payload):
    filtered_df = spacex_df[spacex_df['Payload Mass (kg)'].between(payload[0],payload[1])]
    if entered_site == 'All Sites':
        scatter_fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                                 color='Booster Version Category',
                                 labels={'x': 'Payload Mass(Kg)', 'y': 'Class'},
                                 title='Total Success Launch by all Launch Sites')

        return scatter_fig
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]

        scatter_fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                                 color='Booster Version Category',
                                 labels={'x': 'Payload Mass(Kg)', 'y': 'Class'},
                                 title='Total Success Launch for ' +  entered_site + 'Launch Sites')
        return scatter_fig

# Run the app
if __name__ == '__main__':
    app.run_server()
