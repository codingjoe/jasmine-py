try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from itertools import ifilter
from operator import itemgetter

class Formatter(object):
    COLORS = {
        'red': "\033[0;31m",
        'green': "\033[0;32m",
        'yellow': "\033[0;33m",
        'none': "\033[0m"
    }

    def __init__(self, results, **kwargs):
        self.colors = kwargs.get('colors', True)
        self.output = ''
        self.results = results

    def colorize(self, color, text):
        if not self.colors:
            return text

        return self.COLORS[color] + text + self.COLORS['none']

    def format(self):
        self.output += """
      _                     _
     | |                   (_)
     | | __ _ ___ _ __ ___  _ _ __   ___
 _   | |/ _` / __| '_ ` _ \| | '_ \ / _ \\
| |__| | (_| \__ \ | | | | | | | | |  __/
 \____/ \__,_|___/_| |_| |_|_|_| |_|\___|

"""
        self.output += self.format_progress() + "\n\n"
        self.output += self.format_summary() + "\n\n"
        self.output += self.format_failures()

        return self.output

    def format_progress(self):
        output = ""

        for result in self.results:
            if result.status == "passed":
                output += self.colorize('green', '.')
            elif result.status == "failed":
                output += self.colorize('red', 'X')
            else:
                output += self.colorize('yellow', '?')

        return output

    def format_summary(self):
        output = "{} specs, {} failed".format(len(self.results), len(list(self.results.failed())))

        pending = list(self.results.pending())
        if pending:
            output += ", {} pending".format(len(pending))

        return output

    def format_failures(self):
        output = ""
        for failure in self.results.failed():
            output += self.colorize('red', failure.fullName) + "\n" + self.clean_stack(failure.failedExpectations[0]['stack']) + "\n"

        return output

    def clean_stack(self, stack):
        def dirty(stackline):
            return "__jasmine__" in stackline or "__boot__" in stackline

        return "\n".join([stackline for stackline in stack.split("\n") if not dirty(stackline)])


class ResultList(list):
    def passed(self):
        return self._filter_status('passed')

    def failed(self):
        return self._filter_status('failed')

    def pending(self):
        return self._filter_status('pending')

    def _filter_status(self, status):
        return ifilter(lambda x: x.status == status, self)


class Parser(object):
    def parse(self, items):
        return ResultList([Result(**item) for item in items])


class Result(tuple):
    """Result(status, fullName, failedExpectations, id, description)"""

    __slots__ = ()

    _fields = ('status', 'fullName', 'failedExpectations', 'id', 'description')

    def __new__(_cls, status=None, fullName=None, failedExpectations=[], id=None, description=None):
        """Create new instance of Result(status, fullName, failedExpectations, id, description)"""
        return tuple.__new__(_cls, (status, fullName, failedExpectations, id, description))

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        """Make a new Result object from a sequence or iterable"""
        result = new(cls, iterable)
        if len(result) != 5:
            raise TypeError('Expected 5 arguments, got %d' % len(result))
        return result

    def __repr__(self):
        """Return a nicely formatted representation string"""
        return 'Result(status=%r, fullName=%r, failedExpectations=%r, id=%r, description=%r)' % self

    def _asdict(self):
        """Return a new OrderedDict which maps field names to their values"""
        return OrderedDict(zip(self._fields, self))

    def _replace(_self, **kwds):
        """Return a new Result object replacing specified fields with new values"""
        result = _self._make(map(kwds.pop, ('status', 'fullName', 'failedExpectations', 'id', 'description'), _self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result

    def __getnewargs__(self):
        """Return self as a plain tuple.  Used by copy and pickle."""
        return tuple(self)

    status = property(itemgetter(0), doc='Alias for field number 0')
    fullName = property(itemgetter(1), doc='Alias for field number 1')
    failedExpectations = property(itemgetter(2), doc='Alias for field number 2')
    id = property(itemgetter(3), doc='Alias for field number 3')
    description = property(itemgetter(4), doc='Alias for field number 4')