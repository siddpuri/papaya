import subprocess
import time
import typing as T

import app.logger

SSH_OPTIONS = [
    '-o',
    'StrictHostKeyChecking=no',
    '-o',
    'UserKnownHostsFile=/dev/null',
    '-i',
    '~/.keys/tp.key',
]


class ScriptRunner:
    def __init__(self, address: str) -> None:
        self.address = 'ec2-user@' + address
        self.logger = app.logger.Logger()

    def log(self, message: str) -> None:
        self.logger.log(message)

    # Public methods

    def start(self) -> None:
        self.wait_for_server()
        self.run_remote(
            'sudo ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime',
            'sudo yum update -y',
            'sudo reboot now',
        )
        self.wait_for_server()
        self.run_remote(
            'sudo yum install -y git jre screen emacs',
            'git clone https://github.com/siddpuri/papaya.git',
            'ln -sf papaya/bashrc .bashrc',
            'sudo mkdir /mc',
            'sudo mount /dev/nvme1n1 /mc',
            'start',
            'nohup watch &',
        )

    def warn_all(self, message: str) -> None:
        self.warn(['say'], message)

    def warn_users(self, users: T.List[str], message: str) -> None:
        self.warn([f'tell {u}' for u in users], message)

    def stop(self) -> None:
        self.run_remote('stop')

    # Implementation

    def wait_for_server(self) -> None:
        self.log('Waiting for server')
        while True:
            if self.ssh(['-o', 'ConnectTimeout=1'], 'ls').returncode == 0:
                return

    def warn(self, commands: T.List[str], message: str) -> None:
        self.log('Sending warnings')
        for t in range(5, 0, -1):
            m = 'minutes' if t > 1 else 'minute'
            self.run_remote(*(f'mc {c} {message} in {t} {m}' for c in commands))
            time.sleep(59)
        self.run_remote(*(f'mc {c} {message} now!' for c in commands))

    def run_remote(self, *commands: str) -> None:
        for c in commands:
            self.log(f'Running: {c}')
            self.ssh([], c)

    def ssh(self, options: T.List[str], command: str) -> T.Any:
        args = ['ssh'] + SSH_OPTIONS + options + [self.address, command]
        return subprocess.run(args, capture_output=True, check=False)
