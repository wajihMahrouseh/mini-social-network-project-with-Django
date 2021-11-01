from django.contrib import admin
from django.urls import path, include, reverse
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', include('users.urls', namespace='nsusers')),
    path('accounts/', include('registration.backends.simple.urls')),
    path('admin/', admin.site.urls),
    path('chat/', include('chat.urls', namespace='nschat')),
    path('projects/', include('projects.urls', namespace='nsprojects')),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
