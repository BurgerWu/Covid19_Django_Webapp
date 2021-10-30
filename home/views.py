#import libraries
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
from .db_connections import mysql_connect
from .utils import *
from .forms import *
from .models import FeedBack
from .Dash_Apps import county_plot, imported_plot, vacc_plot
import time


def index(request):
    """View function for home page of site."""
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits+1
    
    #Build Mysql connection for later use
    mysql_connection = mysql_connect.conn

    #Return total covid19 cases statistics
    total_cases_sql = "SELECT sum(Number_of_Confirmed_Cases) as total_cases FROM covid19_cases"
    total_cases = custom_sql(connections['airflow'], total_cases_sql)[0][0]

    #Return total vaccination statistics
    total_vaccincation_sql = "SELECT sum(First_Dose_Daily + Second_Dose_Daily) FROM covid19_vaccination"
    total_vaccination = custom_sql(connections['airflow'], total_vaccincation_sql)[0][0]
 
    #Return options for different counties
    county_options_sql = "SELECT DISTINCT(County_Living) FROM covid19_cases"
    county_options = custom_sql(mysql_connection, county_options_sql)
    county_options = [ x['County_Living'] for x in county_options ]

    #Plotly visualizations
    daily_gender_plot = daily_gender_plotly(mysql_connection)
    total_age_plot = total_age_plotly(mysql_connection)
    exam_stats_plot = exam_stats_plotly(mysql_connection)
    daily_vacc_plot = daily_vacc_plotly(mysql_connection)
    total_vacc_plot = total_vacc_plotly(mysql_connection)

    #Create form for web page
    form = FeedBackForm()

    #Return context to home page view
    context = {'total_case': total_cases,
               'total_vaccination': total_vaccination,
               'daily_gender_plot': daily_gender_plot,
               'total_age_plot': total_age_plot,
               'exam_stats_plot': exam_stats_plot,
               'daily_vacc_plot': daily_vacc_plot,
               'total_vacc_plot': total_vacc_plot,
               'form': form}
        

    # Render the HTML template index.html with the data in the context variable.
    return render(
        request,
        'index.html',
        context= context)


def FeedBackSubmitView(request):
    """View initiated when user submits feedback"""
    
    #Check if request is POST type, that is, sending form data back
    if request.method == 'POST':

        #Read the sent back form 
        form = FeedBackForm(request.POST)

        #Check validity
        if form.is_valid():            
            instance = form.save(commit=False)

            #Add date to the form then save to database
            instance.Date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            instance.save()

            #Append success message to messages
            messages.success(request, 'Feedback submitted successfully.')
        else:
            #Append error message to messages
            messages.error(request, form.errors)

    #After writing into database, redirect to home page
    return HttpResponseRedirect(reverse('index'))
       


