from django import template
from datetime import datetime, timedelta
from dateutil import tz

from app.services.optionbuilder import get_option_builder

register = template.Library()


@register.filter
def mapget(h, key):
    return h[key]


@register.filter
def indexOf(li, el):
    for i, v in enumerate(li):
        if v is el:
            return i
    return -1


@register.filter
def overDeadline(cq):
    if cq.deadline is None:
        return False
    return cq.deadline < datetime.now(tz.gettz("Europe/Riga"))


@register.filter
def answered(answeredQuestionsList, question):
    if answeredQuestionsList is None:
        return False
    if question.id in answeredQuestionsList:
        return True
    return False


@register.simple_tag()
def buildoption(survey, option, session, i):
    option_info = {'survey': survey, 'option-str': option, 'session': session, 'index': i - 1}
    b = get_option_builder(option_info)
    return b.build()
