from django.contrib import admin
from .models import Project, Comment, Fav

class ProjectAdmin(admin.ModelAdmin):
    exclude = ('picture', 'content_type')
    prepopulated_fields = {'slug':('title',)}


admin.site.register(Project, ProjectAdmin)
admin.site.register(Comment)
admin.site.register(Fav)