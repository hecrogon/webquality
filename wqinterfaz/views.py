from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404

from wqinterfaz.models import Execution, Result, Validator, Website
from wqinterfaz.thread import run_crawler
from wqinterfaz.forms import WebsiteForm

from scrapy.crawler import Crawler
from scrapy.settings import Settings
from scrapy import log
from scrapy.xlib.pydispatch import dispatcher

from crawler.spiders.spider import WebQualitySpider

from twisted.internet import reactor
import threading

def index(request):
    return render(request, 'index.html')

def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def list_websites(request):
    websites = Website.objects.filter(user=request.user)
    return render(request, 'websites/list_websites.html', { 'websites': websites })

@login_required
def view_website(request, website_id):
    website = Website.objects.get(pk=website_id)
    return render(request, 'websites/view_website.html', { 'website': website })

@login_required
def edit_website(request, website_id=None):
    if website_id:
        website = Website.objects.get(pk=website_id)
    else:
        website = Website(user=request.user)

    if request.method == 'POST':
        form = WebsiteForm(request.POST, instance=website)

        if form.is_valid():        
            form.save()

            return HttpResponseRedirect(reverse('site_list_websites'))
    else:
        form = WebsiteForm(instance=website)

    return render(request, 'websites/website_form.html', {'form': form,})

@login_required
def delete_website(request, website_id):
#    get_object_or_404(Website, pk=website_id).delete()
    return HttpResponseRedirect(reverse('site_list_websites'))

@login_required
def list_executions(request, website_id):
    website = Website.objects.filter(pk=website_id)
    executions = Execution.objects.filter(user=request.user, website=website)

    if request.is_ajax():
        template = 'websites/list_executions_page.html'
    else:
        template = 'websites/list_executions.html'
    return render(request, template, {
        'executions': executions,
        'page_template': 'websites/list_executions_page.html',
    })

@login_required
def view_execution(request, execution_id):
    execution = Execution.objects.get(pk=execution_id)
    validator = Validator.objects.filter(execution=execution)[0]

    return redirect('wqinterfaz.views.view_execution_by_validator', execution_id=execution.id, validator_id=validator.id)

@login_required
def view_execution_by_validator(request, execution_id, validator_id):
    execution = Execution.objects.get(pk=execution_id)
    validator = Validator.objects.get(pk=validator_id)

    results = Result.objects.filter(execution=execution, validator=validator)
    validators = Validator.objects.filter(execution=execution)

    if request.is_ajax():
        template = 'websites/view_execution_page.html'
    else:
        template = 'websites/view_execution.html'
    return render(request, template, {
        'execution': execution,
        'results': results,
        'validators': validators,
        'validator': validator,
        'page_template': 'websites/view_execution_page.html',
    })

@login_required
def list_validators(request):
    validators = Validator.objects.all().order_by('creation_date')
    return render(request, 'validators/list_validators.html', { 'validators': validators })

@login_required
def view_validator(request, validator_id):
    validator = Validator.objects.filter(pk=validator_id)
    return render(request, 'validators/view_validator.html', { 'validator': validator })

@login_required
def run_test(request, website_id=None):
    website = Website.objects.get(pk=website_id)
    if request.method == 'POST':
        validator_set = {}
        parameters = {}
        for validator_id in request.POST.getlist('validator'):
            validator = Validator.objects.get(pk=validator_id)
            validator_set[validator.classname] = validator

            validator_parameters = { "fields": {} }
            if validator.parameters is not None:
                for field in validator.parameters["fields"]:
                    value = request.POST["param_" + str(validator.id) + "_" + field["name"]]
                    validator_parameters["fields"][field["name"]] =  value
                parameters[validator.classname] = validator_parameters

        threads = list()
        t = threading.Thread(target=run_crawler, args=(request.user, website, validator_set, parameters))
        threads.append(t)
        t.start()

        return render(request, 'websites/running_test.html')
    else:
        validators = Validator.objects.all().order_by('creation_date')
        return render(request, 'websites/run_test.html', { 'website': website, 'validators': validators })

