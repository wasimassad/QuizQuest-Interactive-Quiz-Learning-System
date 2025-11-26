from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Question


class UserRegistrationForm(UserCreationForm):
    """Form for user registration."""
    email = forms.EmailField(required=True)
    profile_picture = forms.ImageField(required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'profile_picture']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'profile_picture':
                field.widget.attrs['class'] = 'form-control-file'


class UserLoginForm(AuthenticationForm):
    """Form for user login."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['class'] = 'form-control'


class QuestionForm(forms.ModelForm):
    """Form for creating and updating questions."""
    class Meta:
        model = Question
        fields = [
            'title', 'content', 'option_a', 'option_b',
            'option_c', 'option_d', 'correct_answer',
            'difficulty', 'category', 'image'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'image':
                field.widget.attrs['class'] = 'form-control-file'
            elif field_name in ['content']:
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['rows'] = 4
            elif field_name in ['correct_answer', 'difficulty']:
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'
