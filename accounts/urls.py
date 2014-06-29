from accounts.forms import AuthenticationFormExtra, ChangeEmailFormExtra, EditProfileFormExtra, PasswordChangeFormExtra, SignupFormExtra
from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView
from wqinterfaz import views
from userena import views as userena_views
from accounts import lib as accounts_lib

urlpatterns = patterns('',
	url(r'^signin/$', userena_views.signin, {'auth_form': AuthenticationFormExtra, 'template_name': 'signin_form.html', 'redirect_field_name': 'prueba', 'redirect_signin_function': accounts_lib.login_redirect}, name='userena_signin'),
	url(r'^signup/$', userena_views.signup, {'signup_form': SignupFormExtra, 'template_name': 'signup_form.html'}, name='userena_signup'),

#	url(r'^(?P<username>[\.\w-]+)/password/$', userena_views.password_change, {'pass_form': PasswordChangeFormExtra, 'template_name': 'accounts/password_form.html'}, name='userena_password_change'),

#	url(r'^(?P<username>[\.\w-]+)/edit/$', userena_views.profile_edit, {'edit_profile_form': EditProfileFormExtra, 'template_name': 'accounts/profile_form.html'}, name='userena_profile_edit'),
#	url(r'^(?P<username>(?!signout|signup|signin)[\.\w-]+)/$', userena_views.profile_detail, {'template_name': 'accounts/profile_detail.html'}, name='userena_profile_detail'),

#	url(r'^(?P<username>[\.\w-]+)/email/$', userena_views.email_change, {'email_form': ChangeEmailFormExtra, 'template_name': 'accounts/email_form.html'}, name='userena_email_change'),

	url(r'^', include('userena.urls')),
)
