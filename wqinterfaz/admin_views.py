from django.shortcuts import redirect, render, get_object_or_404
from wqinterfaz.models import Execution, Validator, Website
from wqinterfaz.thread import run_crawler

def list_executions(request, website_id=None):
    """@todo: Docstring for list_executions.

    :request: @todo
    :website_id: @todo
    :returns: @todo

    """
    website = Website.objects.filter(pk=website_id)
    executions = Execution.objects.filter(user=request.user, website=website)

    if request.is_ajax():
        template = 'admin/list_executions_page.html'
    else:
        template = 'admin/list_executions.html'
    return render(request, template, {
        'executions': executions,
        'page_template': 'admin/list_executions_page.html',
    })

def view_execution(request, execution_id):
    """@todo: Docstring for view_execution.

    :request: @todo
    :execution_id: @todo
    :returns: @todo

    """
    execution = Execution.objects.get(pk=execution_id)
    validator = Validator.objects.filter(execution=execution)[0]

    return redirect('wqinterfaz.views.view_execution_by_validator', execution_id=execution.id, validator_id=validator.id)

def run_test(request, website_id=None):
    """@todo: Docstring for prueba.

    :request: @todo
    :returns: @todo

    """
    website = Website.objects.get(pk=website_id)
    if request.method == 'POST':
        validator_set = {}
        parameters = {}
        for validator_id in request.POST.getlist('validator'):
            validator = Validator.objects.get(pk=validator_id)
            validator_set[validator.classname] = validator

            validator_parameters = {"fields": {}}
            if validator.parameters is not None:
                for field in validator.parameters["fields"]:
                    value = request.POST["param_" + str(validator.id) + "_" + field["name"]]
                    validator_parameters["fields"][field["name"]] =  value
                parameters[validator.classname] = validator_parameters

#        threads = list()
#        t = threading.Thread(target=run_crawler, args=(request.user, website, validator_set, parameters))
#        threads.append(t)
#        t.start()

        return render(request, 'admin/running_test.html')
    else:
        validators = Validator.objects.all().order_by('creation_date')
        return render(request, 'admin/run_test.html', {'website': website, 'validators': validators})

