#import libraries
from os import name
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
from .db_connections import mysql_connect
import pymysql
import pandas as pd

def custom_sql(connection, sql):
    """
    This function runs SQL command using connection specified
    Input: Mysql connection and SQL command
    Output: Returned results
    """
    #Execute SQL command using input connection as cursor
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchall()
    return row


def daily_cases_plotly(mysql_connection, group):
    """
    This function creates dash app for plotting daily cases by group selected (All, imported or domestic)
    Input: Mysql connection and county specified
    Output: Figure object
    """
    #Create SQL command string
    daily_case_sql = """SELECT Date_Confirmation, Imported,
                        sum(Number_of_Confirmed_Cases) AS Total_Daily_Cases
                        FROM covid19_cases GROUP BY Date_Confirmation, Imported"""
    
    #Get table from SQL result
    daily_case_table = pd.DataFrame(custom_sql(mysql_connection, daily_case_sql))

    #Initiate plot data list and append plot object to the list
    plot_data = []
    if group == 'Domestic' or group == 'All':
        sub_df = daily_case_table[daily_case_table['Imported'] == 0]
        plot_data.append(go.Bar(name = 'Domestic', x = sub_df['Date_Confirmation'], y = sub_df['Total_Daily_Cases']))
    if group == 'Imported' or group == 'All':
        sub_df = daily_case_table[daily_case_table['Imported'] == 1]
        plot_data.append(go.Bar(name = 'Imported', x = sub_df['Date_Confirmation'], y = sub_df['Total_Daily_Cases']))
    
    #Create graph object Figure object with plot data
    fig = go.Figure(data = plot_data)
    
    #Update layout for graph object Figure
    fig.update_layout(barmode='stack', 
                      title_text = 'Total Daily Cases',
                      paper_bgcolor = 'rgba(0,0,0,0)', 
                      plot_bgcolor = 'rgba(0,0,0,0)',
                      xaxis_title = 'Date',
                      yaxis_title = 'Total_Daily_Cases')
    
    return fig

#Create Mysql connection
mysql_connection = mysql_connect.conn

#Create DjangoDash applicaiton
app = DjangoDash(name='ImportedPlot')

#Configure app layout
app.layout = html.Div([
                html.Div([ 

                    #Add dropdown for option selection
                    dcc.Dropdown(
                    id = 'imported',
                    options = [{'label': 'All', 'value': 'All'},
                               {'label': 'Imported', 'value': 'Imported'},
                               {'label': 'Domestic', 'value': 'Domestic'}],
                    value = 'All')],
                    style={'width': '25%', 'margin':'0px auto'}),

                html.Div([                 
                    dcc.Graph(id = 'imported_plot', 
                              animate = True, 
                              style={"backgroundColor": "#FFF0F5"})])
                        ])

#Define app input and output callbacks
@app.callback(
               Output('imported_plot', 'figure'),
              [Input('imported', 'value')])
              
def display_value(value):
    """
    This function returns figure object according to value input
    Input: Value specified
    Output: Figure object
    """
    #Get daily cases plot with input value
    fig = daily_cases_plotly(mysql_connection, value)
    
    return fig
