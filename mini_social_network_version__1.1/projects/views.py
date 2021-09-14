from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from django.core.paginator import Paginator

from django.db import models
from django.db.models import Q
from django.db.utils import IntegrityError

from django.contrib import messages

from .owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView
from .utils import visitor_cookie_handler, visitor_cookie_handler_version_1

from .models import Project, Comment, Fav
from .forms import CreateForm, CommentForm


class ProjectListView(View):
    model = Project
    template_name = "Projects/list.html"
    search_type = 'all'

    # helper method
    def search_projects(self, request, type_x):
        strval =  request.GET.get("search", False)
        project_list = Project.objects.search(strval=strval, type_x=type_x)
        return (project_list, strval)

    # helper method
    def favorite_projects(self, request):
        favorites = list()
        if request.user.is_authenticated:
            rows = request.user.profile.favorite_projects.values('id')
            # favorites = [2, 4, ...] using list comprehension
            favorites = [ row['id'] for row in rows ]
        return favorites

    def get(self, request) :
        # strval =  request.GET.get("search", False)
        # project_list = Project.objects.search(strval=strval, type_x=self.search_type)
        project_list, strval = self.search_projects(request, self.search_type)
        favorites = self.favorite_projects(request)

        paginator = Paginator(project_list, 6)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # favorites = list()
        # if request.user.is_authenticated:
        #     rows = request.user.favorite_projects.values('id')
        #     # favorites = [2, 4, ...] using list comprehension
        #     favorites = [ row['id'] for row in rows ]

        context = {
            'search': strval,
            'page_obj': page_obj,
            'favorites': favorites,
            'ctx_msg': 'there are no projects',
            }
        return render(request, self.template_name, context)


class FavProjectListView(ProjectListView):
    search_type = 'fav'


class MostProjectListView(ProjectListView):
    search_type = 'view'


class ProjectDetailView(View):
    model = Project
    template_name = "Projects/detail.html"

    def get(self, request, slug) :
        project = get_object_or_404(Project, slug=slug)
        comment_form = CommentForm()

        # Call the helper function to handle the cookies
        visitor_cookie_handler(request, project)

        context = {'project' : project, 'comment_form': comment_form}
        return render(request, self.template_name, context)


class ProjectCreateView(LoginRequiredMixin, View):
    template_name = 'Projects/form.html'
    success_url = reverse_lazy('nsusers:myaccount')

    def get(self, request, pk=None):
        form = CreateForm()
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, pk=None):
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            context = {'form': form}
            return render(request, self.template_name, context)

        pic = form.save(commit=False)
        pic.owner = self.request.user.profile
        pic.save()

        messages.add_message(request, messages.SUCCESS, 'Data saved.')

        return redirect(self.success_url)


class ProjectUpdateView(LoginRequiredMixin, View):
    template_name = 'Projects/form.html'
    success_url = reverse_lazy('nsusers:myaccount')

    def get(self, request, slug):
        project = get_object_or_404(Project, slug=slug, owner=self.request.user.profile)
        form = CreateForm(instance=project)
        context = {'form': form, 'project': project}
        return render(request, self.template_name, context)

    def post(self, request, slug=None):
        project = get_object_or_404(Project, slug=slug, owner=self.request.user.profile)
        form = CreateForm(request.POST, request.FILES or None, instance=project)

        if not form.is_valid():
            context = {'form': form, 'project': project}
            return render(request, self.template_name, context)

        pic = form.save(commit=False)
        pic.save()

        messages.add_message(request, messages.SUCCESS, 'Data updated.')

        return redirect(self.success_url)


class ProjectDeleteView(OwnerDeleteView):
    model = Project
    template_name = "Projects/delete.html"
    success_url=reverse_lazy('nsusers:myaccount')


def stream_file(request, pk):
    project = get_object_or_404(Project, id=pk)
    response = HttpResponse()
    response['Content-Type'] = project.content_type
    response['Content-Length'] = len(project.picture)
    response.write(project.picture)
    return response


class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        project = get_object_or_404(Project, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user.profile, project=project)
        comment.save()
        return redirect(reverse('nsprojects:project_detail', args=[project.slug]))


class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "projects/delete.html"
    success_url=reverse_lazy('nsprojects:all')

    def get_success_url(self):
        project = self.object.project
        return reverse('nsprojects:project_detail', args=[project.slug])


@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        t = get_object_or_404(Project, id=pk)
        fav = Fav(owner=request.user.profile, project=t)
        try:
            fav.save()  # In case of duplicate key
            t.fav_rate = t.fav_rate + 1
            t.save()
        except IntegrityError as e:
            pass
        
        return HttpResponse()


@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        t = get_object_or_404(Project, id=pk)
        try:
            fav = Fav.objects.get(owner=request.user.profile, project=t).delete()
            t.fav_rate = t.fav_rate - 1
            t.save()
        except Fav.DoesNotExist as e:
            pass

        return HttpResponse()
