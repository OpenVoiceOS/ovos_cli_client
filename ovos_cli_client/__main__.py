# Copyright 2017 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import curses
import io
import os.path
import signal
import sys

from ovos_utils.configuration import read_mycroft_config
from ovos_utils.signal import get_ipc_directory

from ovos_cli_client.text_client import (
    load_settings, save_settings, simple_cli, gui_main,
    start_log_monitor, start_mic_monitor, connect_to_mycroft,
    ctrl_c_handler
)

sys.stdout = io.StringIO()
sys.stderr = io.StringIO()


def custom_except_hook(exctype, value, traceback):
    print(sys.stdout.getvalue(), file=sys.__stdout__)
    print(sys.stderr.getvalue(), file=sys.__stderr__)
    sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__
    sys.__excepthook__(exctype, value, traceback)


sys.excepthook = custom_except_hook  # noqa


def main():
    # Monitor system logs
    try:
        config = read_mycroft_config()
    except:
        config = {}

    if 'log_dir' not in config:
        config["log_dir"] = "/var/log/mycroft"

    log_dir = os.path.expanduser(config['log_dir'])
    for f in os.listdir(log_dir):
        if not f.endswith(".log"):
            continue
        start_log_monitor(os.path.join(log_dir, f))

    # Monitor IPC file containing microphone level info
    start_mic_monitor(os.path.join(get_ipc_directory(), "mic_level"))

    connect_to_mycroft()

    if '--simple' in sys.argv:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        simple_cli()
    else:
        # Special signal handler allows a clean shutdown of the GUI
        signal.signal(signal.SIGINT, ctrl_c_handler)
        load_settings()
        curses.wrapper(gui_main)
        curses.endwin()
        save_settings()


if __name__ == "__main__":
    main()
