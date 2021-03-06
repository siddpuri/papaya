import typing as T

import aws.instance_helper

import app.logger

from .script_runner import ScriptRunner


class Server:
    def __init__(self) -> None:
        self.logger = app.logger.Logger()
        self.instance_helper = aws.instance_helper.InstanceHelper()
        if self.instance_helper.is_instance_running():
            address = self.instance_helper.get_address()
        else:
            address = 'topherpuri.com'
        self.runner = ScriptRunner(address)

    def log(self, message: str) -> None:
        self.logger.log(message)

    # Public methods

    def start(self) -> None:
        self.log('Starting server')
        self.instance_helper.start()
        self.runner = ScriptRunner(self.instance_helper.get_address())
        self.runner.start()

    def warn(self, users: T.List[str], message: str) -> None:
        self.runner.warn_users(users, message)

    def stop(self) -> None:
        self.log('Starting shutdown')
        self.runner.warn_all('Server shutting down')
        self.stop_now()

    def stop_now(self) -> None:
        self.log('Stopping server')
        self.runner.stop()
        self.instance_helper.stop()
