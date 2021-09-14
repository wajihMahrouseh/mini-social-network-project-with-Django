from django.http import HttpResponse
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from django.core.paginator import Paginator

from django.db.utils import IntegrityError

from django.contrib import messages

from .utils import visitor_cookie_handler, visitor_cookie_handler_version_1

from .models import Project, Comment, Fav
from .forms import CreateForm, CommentForm

# helper function
def search_projects(request, type_x):
    strval =  request.GET.get("search", False)
    return (Project.objects.search(strval=strval, type_x=type_x), strval)

# helper function
def favorite_projects(request):
    favorites = list()
    if request.user.is_authenticated:
        rows = request.user.profile.favorite_projects.values('id')
        # favorites = [2, 4, ...] using list comprehension
        favorites = [ row['id'] for row in rows ]
    return favorites

def project_list_view(request):
    project_list, strval = search_projects(request, 'all')
    favorites = favorite_projects(request)

    paginator = Paginator(project_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'search': strval,
        'page_obj': page_obj,
        'favorites': favorites,
        'ctx_msg': 'there are no projects',
        }
    return render(request, "Projects/list.html", context)


def fav_project_list_view(request):
    project_list, strval = search_projects(request, 'fav')
    favorites = favorite_projects(request)

    paginator = Paginator(project_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'search': strval,
        'page_obj': page_obj,
        'favorites': favorites,
        'ctx_msg': 'there are no projects',
        }
    return render(request, "Projects/list.html", context)


def most_project_list_view(request):
    project_list, strval = search_projects(request, 'view')
    favorites = favorite_projects(request)

    paginator = Paginator(project_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'search': strval,
        'page_obj': page_obj,
        'favorites': favorites,
        'ctx_msg': 'there are no projects',
        }
    return render(request, "Projects/list.html", context)


def project_detail_view(request, slug):
    project = get_object_or_404(Project, slug=slug)
    comment_form = CommentForm()

    # Call the helper function to handle the cookies
    visitor_cookie_handler(request, project)

    context = {'project' : project, 'comment_form': comment_form}
    return render(request, "Projects/detail.html", context)

@login_required
def project_create_view(request):
    form = CreateForm()

    if request.method == 'POST':
        form = CreateForm(request.POST, request.FILES or None)

        if form.is_valid():
            proj = form.save(commit=False)
            proj.owner = request.user.profile
            proj.save()

            messages.add_message(request, messages.SUCCESS, 'Data saved.')

            return redirect(reverse('nsusers:myaccount'))

    context = {'form': form}
    return render(request, 'Projects/form.html', context)

@login_required
def project_update_view(request, slug):
    project = get_object_or_404(Project, slug=slug, owner=request.user.profile)
    form = CreateForm(instance=project)

    if request.method == 'POST':
        form = CreateForm(request.POST, request.FILES or None, instance=project)
        
        if form.is_valid():
            pic = form.save(commit=False)
            pic.save()

            messages.add_message(request, messages.SUCCESS, 'Data updated.')
            return redirect(reverse('nsusers:myaccount'))

    context = {'form': form, 'project': project}
    return render(request, "Projects/form.html", context)

@login_required
def project_delete_view(request, slug):
    project = get_object_or_404(Project, slug=slug, owner=request.user.profile)

    if request.method == 'POST':
        project.delete()
        messages.add_message(request, messages.SUCCESS, 'Data deleted.')
        return redirect(reverse('nsusers:myaccount'))

    context = {'project': project}
    return render(request, "Projects/delete.html", context)


def stream_file(request, pk):
    project = get_object_or_404(Project, id=pk)
    response = HttpResponse()
    response['Content-Type'] = project.content_type
    response['Content-Length'] = len(project.picture)
    response.write(project.picture)
    return response

@login_required
def comment_create_view(request, pk):
    if request.method == 'POST':
        project = get_object_or_404(Project, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user.profile, project=project)
        comment.save()
        return redirect(reverse('nsprojects:project_detail', args=[project.slug]))

@login_required
def comment_delete_view(request, pk):
    comment = get_object_or_404(Comment, id=pk)
    project = comment.project.slug

    if request.method == 'POST':
        comment.delete()
        return redirect(reverse('nsprojects:project_detail', args=[project]))

    context = {'object': Comment}
    return render(request, "Projects/delete.html", context)


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
