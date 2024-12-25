from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Author, Post
from ckeditor.widgets import CKEditorWidget
from ckeditor.fields import RichTextField

class AuthorSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class AuthorNameForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['authorname']

    def clean_authorname(self):
        authorname = self.cleaned_data['authorname']
        if Author.objects.filter(authorname=authorname).exists():
            raise forms.ValidationError("This author name is already taken. Please choose another one.")
        return authorname


class PostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget(config_name='default',attrs={'id': 'content'}))  # Use CKEditorWidget for content

    class Meta:
        model = Post
        fields = ['title', 'content', 'image']
