from django.views import View
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.paginator import Paginator

from django.contrib.auth.models import User

from django.contrib import messages
from django.db.models import Q

from .models import Profile, Skill
from .forms import UserProfileForm, SkillForm

from projects.models import Project


class ProfileListView(View):
    template_name = "users/index.html"

    def get(self, request):
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
        return render(request, self.template_name, context)
    

class UserProfile(View):
    template_name = 'users/user_profile.html'

    def get(self, request, username):
        profile = get_object_or_404(Profile, user__username=username)
        context = {'profile': profile}
        return render(request, self.template_name, context)


class UserAccount(LoginRequiredMixin, View):
    template_name = 'users/user_profile.html'

    def get(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        context = {'profile': profile}
        return render(request, self.template_name, context)


class EditAccount(LoginRequiredMixin, View):
    template_name = 'users/form.html'
    success_url = reverse_lazy('nsusers:myaccount')

    def get(self, request):
        profile = request.user.profile
        form = UserProfileForm(instance=profile)
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request):
        profile = request.user.profile
        form = UserProfileForm(request.POST, request.FILES or None, instance=profile)

        if not form.is_valid():
            context = {'form': form}
            return render(request, self.template_name, context)

        pic = form.save(commit=False)
        pic.save()

        return redirect(self.success_url)


class CreateSkill(LoginRequiredMixin, View):
    template_name = 'users/form.html'
    success_url = reverse_lazy('nsusers:myaccount')
    
    def get(self, request):
        form = SkillForm()
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request):
        profile = request.user.profile
        form = SkillForm(request.POST)

        if not form.is_valid():
            context = {'form': form}
            return render(request, self.template_name, context)
        
        skill = form.save(commit=False)
        skill.owner = profile
        skill.save()

        messages.success(request, 'Skill was added successfully!')

        return redirect(self.success_url)


class UpdateSkill(LoginRequiredMixin, View):
    template_name = 'users/form.html'
    success_url = reverse_lazy('nsusers:myaccount')
    
    def get(self, request, pk=None):
        profile = request.user.profile
        skill = get_object_or_404(profile.skill_set, id=pk)
        form = SkillForm(instance=skill)
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, pk=None):
        profile = request.user.profile
        skill = get_object_or_404(profile.skill_set, id=pk)
        form = SkillForm(request.POST, instance=skill)

        if not form.is_valid():
            context = {'form': form}
            return render(request, self.template_name, context)
        
        form.save()

        messages.success(request, 'Skill was added successfully!')

        return redirect(self.success_url)


class DeleteSkill(LoginRequiredMixin, View):
    template_name = 'users/delete.html'
    success_url = reverse_lazy('nsusers:myaccount')
    
    def get(self, request, pk=None):
        profile = request.user.profile
        skill = get_object_or_404(profile.skill_set, id=pk)
        context = {'object': skill}
        return render(request, self.template_name, context)

    def post(self, request, pk=None):
        profile = request.user.profile
        skill = get_object_or_404(profile.skill_set, id=pk)
        skill.delete()

        messages.success(request, 'Skill was deleted successfully!')

        return redirect(self.success_url)
