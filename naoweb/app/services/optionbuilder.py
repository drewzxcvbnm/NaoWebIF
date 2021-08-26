from enum import Enum
from inspect import Signature
from datetime import datetime
from dateutil import tz

from app.items.survey import Survey


class DefaultOptionResolver:

    def __init__(self, o: str, s: Survey, session):
        self.option_builder = ChoiceAwareOptionBuilderWrapper(s, session, o)
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
        return self.option_builder.build_empty_unclickable(self.o)

    def _open(self):
        if self.answered:
            return self._valid_or_invalid()
        return self.option_builder.build_clickable(self.o)

    def _closed(self):
        return self._valid_or_invalid()

    def _valid_or_invalid(self):
        if not self._has_valid():
            return self.option_builder.build_unclickable_with_nums(self.o, self.s)
        if self._is_valid():
            return self.option_builder.build_valid(self.o, self.s)
        return self.option_builder.build_invalid(self.o, self.s)

    def _has_valid(self):
        opts = self.s.currentQuestion.validOptions
        return opts is not None and len(opts) > 0

    def _is_valid(self):
        cq = self.s.currentQuestion
        return any([self.o == cq.options[vop - 1] for vop in cq.validOptions])


class ManualOptionResolver(DefaultOptionResolver):

    def __init__(self, o: str, s: Survey, session):
        super().__init__(o, s, session)
        self.option_builder = ChoiceAwareOptionBuilderWrapper(s, session, o)

    def _open(self):
        if not self.answered:
            return self.option_builder.build_clickable(self.o)
        return self.option_builder.build_unclickable_with_nums(self.o, self.s)


class AutoOptionResolver(DefaultOptionResolver):

    def _open(self):
        if self._over_deadline():
            return self._valid_or_invalid()
        if self.answered:
            return self.option_builder.build_unclickable_with_nums(self.o, self.s)
        return self.option_builder.build_clickable(self.o)

    def _over_deadline(self):
        dl = self.s.currentQuestion.deadline
        if dl is None:
            return False
        return datetime.now(tz.gettz("Europe/Riga")) > dl


class ButtonType(Enum):
    GOOD = "btn-success"
    BAD = "btn-danger"
    NORMAL = "btn-primary"


class OptionBuilder:

    def __init__(self):
        self._button_type = False
        self._grey = False
        self._show_nums = False
        self._clickable = False
        self._survey = None
        self._chosen = False

    def type(self, t: ButtonType):
        self._button_type = t
        return self

    def clickable(self, c: bool):
        self._clickable = c
        return self

    def greyed(self, g: bool):
        self._grey = g
        return self

    def shownums(self, n: bool, survey: Survey = None):
        self._show_nums = n
        self._survey = survey
        return self

    def ischosen(self):
        self._chosen = True
        return self

    def buildoption(self, op: str):
        style = "" if self._grey is False else "background-color: gray;"
        if self._chosen:
            style += "border-color:rgba(82,168,236,.8);border-width:3px;"
        btn = self._button_type.value
        nums = "" if self._show_nums is False else f'<div style="float: right">{self._survey.currentQuestion.results[op]}</div>'
        click = "" if self._clickable is False else f'onclick="submit_answer(\'{op}\')"'
        res = f'<div {click} class ="btn {btn} option" style="display: block;{style}">{op} {nums}</div>'
        return res


class OptionBuilderWrapper:

    def build_clickable(self, option: str):
        b = OptionBuilder().type(ButtonType.NORMAL).clickable(True)
        return self._map_builder(b).buildoption(option)

    def build_empty_unclickable(self, option: str):
        b = OptionBuilder().type(ButtonType.NORMAL).greyed(True)
        return self._map_builder(b).buildoption(option)

    def build_valid(self, option: str, s: Survey):
        b = OptionBuilder().type(ButtonType.GOOD).shownums(True, s)
        return self._map_builder(b).buildoption(option)

    def build_invalid(self, option: str, s: Survey):
        b = OptionBuilder().type(ButtonType.BAD).shownums(True, s)
        return self._map_builder(b).buildoption(option)

    def build_unclickable_with_nums(self, option: str, s: Survey):
        b = OptionBuilder().type(ButtonType.NORMAL).greyed(True).shownums(True, s)
        return self._map_builder(b).buildoption(option)

    def _map_builder(self, builder):
        return builder


class ChoiceAwareOptionBuilderWrapper(OptionBuilderWrapper):

    def __init__(self, survey: Survey, session, option: str):
        self.survey = survey
        self.session = session
        self.option = option
        super().__init__()

    def _map_builder(self, builder):
        qid = self.survey.currentQuestion.id
        if self.session.get('answered_questions') is None or qid not in self.session['answered_questions']:
            return builder
        choice = self.session[qid]
        if choice == self.option:
            builder.ischosen()
        return builder


# < div class ="btn btn-success option" style="display: block;" >
# {{o}}
# <div style = "float: right" > {{s.currentQuestion.results | mapget: o}} < / div >
# < / div >

_optionBuilders = {
    "auto": lambda o, s, ses: AutoOptionResolver(o, s, ses),
    "manual": lambda o, s, ses: ManualOptionResolver(o, s, ses),
}


def getOptionBuilder(s: Survey, o: str, session):
    default = lambda x1, x2, x3: DefaultOptionResolver(x1, x2, x3)
    return _optionBuilders.get(s.type, default)(o, s, session)
