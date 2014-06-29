from django.core.urlresolvers import reverse

def login_redirect(self, field):
	return reverse('dashboard')
