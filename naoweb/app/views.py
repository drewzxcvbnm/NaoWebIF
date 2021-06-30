from django.shortcuts import render
import json
import datetime
from django.template import loader, Context
from django.http import HttpResponse
from app.items.survey import Survey
from app.items.persistence import presentations, surveys
from app.items.presentation import Presentation
from rest_framework.decorators import api_view


async def current_datetime(request):
    now = datetime.datetime.now()
    html = '<html><body>It is now %s.</body></html>' % now
    return HttpResponse(html)


@api_view(["GET"])
def index(request):
    p = Presentation("PP")
    presentations[p.id] = p
    template = loader.get_template('app/index.html')
    context = {"presentations": presentations.values()}
    return HttpResponse(template.render(context))


@api_view(["GET"])
def get_survey(request, sid):
    s = surveys[sid]
    return HttpResponse(status=200, content_type='application/json', content=json.dumps(s.__dict__, default=str))


@api_view(["POST"])
def create_presentation(request):
    p = Presentation(**request.data)
    return HttpResponse(status=200, content=str(p.id))


@api_view(["POST"])
def create_survey(request, pid):
    p = presentations[pid]
    s = Survey(**request.data)
    p.add_survey(s)
    return HttpResponse(status=200, content=str(s.id))
