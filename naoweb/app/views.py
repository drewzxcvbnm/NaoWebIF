from django.shortcuts import render, redirect
import json
import datetime
import jsonpickle
from django.template import loader, Context
from django.http import HttpResponse
from app.items.survey import Survey, SurveyQuestion
from app.items.persistence import presentations, surveys, surveyQuestions
from app.items.presentation import Presentation
from rest_framework.decorators import api_view


def sid_is_present(func):
    def wrapper(*args, **kwargs):
        sid = kwargs['sid']
        if sid not in surveys:
            context = {"msg": f"Survey(id={sid}) is not present"}
            temp = loader.get_template('error/404.html')
            return HttpResponse(status=404, content=temp.render(context))
        return func(*args, **kwargs)

    return wrapper


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


def pin_page(request):
    template = loader.get_template('app/pin.html')
    return HttpResponse(template.render())


def presentation_page(request, pid):
    p = presentations[pid]
    # p.add_survey(Survey("What is the first letter of the alphabet?", ["a", "b", "c"]))
    template = loader.get_template('app/presentation.html')
    context = {"p": p}
    return HttpResponse(template.render(context))


@sid_is_present
def survey_page(request, sid):
    s = surveys[sid]
    context = {"s": s}
    return render(request, 'app/survey.html', context)


@sid_is_present
@api_view(["GET"])
def open_survey(request, sid):
    s = surveys[sid]
    s.open()
    return HttpResponse(status=200, content_type='application/json', content=survey_to_json(s))


@sid_is_present
@api_view(["GET"])
def get_survey_status(request, sid):
    s = surveys[sid]
    ret = {"status": s.status, "qid": s.currentQuestion.id}
    return HttpResponse(status=200, content_type='application/json', content=json.dumps(ret))


@sid_is_present
@api_view(["GET"])
def get_survey(request, sid):
    s = surveys[sid]
    return HttpResponse(status=200, content_type='application/json', content=survey_to_json(s))


@api_view(["GET"])
def get_survey_by_pin(request, pin):
    res = list(filter(lambda x: x.pin.lower() == pin.lower(), surveys.values()))
    if len(res) == 0:
        return HttpResponse(status=400, content_type='application/json', content="false")
    s = res[0]
    return HttpResponse(status=200, content_type='application/json', content=survey_to_json(s))


@api_view(["POST"])
def create_presentation(request):
    p = Presentation(**request.data)
    return HttpResponse(status=200, content=str(p.id))


@api_view(["POST"])
def create_survey(request, pid):
    p = presentations[pid]
    s = Survey.from_json(**request.data)
    p.add_survey(s)
    return HttpResponse(status=200, content=str(s.id))


@api_view(["POST"])
def answer_survey_question(request, qid):
    q = surveyQuestions[qid]
    a = request.data['option']
    q.results[a] += 1
    if "answered_questions" not in request.session:
        request.session["answered_questions"] = []
    request.session["answered_questions"].append(qid)
    if qid not in request.session:
        request.session[qid] = []
    request.session[qid].append(a)
    request.session.modified = True
    q = surveyQuestions[qid]
    return HttpResponse(status=200, content_type='application/json', content=json.dumps(q.results, default=str))


@sid_is_present
@api_view(["POST"])
def update_survey(request, sid):
    s = surveys[sid]
    for k, v in request.data.items():
        setattr(s, k, v)
    return HttpResponse(status=200, content="done")


@api_view(["DELETE"])
def delete_presentation(request, pid):
    pr = presentations[pid]
    del presentations[pid]
    for s in pr.surveys:
        del surveys[s.id]
    return HttpResponse(status=200, content="done")


@api_view(["DELETE"])
def clear_data(request):
    for pid in list(presentations.keys()):
        del presentations[pid]
    for sid in list(surveys.keys()):
        del surveys[sid]
    return HttpResponse(status=200, content="done")


@sid_is_present
def survey_next(request, sid):
    s = surveys[sid]
    s.next()
    return HttpResponse(status=200, content="done")


@sid_is_present
def survey_prev(request, sid):
    s = surveys[sid]
    s.prev()
    return HttpResponse(status=200, content="done")


@api_view(["GET"])
def favicon(request):
    return redirect('/static/app/favicon.ico')


@sid_is_present
@api_view(["GET"])
def user_score(request, sid):
    session = request.session
    survey = surveys[sid]
    denom = len(survey.questions)
    numer = sum(map(lambda q: user_question_score(q, session), survey.questions))
    return HttpResponse(status=200, content=str(round(numer / denom, 2)))


@sid_is_present
@api_view(["GET"])
def survey_score(request, sid):
    survey = surveys[sid]
    denom = len(survey.questions)
    numer = sum(map(lambda q: survey_question_score(q), survey.questions))
    return HttpResponse(status=200, content=str(round(numer / denom, 2)))


def survey_question_score(question):
    results = question.results
    if question.validOptions is None or len(question.validOptions) == 0:
        return 1
    if sum(results) == 0:
        return 0
    valids = [i - 1 for i in question.validOptions]
    return sum([results[valid_option_index] for valid_option_index in valids]) / sum(results)


def user_question_score(question: SurveyQuestion, session):
    valid_options = question.validOptions
    if valid_options is None or len(valid_options) == 0:
        return 1
    if question.id not in session:
        return 0
    valid_options = set(map(lambda o: o - 1, valid_options))
    user_answers = set(session[question.id])
    numer = len(user_answers.intersection(valid_options)) - len(user_answers.difference(valid_options))
    return max(numer / len(valid_options), 0)


def survey_to_json(survey):
    return jsonpickle.encode(survey, unpicklable=False)
