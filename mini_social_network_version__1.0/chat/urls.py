from django.urls import path

from . import views

app_name='chat'
urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('messages/', views.talk_message, name='messages'),
    path('talk/<slug:slug>/', views.talk_main, name='talk'),
    path('view_message/', views.viewMessage, name='view_message'),

]
