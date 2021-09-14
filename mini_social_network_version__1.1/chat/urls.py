from django.urls import path

from . import views

app_name='chat'
urlpatterns = [
    path('inbox/', views.Inbox.as_view(), name='inbox'),
    path('messages/', views.TalkMessages.as_view(), name='messages'),
    path('talk/<slug:slug>/', views.TalkMain.as_view(), name='talk'),
    path('view_message/', views.ViewMessage.as_view(), name='view_message'),

]
