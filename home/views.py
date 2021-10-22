from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.db import connections
from django.contrib import messages
from django.urls import reverse
import pandas as pd
import pymysql.cursors
from plotly.offline import plot
import plotly.graph_objs as go
from datetime import datetime
from .utils import *
from .forms import *
from .models import FeedBack
from .Dash_Apps import county_plot, imported_plot, vacc_plot
import time
# Create your views here.

def index(request):
    """View function for home page of site."""
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits+1
    
    mysql_connection = pymysql.connect(host="127.0.0.1",user='root',password='password',db='airflow',cursorclass=pymysql.cursors.DictCursor)

    total_cases_sql = "SELECT sum(Number_of_Confirmed_Cases) as total_cases FROM covid19_cases"
    total_cases = custom_sql(connections['airflow'], total_cases_sql)[0][0]

    total_vaccincation_sql = "SELECT sum(Total_Vaccinated_Daily) FROM covid19_vaccination"
    total_vaccination = custom_sql(connections['airflow'], total_vaccincation_sql)[0][0]
 
    county_options_sql = "SELECT DISTINCT(County_Living) FROM covid19_cases"
    county_options = custom_sql(mysql_connection, county_options_sql)
    county_options = [ x['County_Living'] for x in county_options ]

    daily_case_plot = daily_cases_plotly(request, mysql_connection, 'All')
    daily_county_plot = daily_county_plotly(request, mysql_connection, 'Taipei City')
    daily_gender_plot = daily_gender_plotly(request, mysql_connection)
    total_age_plot = total_age_plotly(request, mysql_connection)
    exam_stats_plot = exam_stats_plotly(request, mysql_connection)
    daily_vacc_plot = daily_vacc_plotly(request, mysql_connection)
    vacc_brand_plot = vacc_brand_plotly(request, mysql_connection, 'AstraZeneca')
    total_vacc_plot = total_vacc_plotly(request, mysql_connection)

    # form = FeedBackForm(initial = {'Date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    form = FeedBackForm()

    context = {'total_case': total_cases,
               'total_vaccination': total_vaccination,
               'county_options': county_options,
               'daily_case_plot': daily_case_plot,
               'daily_county_plot': daily_county_plot,
               'daily_gender_plot': daily_gender_plot,
               'total_age_plot': total_age_plot,
               'exam_stats_plot': exam_stats_plot,
               'daily_vacc_plot': daily_vacc_plot,
               'vacc_brand_plot': vacc_brand_plot,
               'total_vacc_plot': total_vacc_plot,
               'form': form}
        

    # Render the HTML template index.html with the data in the context variable.
    return render(
        request,
        'index.html',
        context= context)


def FeedBackSubmitView(request):
 
    if request.method == 'POST':
        form = FeedBackForm(request.POST)
        if form.is_valid():            
            instance = form.save(commit=False)
            instance.Date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            instance.save()
            messages.success(request, 'Feedback submitted successfully.')
        else:
            messages.error(request, form.errors)
    #time.sleep(3)
    return HttpResponseRedirect(reverse('index'))
       


