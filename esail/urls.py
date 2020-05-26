from django.urls import path
from esail import views


app_name = 'esail'
urlpatterns = [
    path('', views.index, name='index'),      # /esail/
    path('passage/<int:passage_id>/', views.passage, name='passage'),  # /passage/
    path('passageAll/', views.passageAll, name='passageAll'),  # /passageAll/
    path('passage/<slug:start_port_code>/<slug:dest_port_code>/', views.passage, name='passage'),  # /passage/
    path('port_code/<slug:start_code>/',views.port_code,name='start_code'), #/port_code/
]
