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

def vacc_brand_plotly(mysql_connection, brand):
    vacc_brand_sql = """SELECT Date, First_Dose_Daily, Second_Dose_Daily
                        FROM covid19_vaccination 
                        WHERE Brand = '{}' """.format(brand)

    vacc_brand_table = pd.DataFrame(custom_sql(mysql_connection, vacc_brand_sql))

    fig = go.Figure(data = [go.Bar(name = 'First_Dose', x = vacc_brand_table['Date'], y = vacc_brand_table['First_Dose_Daily']),
                            go.Bar(name = 'Second_Dose', x = vacc_brand_table['Date'], y = vacc_brand_table['Second_Dose_Daily'])])

    fig.update_layout(barmode='stack', 
                      title_text = 'Daily_Vacinated: ' + brand,
                      paper_bgcolor = 'rgba(0,0,0,0)', 
                      plot_bgcolor = 'rgba(0,0,0,0)',
                      xaxis_title = 'Date',
                      yaxis_title = 'Daily_Vaccinated')
    
    return fig

mysql_connection = pymysql.connect(host="127.0.0.1",user='root',password='password',db='airflow',cursorclass=pymysql.cursors.DictCursor)
brand_options_sql = "SELECT DISTINCT(Brand) FROM covid19_vaccination"
brand_options = custom_sql(mysql_connection, brand_options_sql)
brand_options = [ x['Brand'] for x in brand_options ]

app = DjangoDash(name='VaccPlot')

app.layout = html.Div([
                html.Div([    
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


@app.callback(
               Output('vacc_plot', 'figure'),
              [Input('brand', 'value')])
              
def display_value(value):
 
    fig = vacc_brand_plotly(mysql_connection, value)
    
    return fig