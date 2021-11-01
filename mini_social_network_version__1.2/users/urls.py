from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('', views.ProfileListView.as_view(), name='home'),

    path('profile/<slug:username>/', views.UserProfile.as_view(), name='profile'),

    path('myaccount/', views.MyAccount.as_view(), name="myaccount"),
    path('edit_account/', views.EditAccount.as_view(), name="edit_account"),

    path('create_skill/', views.CreateSkill.as_view(), name="create_skill"),
    path('update_skill/<str:pk>/', views.UpdateSkill.as_view(), name="update_skill"),
    path('delete_skill/<str:pk>/', views.DeleteSkill.as_view(), name="delete_skill"),
]