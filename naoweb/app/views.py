from django.shortcuts import render
from django.template import loader
import datetime
from django.http import HttpResponse

async def current_datetime(request):
    now = datetime.datetime.now()
    html = '<html><body>It is now %s.</body></html>' % now
    return HttpResponse(html)

def index(request):
    template = loader.get_template('app/index.html')
    return HttpResponse(template.render())
