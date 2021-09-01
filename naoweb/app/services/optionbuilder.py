from enum import Enum
from inspect import Signature
from datetime import datetime
from dateutil import tz

from app.items.survey import Survey


class DefaultOptionResolver:

    def __init__(self, option_info):
        self.o = option_info['option-str']
        self.s = option_info['survey']
        self.session = option_info['session']
        self.option_index = option_info['index']
        choice_mapper = ChoiceAwareOptionMapper(option_info)
        index_mapper = ChoiceIndexMapper(self.option_index)
        self.option_builder = OptionBuilderWrapper([choice_mapper, index_mapper])
        if self.session.get('answered_questions') is None:
            self.answered = False
        else:
            self.answered = self.s.currentQuestion.id in self.session["answered_questions"]

    def build(self):
        if self.s.status.lower() == "open":
            return self._open()
        if self.s.status.lower() == "closed":
            return self._closed()
        # if self.s.status.lower() == "draft":
        return self.option_builder.build_empty_unclickable(self.o)

    def _open(self):
        if self.s.currentQuestion.answer_type == 'multi-choice' and self._is_unclicked():
            return self.option_builder.build_clickable(self.o)
        if self.s.currentQuestion.answer_type == 'multi-choice' and not self._is_unclicked():
            return self.option_builder.build_empty_unclickable(self.o)
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

    def _is_unclicked(self):
        qid = self.s.currentQuestion.id
        if self.session.get('answered_questions') is None:
            return True
        if qid not in self.session['answered_questions']:
            return True
        return self.option_index not in self.session[qid]


class ManualOptionResolver(DefaultOptionResolver):

    def _open(self):
        if self.s.currentQuestion.answer_type == 'multi-choice' and self._is_unclicked():
            return self.option_builder.build_clickable(self.o)
        if self.s.currentQuestion.answer_type == 'multi-choice' and not self._is_unclicked():
            return self.option_builder.build_empty_unclickable(self.o)
        if not self.answered:
            return self.option_builder.build_clickable(self.o)
        return self.option_builder.build_unclickable_with_nums(self.o, self.s)


class AutoOptionResolver(DefaultOptionResolver):

    def _open(self):
        if self._over_deadline():
            return self._valid_or_invalid()
        if self.s.currentQuestion.answer_type == 'multi-choice' and self._is_unclicked():
            return self.option_builder.build_clickable(self.o)
        if self.s.currentQuestion.answer_type == 'multi-choice' and not self._is_unclicked():
            return self.option_builder.build_empty_unclickable(self.o)
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
        self._index = None

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

    def index(self, index):
        self._index = index
        return self

    def buildoption(self, op: str):
        style = "" if self._grey is False else "background-color: gray;"
        if self._chosen:
            style += "border-color:rgba(82,168,236,.8);border-width:3px;"
        btn = self._button_type.value
        nums = "" if self._show_nums is False else f'<div style="float: right">{self._survey.currentQuestion.results[self._index]}</div>'
        click = "" if self._clickable is False else f'onclick="submit_answer({self._index})"'
        index = "" if self._index is None else f'index={self._index}'
        res = f'<div {click} {index} class ="btn {btn} option" style="display: block;{style}">{op} {nums}</div>'
        return res


class OptionBuilderWrapper:

    def __init__(self, mappers):
        self.mappers = mappers

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
        for mapper in self.mappers:
            builder = mapper.map_builder(builder)
        return builder


class ChoiceIndexMapper:

    def __init__(self, option_index):
        self.i = option_index

    def map_builder(self, builder):
        builder.index(self.i)
        return builder


class ChoiceAwareOptionMapper:

    def __init__(self, option_info):
        self.session = option_info['session']
        self.qid = option_info['survey'].currentQuestion.id
        self.option = option_info['option-str']
        self.option_index = option_info['index']

    def map_builder(self, builder):
        qid = self.qid
        if self.session.get('answered_questions') is None or qid not in self.session['answered_questions']:
            return builder
        choices = self.session[qid]
        if self.option_index in choices:
            builder.ischosen()
        return builder


# < div class ="btn btn-success option" style="display: block;" >
# {{o}}
# <div style = "float: right" > {{s.currentQuestion.results | mapget: o}} < / div >
# < / div >

_optionBuilders = {
    "auto": lambda o: AutoOptionResolver(o),
    "manual": lambda o: ManualOptionResolver(o),
}


def get_option_builder(option_info):
    default = lambda info: DefaultOptionResolver(info)
    return _optionBuilders.get(option_info['survey'].type, default)(option_info)
