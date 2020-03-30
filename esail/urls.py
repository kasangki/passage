from django.urls import path
from esail import views


app_name = 'esail'
urlpatterns = [
    path('', views.index, name='index'),      # /esail/
    #path('passage/', views.passage, name='passage'),  # /passage/
    path('passage/<int:passage_id>/', views.passage, name='passage'),  # /passage/
]
