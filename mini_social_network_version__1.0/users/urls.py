from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('', views.profile_list_view, name='home'),

    path('profile/<slug:username>/', views.userProfile, name='profile'),

    path('myaccount/', views.userAccount, name="myaccount"),
    path('edit_account/', views.editAccount, name="edit_account"),

    path('create_skill/', views.createSkill, name="create_skill"),
    path('update_skill/<str:pk>/', views.updateSkill, name="update_skill"),
    path('delete_skill/<str:pk>/', views.deleteSkill, name="delete_skill"),
]
