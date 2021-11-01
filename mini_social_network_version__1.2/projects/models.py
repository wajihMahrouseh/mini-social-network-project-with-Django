from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save

from django.core.validators import MinLengthValidator

from users.models import Profile

from .utils import unique_slug_generator


class ProjectQuerySet(models.QuerySet):
    def search(self, strval=None, type_x=None):
        if strval:
            query = Q(title__icontains=strval)
            query.add(Q(text__icontains=strval), Q.OR)
            query.add(Q(owner__user__username__icontains=strval), Q.OR)
            return self.filter(query).select_related().order_by('-created_at')
        elif 'all' == type_x:
            return self.all().order_by('-created_at')
        elif 'fav' == type_x:
            return self.filter(fav_rate__gt=0).order_by('-fav_rate')[:18]
        elif 'view' == type_x:
            return self.filter(views__gt=0).order_by('-views')[:18]

class ProjectManager(models.Manager):
    def get_queryset(self):
        return ProjectQuerySet(self.model, using=self._db)

    def search(self, strval=None, type_x=None):
        return self.get_queryset().search(strval=strval, type_x=type_x)

class Project(models.Model):
    title = models.CharField(
            max_length=200,
            validators=[MinLengthValidator(2, "Title must be greater than 2 characters")]
    )
    text = models.TextField()
    owner = models.ForeignKey(Profile,
        on_delete=models.CASCADE, related_name='projects_owned')
    comments = models.ManyToManyField(Profile,
        through='Comment', related_name='project_comments')
    favorites = models.ManyToManyField(Profile,
        through='Fav', related_name='favorite_projects')

    # Picture
    picture = models.BinaryField(null=True, blank=True, editable=True)
    content_type = models.CharField(max_length=256, null=True, blank=True,
                                    help_text='The MIMEType of the file')

    slug = models.SlugField(unique=True, blank=True)
    views = models.PositiveIntegerField(default=0, blank=True)
    fav_rate = models.PositiveIntegerField(default=0, blank=True)
    source_code = models.URLField(max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProjectManager()

    def __str__(self):
        return self.title

def project_pre_save(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(project_pre_save, sender=Project)

class Comment(models.Model):
    text = models.TextField(
        validators=[MinLengthValidator(3, "Comment must be greater than 3 characters")]
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if len(self.text) < 15 : return self.text
        return self.text[:11] + ' ...'


class Fav(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE,
        related_name='favs_users')

    class Meta:
        unique_together = ('project', 'owner')

    def __str__(self):
        if len(self.project.title) <= 32: return f"{self.owner.user.username} likes {self.project.title[:32]}"
        return f"{self.owner.user.username} likes {self.project.title[:32]} ..."
