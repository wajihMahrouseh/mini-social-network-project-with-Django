from django.urls import path, reverse_lazy
from django.views.generic import TemplateView

from . import views

app_name = 'projects'

urlpatterns = [
    path('projects_list/', views.project_list_view, name='all'),
    path('most_favorite_projects/', views.fav_project_list_view, name='most_favorite_projects'),
    path('most_viewed_projects/', views.most_project_list_view, name='most_viewed_projects'),

    path('project/<slug:slug>/', views.project_detail_view, name='project_detail'),
    path('project_create/', views.project_create_view, name='project_create'),
    path('project/<slug:slug>/update/', views.project_update_view, name='project_update'),
    path('project/<slug:slug>/delete/', views.project_delete_view, name='project_delete'),
    path('project_picture/<int:pk>/', views.stream_file, name='project_picture'),

    path('comment/<int:pk>/create/', views.comment_create_view, name='project_comment_create'),
    path('comment/<int:pk>/delete/', views.comment_delete_view, name='project_comment_delete'),

    path('project/<int:pk>/favorite/', views.AddFavoriteView.as_view(), name='project_favorite'),
    path('project/<int:pk>/unfavorite/', views.DeleteFavoriteView.as_view(), name='project_unfavorite'),
    
]
