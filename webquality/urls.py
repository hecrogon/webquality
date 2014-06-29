from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/wqinterfaz/run_test/(?P<website_id>\d+)/$', 'wqinterfaz.admin_views.run_test'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt'), {'mimetype': 'text/plain'}),
    url(r'^sitemap\.xml$', TemplateView.as_view(template_name='sitemap.xml'), {'mimetype': 'application/xml'}),
)

urlpatterns += i18n_patterns('',
    url(r'^$', RedirectView.as_view(url='site/')),
    url(r'^site/', include('wqinterfaz.urls')),
    url(r'^accounts/', include('accounts.urls')),
)
