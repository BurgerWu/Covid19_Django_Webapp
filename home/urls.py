#import libraries
from django.urls import path, include
from . import views
from .Dash_Apps import county_plot, imported_plot, vacc_plot

#Create URL patterns
urlpatterns = [
    path('', views.index, name = 'index'),
    path('submit',views.FeedBackSubmitView, name = 'submit_feedback'),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),]

