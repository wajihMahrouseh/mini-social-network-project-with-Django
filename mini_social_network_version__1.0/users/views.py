from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404

from django.core.paginator import Paginator

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.db.models import Q

from .models import Profile, Skill
from .forms import UserProfileForm, SkillForm

from projects.models import Project


def profile_list_view(request):
    strval =  request.GET.get("search", False)
    if strval:
        query = Q(user__username__icontains=strval)
        query.add(Q(bio__icontains=strval), Q.OR)
        query.add(Q(skill__name__icontains=strval), Q.OR)

        profile_list = Profile.objects.distinct().filter(query).select_related().order_by('-created_at')
    else:
        profile_list = Profile.objects.all().order_by('-created_at')

    paginator = Paginator(profile_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'search': strval,
        'page_obj': page_obj,
        'ctx_msg': 'there are no profiles with the input search',
        }
    return render(request, "users/index.html", context)


def userProfile(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    context = {'profile': profile,}
    return render(request, 'users/user_profile.html', context)


@login_required
def userAccount(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    context = {'profile': profile}
    return render(request, 'users/user_profile.html', context)


@login_required
def editAccount(request):
    profile = request.user.profile
    form = UserProfileForm(instance=profile)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES or None, instance=profile)

        if form.is_valid():
            form.save()

            return redirect(reverse('nsusers:myaccount'))

    context = {'form': form}
    return render(request, 'users/form.html', context)


@login_required
def createSkill(request):
    profile = request.user.profile
    form = SkillForm()

    if request.method == 'POST':
        form = SkillForm(request.POST)

        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = profile
            skill.save()

            messages.success(request, 'Skill was added successfully!')

            return redirect(reverse('nsusers:myaccount'))

    context = {'form': form}
    return render(request, 'users/form.html', context)


@login_required
def updateSkill(request, pk):
    profile = request.user.profile
    skill = get_object_or_404(profile.skill_set, id=pk)
    form = SkillForm(instance=skill)

    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)

        if form.is_valid():
            form.save()

            messages.success(request, 'Skill was updated successfully!')

            return redirect(reverse('nsusers:myaccount'))

    context = {'form': form}
    return render(request, 'users/form.html', context)


@login_required
def deleteSkill(request, pk):
    profile = request.user.profile
    skill = get_object_or_404(profile.skill_set, id=pk)

    if request.method == 'POST':
        skill.delete()

        messages.success(request, 'Skill was deleted successfully!')

        return redirect(reverse('nsusers:myaccount'))

    context = {'object': skill}
    return render(request, 'users/delete.html', context)
