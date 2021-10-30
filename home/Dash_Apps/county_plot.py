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

def daily_county_plotly(mysql_connection, county):
    """
    This function creates dash app for plotting daily cases by county selected
    Input: Mysql connection and county specified
    Output: Figure object
    """
    #Create SQL command string
    daily_county_sql = """SELECT Date_Confirmation,
                                 sum(Number_of_Confirmed_Cases) AS Total_Daily_Cases
                          FROM covid19_cases 
                          WHERE County_Living = '{}'
                          GROUP BY Date_Confirmation""".format(county)
    
    #Get table from SQL result
    daily_county_table = pd.DataFrame(custom_sql(mysql_connection, daily_county_sql))
    
    #Create graph object Figure object with data
    fig = go.Figure(data = go.Bar(name = 'Daily Cases: ' + county, x = daily_county_table['Date_Confirmation'], y = daily_county_table['Total_Daily_Cases']))
    
    #Update layout for graph object Figure
    fig.update_layout(barmode='stack', 
                      title_text = 'Daily Cases: ' + county,
                      paper_bgcolor = 'rgba(0,0,0,0)', 
                      plot_bgcolor = 'rgba(0,0,0,0)',
                      xaxis_title = 'Date',
                      yaxis_title = 'Total_Daily_Cases')
    
    return fig

#Create Mysql connection
mysql_connection = mysql_connect.conn

#Get plot options by running SQL query
county_options_sql = "SELECT DISTINCT(County_Living) FROM covid19_cases"
county_options = custom_sql(mysql_connection, county_options_sql)
county_options = [ x['County_Living'] for x in county_options ]

#Create DjangoDash applicaiton
app = DjangoDash(name='CountyPlot')

#Configure app layout
app.layout = html.Div([
                html.Div([
                    
                    #Add dropdown for option selection
                    dcc.Dropdown(
                    id = 'county',
                    options = [{'label': i, 'value': i} for i in county_options],
                    value = 'Taipei City')],
                    style={'width': '25%', 'margin':'0px auto'}),

                html.Div([                 
                    dcc.Graph(id = 'county_plot', 
                              animate = True, 
                              style={"backgroundColor": "#FFF0F5"})])
                        ])

#Define app input and output callbacks
@app.callback(
               Output('county_plot', 'figure'),
              [Input('county', 'value')])
              
def display_value(value):
    """
    This function returns figure object according to value input
    Input: Value specified
    Output: Figure object
    """
    #Get daily cases plot with input value
    fig = daily_county_plotly(mysql_connection, value)
    
    return fig
