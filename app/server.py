import typing as T

import aws.instance_helper

from .script_runner import ScriptRunner


class Server:
    def __init__(self) -> None:
        self.instance_helper = aws.instance_helper.InstanceHelper()
        try:
            address = self.instance_helper.get_address()
        except Exception:
            address = 'topherpuri.com'
        self.runner = ScriptRunner(address)

    # Public methods

    def start(self) -> None:
        self.instance_helper.start()
        self.runner = ScriptRunner(self.instance_helper.get_address())
        self.runner.start()

    def warn(self, users: T.List[str], message: str) -> None:
        self.runner.warn_users(users, message)

    def stop(self) -> None:
        self.runner.warn_all('Server shutting down')
        self.stop_now()

    def stop_now(self) -> None:
        self.runner.stop()
        self.instance_helper.stop()
