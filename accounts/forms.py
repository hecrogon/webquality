from accounts.models import UserProfile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import Group
from userena.forms import ChangeEmailForm, EditProfileForm, AuthenticationForm, SignupForm

class ChangeEmailFormExtra(ChangeEmailForm):
	def __init__(self, *args, **kwargs):
		super(ChangeEmailFormExtra, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_class = 'well form-inline'
		self.helper.add_input(Submit('submit', 'Submit'))

class EditProfileFormExtra(EditProfileForm):
	def __init__(self, *args, **kwargs):
		super(EditProfileFormExtra, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_class = 'well form-inline'
		self.helper.add_input(Submit('submit', 'Submit'))

class PasswordChangeFormExtra(PasswordChangeForm):
	def __init__(self, *args, **kwargs):
		super(PasswordChangeFormExtra, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_class = 'well form-inline'
		self.helper.add_input(Submit('submit', 'Submit'))

class AuthenticationFormExtra(AuthenticationForm):
	def __init__(self, *args, **kwargs):
		super(AuthenticationFormExtra, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_class = 'form-horizontal'
		self.helper.add_input(Submit('submit', 'Submit'))

class SignupFormExtra(SignupForm):
	def __init__(self, *args, **kwargs):
		super(SignupFormExtra, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_class = 'form-horizontal'
		self.helper.add_input(Submit('submit', 'Submit'))

	def save(self):
		user = super(SignupFormExtra, self).save()
		
		user_profile = user.get_profile()
		group = self.cleaned_data['group']
		user.groups.add(Group.objects.get(name=group))
		user_profile.save()

		return user

