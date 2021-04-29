from django.shortcuts import render
from django.views import View as ViewBase
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.http import HttpResponseRedirect


class HomeView(ViewBase):
    def get(self, req):
        return HttpResponseRedirect('/')
