from enum import Enum
from inspect import Signature
from datetime import datetime
from dateutil import tz

from app.items.survey import Survey


class DefaultOptionBuilder:

    def __init__(self, o: str, s: Survey, session):
        self.o = o
        self.s = s
        if session.get('answered_questions') is None:
            self.answered = False
        else:
            self.answered = s.currentQuestion.id in session["answered_questions"]

    def build(self):
        if self.s.status.lower() == "open":
            return self._open()
        if self.s.status.lower() == "closed":
            return self._closed()
        # if self.s.status.lower() == "draft":
        return OptionBuilder.buildEmptyUnclickable(self.o)

    def _open(self):
        if self.answered:
            return self._valid_or_invalid()
        return OptionBuilder.buildClickable(self.o)

    def _closed(self):
        return self._valid_or_invalid()

    def _valid_or_invalid(self):
        if not self._has_valid():
            return OptionBuilder.buildUnclickableWithNums(self.o, self.s)
        if self._is_valid():
            return OptionBuilder.buildValid(self.o, self.s)
        return OptionBuilder.buildInvalid(self.o, self.s)

    def _has_valid(self):
        return self.s.currentQuestion.validOption is not None

    def _is_valid(self):
        cq = self.s.currentQuestion
        vop = cq.options[cq.validOption - 1]
        return vop == self.o


class ManualOptionBuilder(DefaultOptionBuilder):
    pass


class AutoOptionBuilder(DefaultOptionBuilder):

    def _open(self):
        if self._over_deadline():
            return self._valid_or_invalid()
        if self.answered:
            return OptionBuilder.buildUnclickableWithNums(self.o, self.s)
        return OptionBuilder.buildClickable(self.o)

    def _over_deadline(self):
        dl = self.s.currentQuestion.deadline
        if dl is None:
            return False
        return datetime.now(tz.gettz("Europe/Riga")) > dl


class OptionBuilderWrapper:

    def __init__(self, builder):
        self.b = builder
        self.paramnum = len(Signature(builder).parameters)

    def build(self, o: str, s: Survey = None):
        if self.paramnum == 2:
            return self.b(o, s)
        else:
            return self.b(o)


class ButtonType(Enum):
    GOOD = "btn-success"
    BAD = "btn-danger"
    NORMAL = "btn-primary"


class OptionBuilder:

    def __init__(self):
        self._t = False
        self._g = False
        self._n = False
        self._c = False
        self._s = None

    def type(self, t: ButtonType):
        self._t = t
        return self

    def clickable(self, c: bool):
        self._c = c
        return self

    def greyed(self, g: bool):
        self._g = g
        return self

    def shownums(self, n: bool, survey: Survey = None):
        self._n = n
        self._s = survey
        return self

    def buildoption(self, op: str):
        style = "" if self._g == False else "background-color: gray"
        btn = self._t.value
        nums = "" if self._n == False else f'<div style="float: right">{self._s.currentQuestion.results[op]}</div>'
        click = "" if self._c == False else f'onclick="submit_answer(\'{op}\')"'
        return f'<div {click} class ="btn {btn} option" style="display: block;{style}">{op} {nums}</div>'

    @staticmethod
    def buildClickable(option: str):
        return OptionBuilder().type(ButtonType.NORMAL).clickable(True).buildoption(option)

    @staticmethod
    def buildEmptyUnclickable(option: str):
        return OptionBuilder().type(ButtonType.NORMAL).greyed(True).buildoption(option)

    @staticmethod
    def buildValid(option: str, s: Survey):
        return OptionBuilder().type(ButtonType.GOOD).shownums(True, s).buildoption(option)

    @staticmethod
    def buildInvalid(option: str, s: Survey):
        return OptionBuilder().type(ButtonType.BAD).shownums(True, s).buildoption(option)

    @staticmethod
    def buildUnclickableWithNums(option: str, s: Survey):
        return OptionBuilder().type(ButtonType.NORMAL).greyed(True).shownums(True, s).buildoption(option)


# < div class ="btn btn-success option" style="display: block;" >
# {{o}}
# <div style = "float: right" > {{s.currentQuestion.results | mapget: o}} < / div >
# < / div >

_optionBuilders = {
    "auto": lambda o, s, ses: AutoOptionBuilder(o, s, ses),
    "man": lambda o, s, ses: ManualOptionBuilder(o, s, ses),
}


def getOptionBuilder(s: Survey, o: str, session):
    mydef = lambda x1, x2, x3: DefaultOptionBuilder(x1, x2, x3)
    return _optionBuilders.get(s.type, mydef)(o, s, session)
