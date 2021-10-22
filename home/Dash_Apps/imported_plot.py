from os import name
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
import pymysql
import pandas as pd

def custom_sql(connection, sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchall()
    return row


def daily_cases_plotly(mysql_connection, group):
    daily_case_sql = """SELECT Date_Confirmation, Imported,
                        sum(Number_of_Confirmed_Cases) AS Total_Daily_Cases
                        FROM covid19_cases GROUP BY Date_Confirmation, Imported"""
    daily_case_table = pd.DataFrame(custom_sql(mysql_connection, daily_case_sql))
    plot_data = []
    if group == 'Domestic' or group == 'All':
        sub_df = daily_case_table[daily_case_table['Imported'] == 0]
        plot_data.append(go.Bar(name = 'Domestic', x = sub_df['Date_Confirmation'], y = sub_df['Total_Daily_Cases']))
    if group == 'Imported' or group == 'All':
        sub_df = daily_case_table[daily_case_table['Imported'] == 1]
        plot_data.append(go.Bar(name = 'Imported', x = sub_df['Date_Confirmation'], y = sub_df['Total_Daily_Cases']))
    
    fig = go.Figure(data = plot_data)

    fig.update_layout(barmode='stack', 
                      title_text = 'Total Daily Cases',
                      paper_bgcolor = 'rgba(0,0,0,0)', 
                      plot_bgcolor = 'rgba(0,0,0,0)',
                      xaxis_title = 'Date',
                      yaxis_title = 'Total_Daily_Cases')
    
    return fig

mysql_connection = pymysql.connect(host="127.0.0.1",user='root',password='password',db='airflow',cursorclass=pymysql.cursors.DictCursor)

app = DjangoDash(name='ImportedPlot')

app.layout = html.Div([
                html.Div([    
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


@app.callback(
               Output('imported_plot', 'figure'),
              [Input('imported', 'value')])
              
def display_value(value):
 
    fig = daily_cases_plotly(mysql_connection, value)
    
    return fig