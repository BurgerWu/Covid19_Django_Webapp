#import libraries
import pandas as pd
import pymysql.cursors
from plotly.offline import plot
from plotly.subplots import make_subplots
import plotly.graph_objs as go

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

def daily_gender_plotly(mysql_connection):
    """
    This function plots daily cases on basis of gender and returns as a div object
    Input: Mysql connection
    Output: Plot div object
    """
    #Create SQL command string
    daily_gender_sql = """SELECT Date_Confirmation, Gender,
                        sum(Number_of_Confirmed_Cases) AS Total_Daily_Cases
                        FROM covid19_cases GROUP BY Date_Confirmation, Gender"""
    
    #Get table from SQL result
    daily_gender_table = pd.DataFrame(custom_sql(mysql_connection, daily_gender_sql))
    
    #Initiate plot data list and append plot object to the list
    plot_data = []
    for gender in daily_gender_table['Gender'].unique():
        sub_df = daily_gender_table[daily_gender_table['Gender'] == gender]
        plot_data.append(go.Bar(name = gender, x = sub_df['Date_Confirmation'], y = sub_df['Total_Daily_Cases']))
    
    #Create graph object Figure object with plot data
    fig = go.Figure(data = plot_data)

    #Update layout for graph object Figure
    fig.update_layout(barmode='stack', 
                      title_text = 'Daily Cases By Gender',
                      paper_bgcolor = 'rgba(0,0,0,0)', 
                      plot_bgcolor = 'rgba(0,0,0,0)',
                      xaxis_title = 'Date',
                      yaxis_title = 'Daily_Cases')
    
    #Turn graph object into local plotly graph
    daily_gender_plot = plot({'data': fig}, output_type='div')

    return daily_gender_plot

def total_age_plotly(mysql_connection):
    """
    This function plots total cases according to age group and returns as a div object
    Input: Mysql connection
    Output: Plot div object
    """
    #Create SQL command string
    total_age_sql = """SELECT Age_Group, SUM(Number_of_Confirmed_Cases) AS Total_Cases
                       FROM covid19_cases 
                       GROUP BY Age_Group"""

    #Get table from SQL result and sort by age                   
    total_age_table = pd.DataFrame(custom_sql(mysql_connection, total_age_sql))
    total_age_table['new_age'] = total_age_table['Age_Group'].apply(lambda x: int(x.split('+')[0].split('-')[0]))
    total_age_table.sort_values(by='new_age', inplace=True)
    
    #Create graph object Figure object with data
    fig = go.Figure(data = go.Bar(name = 'Age_Group', x = total_age_table['Age_Group'], y = total_age_table['Total_Cases']))

    #Update layout for graph object Figure
    fig.update_layout(title_text = 'Total Cases By Age Group',
                      paper_bgcolor = 'rgba(0,0,0,0)', 
                      plot_bgcolor = 'rgba(0,0,0,0)',
                      xaxis_title = 'Age_Group',
                      yaxis_title = 'Total_Cases')
    
    #Turn graph object into local plotly graph
    total_age_plot = plot({'data': fig}, output_type='div')

    return total_age_plot

def exam_stats_plotly(mysql_connection):
    """
    This function plots daily examinations as well as positive rate and returns as a div object
    Input: Mysql connection
    Output: Plot div object
    """
    #Create SQL command string
    exam_stats_sql = """WITH c AS (SELECT Date_Confirmation, 
                                   SUM(Number_of_Confirmed_Cases) AS Total_Cases 
		                           FROM covid19_cases GROUP BY Date_Confirmation)

                        SELECT s.Date_Reported, s.Reported_Covid19, 
                               s.Reported_Enhanced_Surveillance,
	                           s.Reported_Home_Quarantine, c.Total_Cases
                        FROM covid19_suspects s
                        LEFT JOIN c ON s.Date_Reported = c.Date_Confirmation"""

    #Get table from SQL result
    exam_stats_table = pd.DataFrame(custom_sql(mysql_connection, exam_stats_sql))
    
    #Fill 0 if there is no reported positive cases
    exam_stats_table['Total_Cases'].fillna(0, inplace = True)

    #Reconstruct table and calculate positive rate
    exam_stats_table['Total_Examinations'] = exam_stats_table['Reported_Covid19'] + exam_stats_table['Reported_Enhanced_Surveillance'] + exam_stats_table['Reported_Home_Quarantine']
    exam_stats_table = exam_stats_table[exam_stats_table['Total_Examinations'] != 0]
    exam_stats_table['Positive_Rate'] = exam_stats_table['Total_Cases']/exam_stats_table['Total_Examinations'] * 100
 
    #Create figure by applying make_subplot function because we later will plot two plots on same figure object
    fig = make_subplots(rows = 3, cols = 1,
                        specs = [[{}], [{"rowspan": 2}], [None]],
                        subplot_titles = ("Positive Rate", "Total Examinations"))
    # Add traces to different subplot
    fig.add_trace(go.Bar(name = 'Reported_Covid19', x = exam_stats_table['Date_Reported'], 
                         y = exam_stats_table['Reported_Covid19']), row = 2, col = 1)
    fig.add_trace(go.Bar(name = 'Reported_Enhanced_Surveillance', x = exam_stats_table['Date_Reported'],
                         y = exam_stats_table['Reported_Enhanced_Surveillance']), row = 2, col = 1)
    fig.add_trace(go.Bar(name = 'Reported_Home_Quarantine', x = exam_stats_table['Date_Reported'], 
                         y = exam_stats_table['Reported_Home_Quarantine']), row = 2, col = 1)
    fig.add_trace(go.Scatter(name = 'Positive_Rate', x = exam_stats_table['Date_Reported'], 
                             y = exam_stats_table['Positive_Rate']), row = 1, col = 1)
    
    #Update layout for figure
    fig.update_layout(title_text = 'Daily Examinations VS Positive Rate',
                      barmode = 'stack',
                      paper_bgcolor = 'rgba(0,0,0,0)', 
                      plot_bgcolor = 'rgba(0,0,0,0)')

    # Set x-axis title
    fig.update_xaxes(title_text = "Date", row = 2, col = 1)

    # Set y-axes titles
    fig.update_yaxes(title_text = "Daily Examinations", row = 2, col = 1)
    fig.update_yaxes(title_text = "Positive Rate (%)", row = 1, col = 1)

    #Turn graph object into local plotly graph
    exam_stats_plot = plot({'data': fig}, output_type='div')

    return exam_stats_plot

def daily_vacc_plotly(mysql_connection):
    """
    This function plots daily vaccinations and returns as a div object
    Input: Mysql connection
    Output: Plot div object
    """
    #Create SQL command string
    daily_vacc_sql = "SELECT Date, Brand, First_Dose_Daily + Second_Dose_Daily + Third_Dose_Beyond_Daily AS Total_Vaccinated_Daily FROM covid19_vaccination"
    
    #Get table from SQL result
    daily_vacc_table = pd.DataFrame(custom_sql(mysql_connection, daily_vacc_sql))
    
    #Initiate plot data list and append plot object to the list
    plot_data = []
    for vaccines in daily_vacc_table['Brand'].unique():
        sub_df = daily_vacc_table[daily_vacc_table['Brand'] == vaccines]
        plot_data.append(go.Bar(name = vaccines, x = sub_df['Date'], y = sub_df['Total_Vaccinated_Daily']))
    
    #Create graph object Figure object with plot data
    fig = go.Figure(data = plot_data)

    #Update layout for graph object Figure
    fig.update_layout(barmode='stack', 
                      title_text = 'Daily Vaccination',
                      paper_bgcolor = 'rgba(0,0,0,0)', 
                      plot_bgcolor = 'rgba(0,0,0,0)',
                      xaxis_title = 'Date',
                      yaxis_title = 'Daily_Vaccination')

    #Turn graph object into local plotly graph
    daily_vacc_plot = plot({'data': fig}, output_type='div')

    return daily_vacc_plot

def total_vacc_plotly(mysql_connection):
    """
    This function plots total vaccinations of each vaccine and returns as a div object
    Input: Mysql connection
    Output: Plot div object
    """
    #Create SQL command string
    total_vacc_sql = """SELECT Brand, SUM(First_Dose_Daily) AS Total_First_Dose, 
	                                  SUM(Second_Dose_Daily) AS Total_Second_Dose,
                                      SUM(Third_Dose_Beyond_Daily) AS Total_Third_Dose_Beyond 
                        FROM covid19_vaccination
                        GROUP BY Brand"""
    
    #Get total vaccination table from SQL result
    total_vacc_table = pd.DataFrame(custom_sql(mysql_connection, total_vacc_sql))
    
    #Create graph object Figure object with data
    fig = go.Figure(data = [go.Bar(name = 'First_Dose', x = total_vacc_table['Brand'], y = total_vacc_table['Total_First_Dose']),
                            go.Bar(name = 'Second_Dose', x = total_vacc_table['Brand'], y = total_vacc_table['Total_Second_Dose']),
                            go.Bar(name = 'Third_Dose_Beyond', x = total_vacc_table['Brand'], y = total_vacc_table['Total_Third_Dose_Beyond'])])

    #Update layout for graph object Figure
    fig.update_layout(barmode='stack', 
                      title_text = 'Total Vacination Plot',
                      paper_bgcolor = 'rgba(0,0,0,0)', 
                      plot_bgcolor = 'rgba(0,0,0,0)',
                      xaxis_title = 'Brand',
                      yaxis_title = 'Total Vaccination')
    
    #Turn graph object into local plotly graph
    total_vacc_plot = plot({'data': fig}, output_type='div')

    return total_vacc_plot

