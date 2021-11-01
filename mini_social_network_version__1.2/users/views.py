from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib import messages
from django.db.models import Q

from .models import Profile, Skill
from .forms import UserProfileForm, SkillForm

from projects.models import Project


from django.views import generic


class ProfileListView(generic.ListView):
    model = Profile
    template_name = "users/index.html"
    context_object_name = 'page_obj'
    paginate_by = 6

    def get_queryset(self):
        strval =  self.request.GET.get("search", False)
        if strval:
            query = Q(user__username__icontains=strval)
            query.add(Q(bio__icontains=strval), Q.OR)
            query.add(Q(skill__name__icontains=strval), Q.OR)

            profile_list = Profile.objects.distinct().filter(query).select_related().order_by('-created_at')
        else:
            profile_list = Profile.objects.all().order_by('-created_at')

        return profile_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        strval =  self.request.GET.get("search", False)
        context["search"] = strval
        context["ctx_msg"] = 'there are no profiles with the input search'
        
        return context
    

class UserProfile(generic.DetailView):
    model = Profile
    template_name = 'users/user_profile.html'
    context_object_name = 'profile'
    
    def get_object(self):
        kwargs_args = self.kwargs['username']
        obj = get_object_or_404(Profile, user__username=kwargs_args)
        return obj


class MyAccount(LoginRequiredMixin, generic.DetailView):
    template_name = 'users/user_profile.html'
    context_object_name = 'profile'
    
    def get_object(self):
        kwargs_args = self.request.user
        obj = get_object_or_404(Profile, user=kwargs_args)
        return obj


class EditAccount(LoginRequiredMixin, generic.UpdateView):
    model = Profile
    form_class = UserProfileForm
    template_name = 'users/form.html'
    success_url = reverse_lazy('nsusers:myaccount')

    def get_object(self):
        return self.request.user.profile


class CreateSkill(LoginRequiredMixin, generic.CreateView):
    form_class = SkillForm
    template_name = 'users/form.html'
    success_url = reverse_lazy('nsusers:myaccount')

    def form_valid(self, form):
        profile = self.request.user.profile
        skill = form.save(commit=False)
        skill.owner = profile
        skill.save()
        return super(CreateSkill, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Skill was added successfully!')
        return super().get_success_url()


class UpdateSkill(LoginRequiredMixin, generic.UpdateView):
    form_class = SkillForm
    template_name = 'users/form.html'
    success_url = reverse_lazy('nsusers:myaccount')

    def get_object(self):
        profile = self.request.user.profile
        return get_object_or_404(profile.skill_set, id=self.kwargs['pk'])
    
    def get_success_url(self):
        messages.success(self.request, 'Skill was updated successfully!')
        return super().get_success_url()


class DeleteSkill(LoginRequiredMixin, generic.DeleteView):
    template_name = 'users/delete.html'
    success_url = reverse_lazy('nsusers:myaccount')

    def get_object(self):
        profile = self.request.user.profile
        return get_object_or_404(profile.skill_set, id=self.kwargs['pk'])

    def get_success_url(self):
        messages.success(self.request, 'Skill was deleted successfully!')
        return super().get_success_url()

