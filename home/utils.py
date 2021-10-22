import pandas as pd
import pymysql.cursors
from plotly.offline import plot
from plotly.subplots import make_subplots
import plotly.graph_objs as go

def custom_sql(connection, sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchall()
    return row

def daily_cases_plotly(request, mysql_connection, group = 'All'):
    daily_case_sql = """SELECT Date_Confirmation, Imported,
                        sum(Number_of_Confirmed_Cases) AS Total_Daily_Cases
                        FROM covid19_cases GROUP BY Date_Confirmation, Imported"""
    daily_case_table = pd.DataFrame(custom_sql(mysql_connection, daily_case_sql))
    plot_data = []
    if group == 'Domestic' or 'All':
        sub_df = daily_case_table[daily_case_table['Imported'] == 0]
        plot_data.append(go.Bar(name = 'Domestic', x = sub_df['Date_Confirmation'], y = sub_df['Total_Daily_Cases']))
    if group == 'Imported' or 'All':
        sub_df = daily_case_table[daily_case_table['Imported'] == 1]
        plot_data.append(go.Bar(name = 'Imported', x = sub_df['Date_Confirmation'], y = sub_df['Total_Daily_Cases']))
    
    fig = go.Figure(data = plot_data)

    fig.update_layout(barmode='stack', 
                      title_text = 'Total Daily Cases',
                      paper_bgcolor = 'rgba(0,0,0,0)', 
                      plot_bgcolor = 'rgba(0,0,0,0)',
                      xaxis_title = 'Date',
                      yaxis_title = 'Total_Daily_Cases')
    
    daily_case_plot = plot({'data': fig}, output_type='div')

    return daily_case_plot

def daily_county_plotly(request, mysql_connection, county):
    daily_county_sql = """SELECT Date_Confirmation,
                                 sum(Number_of_Confirmed_Cases) AS Total_Daily_Cases
                          FROM covid19_cases 
                          WHERE County_Living = '{}'
                          GROUP BY Date_Confirmation""".format(county)
    daily_county_table = pd.DataFrame(custom_sql(mysql_connection, daily_county_sql))
    fig = go.Figure(data = go.Bar(name = 'Daily Cases: ' + county, x = daily_county_table['Date_Confirmation'], y = daily_county_table['Total_Daily_Cases']))

    fig.update_layout(barmode='stack', 
                      title_text = 'Daily Cases: ' + county,
                      paper_bgcolor = 'rgba(0,0,0,0)', 
                      plot_bgcolor = 'rgba(0,0,0,0)',
                      xaxis_title = 'Date',
                      yaxis_title = 'Total_Daily_Cases')
    
    daily_county_plot = plot({'data': fig}, output_type='div')

    return daily_county_plot

def daily_gender_plotly(request, mysql_connection):
    daily_gender_sql = """SELECT Date_Confirmation, Gender,
                        sum(Number_of_Confirmed_Cases) AS Total_Daily_Cases
                        FROM covid19_cases GROUP BY Date_Confirmation, Gender"""
    daily_gender_table = pd.DataFrame(custom_sql(mysql_connection, daily_gender_sql))
    plot_data = []
    for gender in daily_gender_table['Gender'].unique():
        sub_df = daily_gender_table[daily_gender_table['Gender'] == gender]
        plot_data.append(go.Bar(name = gender, x = sub_df['Date_Confirmation'], y = sub_df['Total_Daily_Cases']))
    
    fig = go.Figure(data = plot_data)

    fig.update_layout(barmode='stack', 
                      title_text = 'Daily Cases By Gender',
                      paper_bgcolor = 'rgba(0,0,0,0)', 
                      plot_bgcolor = 'rgba(0,0,0,0)',
                      xaxis_title = 'Date',
                      yaxis_title = 'Daily_Cases')
    
    daily_gender_plot = plot({'data': fig}, output_type='div')

    return daily_gender_plot

def total_age_plotly(request, mysql_connection):
    total_age_sql = """SELECT Age_Group, SUM(Number_of_Confirmed_Cases) AS Total_Cases
                       FROM covid19_cases 
                       GROUP BY Age_Group"""
    total_age_table = pd.DataFrame(custom_sql(mysql_connection, total_age_sql))
    total_age_table['new_age'] = total_age_table['Age_Group'].apply(lambda x: int(x.split('+')[0].split('-')[0]))
    total_age_table.sort_values(by='new_age', inplace=True)

    fig = go.Figure(data = go.Bar(name = 'Age_Group', x = total_age_table['Age_Group'], y = total_age_table['Total_Cases']))

    fig.update_layout(title_text = 'Total Cases By Age Group',
                      paper_bgcolor = 'rgba(0,0,0,0)', 
                      plot_bgcolor = 'rgba(0,0,0,0)',
                      xaxis_title = 'Age_Group',
                      yaxis_title = 'Total_Cases')
    
    total_age_plot = plot({'data': fig}, output_type='div')

    return total_age_plot

def exam_stats_plotly(request, mysql_connection):
    exam_stats_sql = """WITH c AS (SELECT Date_Confirmation, 
                                   SUM(Number_of_Confirmed_Cases) AS Total_Cases 
		                           FROM covid19_cases GROUP BY Date_Confirmation)

                        SELECT s.Date_Reported, s.Reported_Covid19, 
                               s.Reported_Enhanced_Surveillance,
	                           s.Reported_Home_Quarantine, c.Total_Cases
                        FROM covid19_suspects s
                        LEFT JOIN c ON s.Date_Reported = c.Date_Confirmation"""

    exam_stats_table = pd.DataFrame(custom_sql(mysql_connection, exam_stats_sql))
    exam_stats_table['Total_Cases'].fillna(0, inplace = True)
    exam_stats_table['Total_Examinations'] = exam_stats_table['Reported_Covid19'] + exam_stats_table['Reported_Enhanced_Surveillance'] + exam_stats_table['Reported_Home_Quarantine']
    exam_stats_table = exam_stats_table[exam_stats_table['Total_Examinations'] != 0]
    exam_stats_table['Positive_Rate'] = exam_stats_table['Total_Cases']/exam_stats_table['Total_Examinations'] * 100
 
    # Create figure with secondary y-axis
    #fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig = make_subplots(rows = 3, cols = 1,
                        specs = [[{}], [{"rowspan": 2}], [None]],
                        subplot_titles = ("Positive Rate", "Total Examinations"))
    # Add traces
    fig.add_trace(go.Bar(name = 'Reported_Covid19', x = exam_stats_table['Date_Reported'], 
                         y = exam_stats_table['Reported_Covid19']), row = 2, col = 1)
    fig.add_trace(go.Bar(name = 'Reported_Enhanced_Surveillance', x = exam_stats_table['Date_Reported'],
                         y = exam_stats_table['Reported_Enhanced_Surveillance']), row = 2, col = 1)
    fig.add_trace(go.Bar(name = 'Reported_Home_Quarantine', x = exam_stats_table['Date_Reported'], 
                         y = exam_stats_table['Reported_Home_Quarantine']), row = 2, col = 1)
    fig.add_trace(go.Scatter(name = 'Positive_Rate', x = exam_stats_table['Date_Reported'], 
                             y = exam_stats_table['Positive_Rate']), row = 1, col = 1)
    
    fig.update_layout(title_text = 'Daily Examinations VS Positive Rate',
                      barmode = 'stack',
                      paper_bgcolor = 'rgba(0,0,0,0)', 
                      plot_bgcolor = 'rgba(0,0,0,0)')

    # Set x-axis title
    fig.update_xaxes(title_text = "Date", row = 2, col = 1)
    # fig.update_xaxes(title_text = "Date", row = 1, col = 1)

    # Set y-axes titles
    fig.update_yaxes(title_text = "Daily Examinations", row = 2, col = 1)
    fig.update_yaxes(title_text = "Positive Rate (%)", row = 1, col = 1)


    exam_stats_plot = plot({'data': fig}, output_type='div')

    return exam_stats_plot

def daily_vacc_plotly(request, mysql_connection):
    daily_vacc_sql = "SELECT Date, Brand, First_Dose_Daily + Second_Dose_Daily AS Total_Vaccinated_Daily FROM covid19_vaccination"
    daily_vacc_table = pd.DataFrame(custom_sql(mysql_connection, daily_vacc_sql))

    plot_data = []
    for vaccines in daily_vacc_table['Brand'].unique():
        sub_df = daily_vacc_table[daily_vacc_table['Brand'] == vaccines]
        plot_data.append(go.Bar(name = vaccines, x = sub_df['Date'], y = sub_df['Total_Vaccinated_Daily']))
    
    fig = go.Figure(data = plot_data)
    # Change the bar mode
    fig.update_layout(barmode='stack', 
                      title_text = 'Daily Vaccination',
                      paper_bgcolor = 'rgba(0,0,0,0)', 
                      plot_bgcolor = 'rgba(0,0,0,0)',
                      xaxis_title = 'Date',
                      yaxis_title = 'Daily_Vaccination')
    
    daily_vacc_plot = plot({'data': fig}, output_type='div')

    return daily_vacc_plot

def vacc_brand_plotly(request, mysql_connection, brand = 'AstraZeneca'):
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
    
    vacc_brand_plot = plot({'data': fig}, output_type='div')

    return vacc_brand_plot

def total_vacc_plotly(request, mysql_connection):
    total_vacc_sql = """SELECT Brand, SUM(First_Dose_Daily) AS Total_First_Dose, 
	                                  SUM(Second_Dose_Daily) AS Total_Second_Dose
                        FROM covid19_vaccination
                        GROUP BY Brand"""
    
    total_vacc_table = pd.DataFrame(custom_sql(mysql_connection, total_vacc_sql))
    fig = go.Figure(data = [go.Bar(name = 'First_Dose', x = total_vacc_table['Brand'], y = total_vacc_table['Total_First_Dose']),
                            go.Bar(name = 'Second_Dose', x = total_vacc_table['Brand'], y = total_vacc_table['Total_Second_Dose'])])

    fig.update_layout(barmode='stack', 
                      title_text = 'Total Vacination Plot',
                      paper_bgcolor = 'rgba(0,0,0,0)', 
                      plot_bgcolor = 'rgba(0,0,0,0)',
                      xaxis_title = 'Brand',
                      yaxis_title = 'Total Vaccination')
    
    total_vacc_plot = plot({'data': fig}, output_type='div')

    return total_vacc_plot

