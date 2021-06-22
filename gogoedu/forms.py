from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from gogoedu.models import myUser
from django.utils.translation import gettext as _


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=255, required=True)
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        # help_text=password_validation.password_validators_help_text_html(),
    )

    class Meta:
        model = myUser
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]

    def clean(self):
        email = self.cleaned_data.get('email')
        if myUser.objects.filter(email=email):
            raise forms.ValidationError(_("Email existed. Please try again"))
        return self.cleaned_data


class UserUpdateForm(UserChangeForm):
    class Meta:
        model = myUser
        fields = ["first_name", "last_name",  "avatar"]
        exclude = ['user']
