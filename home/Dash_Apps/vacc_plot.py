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

def vacc_brand_plotly(mysql_connection, brand):
    """
    This function creates dash app for plotting daily vaccinations by brand selected
    Input: Mysql connection and county specified
    Output: Figure object
    """
    #Create SQL command string
    vacc_brand_sql = """SELECT Date, First_Dose_Daily, Second_Dose_Daily, Third_Dose_Beyond_Daily
                        FROM covid19_vaccination 
                        WHERE Brand = '{}' """.format(brand)
    
    #Get table from SQL result
    vacc_brand_table = pd.DataFrame(custom_sql(mysql_connection, vacc_brand_sql))
    
    #Create graph object Figure object with data
    fig = go.Figure(data = [go.Bar(name = 'First_Dose', x = vacc_brand_table['Date'], y = vacc_brand_table['First_Dose_Daily']),
                            go.Bar(name = 'Second_Dose', x = vacc_brand_table['Date'], y = vacc_brand_table['Second_Dose_Daily']),
                            go.Bar(name = 'Third_Dose_Beyond', x = vacc_brand_table['Date'], y = vacc_brand_table['Third_Dose_Beyond_Daily'])])
    #Update layout for graph object Figure
    fig.update_layout(barmode='stack', 
                      title_text = 'Daily_Vacinated: ' + brand,
                      paper_bgcolor = 'rgba(0,0,0,0)', 
                      plot_bgcolor = 'rgba(0,0,0,0)',
                      xaxis_title = 'Date',
                      yaxis_title = 'Daily_Vaccinated')
    
    return fig

#Create Mysql connection
mysql_connection = mysql_connect.conn

#Get plot options by running SQL query
brand_options_sql = "SELECT DISTINCT(Brand) FROM covid19_vaccination"
brand_options = custom_sql(mysql_connection, brand_options_sql)
brand_options = [ x['Brand'] for x in brand_options ]

#Create DjangoDash applicaiton
app = DjangoDash(name='VaccPlot')

#Configure app layout
app.layout = html.Div([
                html.Div([ 

                    #Add dropdown for option selection
                    dcc.Dropdown(
                    id = 'brand',
                    options = [{'label': i, 'value': i} for i in brand_options],
                    value = 'AstraZeneca')],
                    style={'width': '25%', 'margin':'0px auto'}),

                html.Div([                 
                    dcc.Graph(id = 'vacc_plot', 
                              animate = True, 
                              style={"backgroundColor": "#FFF0F5"})])
                        ])

#Define app input and output callbacks
@app.callback(
               Output('vacc_plot', 'figure'),
              [Input('brand', 'value')])
              
def display_value(value):
    """
    This function returns figure object according to value input
    Input: Value specified
    Output: Figure object
    """
    #Get daily vaccination plot with input value
    fig = vacc_brand_plotly(mysql_connection, value)
    
    return fig
