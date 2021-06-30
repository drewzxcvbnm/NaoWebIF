from django.shortcuts import render
import json
import datetime
from django import template
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


def index(request):
    # p = Presentation("PP")
    # presentations[p.id] = p
    template = loader.get_template('app/index.html')
    context = {"presentations": presentations.values()}
    return HttpResponse(template.render(context))


def presentation_page(request, pid):
    p = presentations[pid]
    # p.add_survey(Survey("What is the first letter of the alphabet?", ["a", "b", "c"]))
    template = loader.get_template('app/presentation.html')
    context = {"p": p}
    return HttpResponse(template.render(context))


def survey_page(request, sid):
    s = surveys[sid]
    context = {"s": s}
    return render(request, 'app/survey.html', context)


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


@api_view(["POST"])
def answer_survey(request, sid):
    s = surveys[sid]
    a = request.data['option']
    s.results[a] += 1
    if "answered_surveys" not in request.session:
        request.session["answered_surveys"] = []
    request.session["answered_surveys"].append(sid)
    request.session.modified = True
    s = surveys[sid]
    return HttpResponse(status=200, content_type='application/json', content=json.dumps(s.results, default=str))
