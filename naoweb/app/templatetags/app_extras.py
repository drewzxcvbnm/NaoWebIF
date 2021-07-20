from django import template
from datetime import datetime, timedelta
from dateutil import tz

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
