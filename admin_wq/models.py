from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _ 
from json_field import JSONField
import json

class Base(models.Model):
    creation_date = models.DateTimeField('creation date', auto_now_add=True)
    modification_date = models.DateTimeField('modification date', auto_now=True)

    class Meta:
        abstract = True

class Config(Base):
    key = models.CharField(max_length=200, verbose_name=_("Key"))
    value = models.CharField(max_length=200, verbose_name=_("Value"))

class Website(Base):
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    domain = models.CharField(max_length=200, verbose_name=_("Domain"))
    start_url = models.CharField(max_length=200, verbose_name=_("Start Url"))
    user = models.ForeignKey(User, verbose_name=_("User"))

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Validator(Base):
    classname = models.CharField(max_length=200, verbose_name=_("Class name"))
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    description = models.TextField(verbose_name=_("Name"))
    parameters = JSONField()

    def __unicode__(self):
        return self.name

class Execution(Base):
    start_date = models.DateTimeField('start date', auto_now_add=True)
    end_date = models.DateTimeField('end date', blank=True, null=True)
    parameters = JSONField()
    website = models.ForeignKey(Website)
    user = models.ForeignKey(User, verbose_name=_("User"))
    validators = models.ManyToManyField(Validator, verbose_name=_("Validators"))

class Page(Base):
    url = models.CharField(max_length=200)
    user = models.ForeignKey(User, verbose_name=_("User"))
    website = models.ForeignKey(Website)

class Result(Base):
    description = JSONField()
    execution = models.ForeignKey(Execution)
    page = models.ForeignKey(Page)
    validator = models.ForeignKey(Validator)
