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
        url = reverse('run_test', kwargs={'website_id':obj.id})
        return '<a href="%s">Run</a>' % (url)
    object_link.allow_tags = True

admin.site.register(Website, WebsiteAdmin)
admin.site.register(Validator)
admin.site.register(ValidatorType)

