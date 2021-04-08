import datetime
import re
import typing as T

import app.script_runner

BRACKET = '\\[([^]]+)\\]'
LINE = f'^{BRACKET} {BRACKET}: (.*)$'

JOIN = '^([^ ]+) .*joined the game$'
LEFT = '^([^ ]+) .*left the game$'
SHUT = "^Closing Server$"

TIME_FORMAT = "%H:%M:%S"


class Entry:
    def __init__(self, line: str) -> None:
        match = re.search(LINE, line)
        assert match
        self.time = datetime.datetime.strptime(match.group(1), TIME_FORMAT)
        self.orig = match.group(2)
        self.text = match.group(3)


class Parser:
    def __init__(self) -> None:
        self.script_runner = app.script_runner.ScriptRunner('topherpuri.com')
        self.entries: T.List[Entry] = []

    def load(self, pattern: str = '*') -> None:
        response = self.script_runner.ssh([], f'zcat -f /mc/logs/{pattern}')
        lines = str(response.stdout, 'utf-8').split('\n')
        self.entries = [Entry(l) for l in lines if re.search(LINE, l)]

    def stats(self) -> T.List[T.Tuple[str, datetime.timedelta]]:
        stats: T.Dict[str, T.List[T.List[datetime.datetime]]] = {}
        for e in self.entries:
            join = re.search(JOIN, e.text)
            if join:
                name = join.group(1)
                if name not in stats:
                    stats[name] = []
                stats[name].append([e.time])
            left = re.search(LEFT, e.text)
            if left:
                name = left.group(1)
                stats[left.group(1)][-1].append(e.time)
            shut = re.search(SHUT, e.text)
            if shut:
                for _, v in stats.items():
                    if len(v[-1]) == 1:
                        v[-1].append(e.time)
        result = [(k, self.add_times(v)) for k, v in stats.items()]
        result.sort(key=lambda x: x[1], reverse=True)
        return result

    def add_times(
        self, times: T.List[T.List[datetime.datetime]]
    ) -> datetime.timedelta:
        if len(times[-1]) == 1:
            del times[-1]
        assert all(len(t) == 2 for t in times)
        return sum((t[1] - t[0] for t in times), datetime.timedelta())
