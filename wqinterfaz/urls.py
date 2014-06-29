from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView
from wqinterfaz import views

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='index/')),
    url(r'^index/$', 'wqinterfaz.views.index', name="index"),
    url(r'^dashboard/$', 'wqinterfaz.views.dashboard', name="dashboard"),

    url(r'^list_websites/$', 'wqinterfaz.views.list_websites', name='site_list_websites'),
    url(r'^view_website/(?P<website_id>\d+)/$', 'wqinterfaz.views.view_website', name='view_website'),
    url(r'^edit_website/$', 'wqinterfaz.views.edit_website', name="new_website"),
    url(r'^edit_website/(?P<website_id>\d+)/$', 'wqinterfaz.views.edit_website', name="edit_website"),
    url(r'^delete_website/(?P<website_id>\d+)/$', 'wqinterfaz.views.delete_website', name='delete_website'),

    url(r'^list_validators/$', 'wqinterfaz.views.list_validators', name='site_list_validators'),
    url(r'^view_validator/(?P<validator_id>\d+)/$', 'wqinterfaz.views.view_validator', name='view_validator'),

    url(r'^run_test/(?P<website_id>\d+)/$', 'wqinterfaz.views.run_test', name='run_test'),

    url(r'^list_executions/(?P<website_id>\d+)/$', 'wqinterfaz.views.list_executions', name='list_executions'),
    url(r'^view_execution/(?P<execution_id>\d+)/$', 'wqinterfaz.views.view_execution', name='view_execution'),
    url(r'^view_execution_by_validator/(?P<execution_id>\d+)/(?P<validator_id>\d+)/$', 'wqinterfaz.views.view_execution_by_validator', name='view_execution_by_validator'),
)
