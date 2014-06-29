from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Submit
from wqinterfaz.models import Website

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import ModelForm
from django.forms.models import inlineformset_factory, formset_factory
from django.utils.translation import ugettext_lazy as _ 
#from tinymce.widgets import TinyMCE

class WebsiteForm(forms.ModelForm):
    name = forms.CharField(max_length=100, required=False, label=_("Name")) 
    domain = forms.CharField(max_length=100, required=False, label=_("Domain")) 
    start_url = forms.CharField(max_length=100, required=False, label=_("Start Url")) 

    def __init__(self, *args, **kwargs):
        super(WebsiteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
#        self.helper.form_class = 'well form-inline'

    class Meta:
        model = Website
        fields = ['name', 'domain', 'start_url']

