from django.contrib import admin
from django.core.urlresolvers import reverse
from wqinterfaz.models import *

class WebsiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain', 'start_url', 'object_link')
    list_select_related = True

    def queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(WebsiteAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def object_link(self, obj):
        url1 = reverse('run_test', kwargs={'website_id':obj.id})
#        url2 = reverse('list_executions', kwargs={'website_id':obj.id})
        url2 = '/admin/wqinterfaz/execution/?website__id__exact=%s' % (obj.id)
        return '<a href="%s">Run</a><a href="%s">List</a>' % (url1, url2)
    object_link.allow_tags = True

class ExecutionAdmin(admin.ModelAdmin):
    list_display = ('website', 'start_date', 'end_date', 'object_link',)
    list_filter = ('website',)

    def object_link(self, obj):
        url = '/admin/wqinterfaz/result/?execution__id__exact=%s' % (obj.id)
        return '<a href="%s">Results</a>' % (url)
    object_link.allow_tags = True

class ResultAdmin(admin.ModelAdmin):
    list_display = ('description', 'page', 'validator',)
    list_filter = ('validator',)

admin.site.register(Execution, ExecutionAdmin)
admin.site.register(Website, WebsiteAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Validator)
