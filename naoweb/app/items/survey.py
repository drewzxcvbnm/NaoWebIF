import json
import time
from threading import Timer, Thread
from typing import List
from datetime import datetime, timedelta
from dateutil import tz

from app.items.item import Item

from app.items.persistence import surveys, pinGenerator, surveyQuestions, pins


class SurveyQuestion(Item):

    def __init__(self, question: str, options: List[str], timelimit: int = None, validoptions: [int] = None,
                 answertype='single-choice', **kwargs):
        super().__init__()
        self.deadline = None
        self.question = question
        self.options = options
        self.timelimit = timelimit
        self.results = [0 for i in options]
        self.validOptions = validoptions
        self.answer_type = answertype
        surveyQuestions[self.id] = self

    def set_deadline(self):
        self.deadline = datetime.now(tz.gettz("Europe/Riga")) + timedelta(seconds=self.timelimit)


class Survey(Item):

    def __init__(self, questions: List[SurveyQuestion], status: str = "Draft", type: str = "manual",
                 pin=None, timelimit=None, **kwargs):
        super().__init__()
        self.status = status
        self.pin = pin if pin is not None else next(pinGenerator)
        self.questions = questions
        self.currentQuestion = self.questions[0]
        self.type = type
        self.timelimit = timelimit
        self.deadline = None
        pins.add(self.pin)
        surveys[self.id] = self

    @staticmethod
    def from_json(**kwargs):
        questions = kwargs.pop("questions")
        type = kwargs.get("type")
        return Survey([Survey._create_question(q, type) for q in questions], **kwargs)

    @staticmethod
    def _create_question(qmap, survey_type, **kwargs):
        if survey_type == "auto" and qmap.get("timelimit") is None:
            qmap["timelimit"] = 30
        return SurveyQuestion(**qmap)

    def open(self):
        self.status = "Open"
        if self.timelimit is not None:
            self.deadline = datetime.now(tz.gettz("Europe/Riga")) + timedelta(seconds=self.timelimit)
            Thread(target=self._close_after_deadline).start()
        if self.currentQuestion.timelimit is not None:
            self.currentQuestion.set_deadline()
        if self.type == "auto":
            self.currentQuestion.set_deadline()
            Thread(target=self.autorun).start()

    def autorun(self):
        for qi in range(0, len(self.questions)):
            self.currentQuestion = self.questions[qi]
            self.currentQuestion.set_deadline()
            time.sleep(self.currentQuestion.timelimit)
            time.sleep(5)  # 5 second time window to show answers on FE
        self.close()

    def next(self):
        from app.templatetags.app_extras import indexOf
        i = indexOf(self.questions, self.currentQuestion)
        if i < len(self.questions) - 1:
            i += 1
        self.currentQuestion = self.questions[i]
        if self.currentQuestion.timelimit is not None:
            self.currentQuestion.set_deadline()

    def prev(self):
        from app.templatetags.app_extras import indexOf
        i = indexOf(self.questions, self.currentQuestion)
        if i != 0:
            i -= 1
        self.currentQuestion = self.questions[i]
        if self.currentQuestion.timelimit is not None:
            self.currentQuestion.set_deadline()

    def _close_after_deadline(self):
        time.sleep(self.timelimit)
        self.close()

    def close(self):
        self.status = 'Closed'
