from django.shortcuts import render
import json
import datetime
from django.template import loader, Context
from django.http import HttpResponse
from app.items.persistence import presentations
from app.items.presentation import Presentation
from rest_framework.decorators import api_view

async def current_datetime(request):
    now = datetime.datetime.now()
    html = '<html><body>It is now %s.</body></html>' % now
    return HttpResponse(html)

def index(request):
    p = Presentation("PP")
    presentations[p.id] = p
    template = loader.get_template('app/index.html')
    context = {"presentations": presentations.values()}
    return HttpResponse(template.render(context))

@api_view(["POST"])
def createPresentation(request):
    p = Presentation(**request.data)
    presentations[p.id] = p
    return HttpResponse(status=200)