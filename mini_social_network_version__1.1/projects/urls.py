from django.urls import path, reverse_lazy
from django.views.generic import TemplateView

from . import views

app_name = 'projects'

urlpatterns = [
    path('projects_list/', views.ProjectListView.as_view(), name='all'),
    path('most_favorite_projects/', views.FavProjectListView.as_view(), name='most_favorite_projects'),
    path('most_viewed_projects/', views.MostProjectListView.as_view(), name='most_viewed_projects'),

    path('project/<slug:slug>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('project_create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('project/<slug:slug>/update/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('project/<slug:slug>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
    path('project_picture/<int:pk>/', views.stream_file, name='project_picture'),

    path('comment/<int:pk>/create/', views.CommentCreateView.as_view(), name='project_comment_create'),
    path('comment/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='project_comment_delete'),

    path('project/<int:pk>/favorite/', views.AddFavoriteView.as_view(), name='project_favorite'),
    path('project/<int:pk>/unfavorite/', views.DeleteFavoriteView.as_view(), name='project_unfavorite'),
    
]
