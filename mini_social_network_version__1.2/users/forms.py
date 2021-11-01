from django import forms
from .models import Profile, Skill


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('short_intro', 'bio', 'profile_image', 'social_github', 'social_linkedin')
        widgets = {
            'short_intro': forms.TextInput(attrs={'class': 'input input--text', 'placeholder': 'enter short_intro ..'}),
            'bio': forms.Textarea(attrs={
            'class': 'input input--textarea',
            'id': 'formInput#textarea',
            'name': 'comment',
            'placeholder': 'enter bio ...',
            'rows': '5'
            }),
            'social_github': forms.TextInput(attrs={'class': 'input input--text', 'placeholder': 'ex. GitHub.com/username ..'}),
            'social_linkedin': forms.TextInput(attrs={'class': 'input input--text', 'placeholder': 'ex. linkedin.com/in/username ..'}),
            
        }

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input input--text', 'palceholder': 'enter skill ..'}),
            
        }