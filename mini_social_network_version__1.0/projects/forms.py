from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile
from .models import Project
from .humanize import naturalsize

class CreateForm(forms.ModelForm):
    max_upload_limit = 2 * 1024 * 1024
    max_upload_limit_text = naturalsize(max_upload_limit)

    picture = forms.FileField(required=False, label='File to Upload <= '+max_upload_limit_text)
    upload_field_name = 'picture'

    class Meta:
        model = Project
        fields = ['title', 'text',  'source_code', 'picture']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input input--text', 'placeholder': 'enter title ..'}),
            'text': forms.Textarea(attrs={'class': 'input input--text', 'rows': '6', 'placeholder': 'enter text ..'}),
            'source_code': forms.TextInput(attrs={'class': 'input input--text', 'placeholder': 'enter source code ..'}),
            
        }

    # Validate the size of the picture
    def clean(self):
        cleaned_data = super().clean()
        pic = cleaned_data.get('picture')
        if pic is None:
            return
        if len(pic) > self.max_upload_limit:
            self.add_error('picture', "File must be < "+self.max_upload_limit_text+" bytes")
            
    # Convert uploaded File object to a picture
    def save(self, commit=True):
        instance = super(CreateForm, self).save(commit=False)

        # We only need to adjust picture if it is a freshly uploaded file
        f = instance.picture   # Make a copy
        if isinstance(f, InMemoryUploadedFile):  # Extract data from the form to the model
            bytearr = f.read()
            instance.content_type = f.content_type
            instance.picture = bytearr  # Overwrite with the actual image data

        if commit:
            instance.save()

        return instance

class CommentForm(forms.Form):
    comment = forms.CharField(
        required=True,
        max_length=500,
        min_length=3,
        strip=True,
        widget=forms.Textarea(attrs={
            'class': 'input input--textarea',
            'id': 'formInput#textarea',
            'name': 'comment',
            'placeholder': 'Write your comments here...',
            'rows': '5'
            })
        )
