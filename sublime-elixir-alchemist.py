import os
import re
import sublime, sublime_plugin
import sys
from queue import Queue, Empty
from subprocess import PIPE, Popen
from threading import Thread

_alchemist_session = None
_project_home = None
_alchemist_home = None
_home = None
_elixir_bin = None
# needs to be configurable
_elixir_source = '/opt/local/elixir-1.1.1/lib/elixir/lib'


def plugin_loaded():
    fix_path()
    log("Plugin Loaded")
    setup_home_directory()
    setup_home()


def load_alchemist():
    global _alchemist_session
    if _alchemist_session is None and _project_home is not None:
        _alchemist_session = AlchemistSession()
        log("Alchemist Session Started")
    return _alchemist_session


def log(value): print("sublime-elixir-alchemist: {}".format(value))


def fix_path():
    _environ = dict(os.environ)
    _environ['PATH'] = os.environ["PATH"] + ":/usr/local/bin"
    os.environ.clear()
    os.environ.update(_environ)


def setup_home():
    global _home
    global _alchemist_home
    global _elixir_bin
    packages = os.path.abspath(get_window_variable("packages"))
    _home = os.path.join(packages, "sublime-elixir-alchemist")
    _alchemist_home = os.path.join(_home, "alchemist-server")
    _elixir_bin = "/usr/local/bin/elixir"


def setup_home_directory():
    global _project_home
    try:
        _project_home = get_window_variable("folder")
    except KeyError:
        try:
            file_path = get_window_variable("file_path")
            if file_path.endswith("/lib"):
                _project_home = file_path[:-4]
        except KeyError:
            try:
                file_name = get_window_variable("file_name")
                if file_name == "mix.exs":
                    _project_home = get_window_variable("file_path")[:-7]
            except KeyError:
                log("Unable to determine home directory")
    log("Home directory is currently set to: {}".format(_project_home))


def get_window_variable(key):
    return sublime.active_window().extract_variables()[key]


def is_elixir_file(filename):
    return filename and filename.endswith(('.ex', '.exs'))


def get_pre_word(view, region):
    lines = view.lines(view.visible_region())
    line_of_file = None
    line_index = None
    for line in lines:
        if line.a <= region <= line.b:
            line_of_file = view.substr(line)
            line_index = region - line.a
    return line_of_file[0:line_index].split(" ")[-1]


class AlchemistSession(object):
    def __init__(self):
        is_posix = 'posix' in sys.builtin_module_names
        alchemist_run_path = os.path.join(_alchemist_home, "run.exs")
        args = [_elixir_bin, alchemist_run_path, "dev"]
        self._process = Popen(args, stdin=PIPE, stdout=PIPE, bufsize=1,
                              stderr=PIPE, close_fds=is_posix,
                              universal_newlines=True, cwd=_project_home)
        self._queue = Queue()
        self._thread = Thread(target=self._enqueue_output,
                              args=(self._process.stdout, self._queue))
        self._thread.daemon = True
        self._thread.start()

    def close(self):
        if self._process:
            self._process.terminate()

    def get_suggestions(self, evaluated_word):
        if '"' in evaluated_word or "'" in evaluated_word:
            return None
        else:
            command = 'COMP {{ "{0:s}", [ context: Elixir, imports: [], ' \
                      'aliases: [] ] }}\n'.format(evaluated_word)
            self._process.stdin.write(command)
            result = [c for c in self._get_comp_result() if not c.endswith(".")]
            return [[c, c.split("/")[0]] for c in result]

    def get_definitions(self, evaluated_word):
        if '"' in evaluated_word or "'" in evaluated_word:
            return None
        else:
            command = 'DEFL {{ "{0:s}", [ context: Elixir, imports: [], ' \
                      'aliases: [] ] }}\n'.format(evaluated_word)
            self._process.stdin.write(command)
            return self._get_defl_result()

    def _get_comp_result(self):
        result = ''
        while not result.endswith('END-OF-COMP\n'):
            try:
                line = self._queue.get_nowait()
                result += line
            except Empty:
                pass
        commands = sorted(result.split("\n")[0:-2])
        return commands

    def _get_defl_result(self):
        result = ''
        while not result.endswith('END-OF-DEFL\n'):
            try:
                line = self._queue.get_nowait()
                result += line
            except Empty:
                pass
        definitions = sorted(result.split("\n")[0:-2])
        return definitions

    def _enqueue_output(self, stdout, queue):
        for line in iter(stdout.readline, b''):
            queue.put(line)
        stdout.close()


class AutoComplete(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        if is_elixir_file(view.file_name()):
            load_alchemist()
            pre_word = get_pre_word(view, locations[0])
            return _alchemist_session.get_suggestions(pre_word)
        else:
            return None


class FindElixirDefinitionCommand(sublime_plugin.TextCommand):
    """"""
    def run(self, edit):
        view = sublime.active_window().active_view()
        if is_elixir_file(view.file_name()):
            load_alchemist()
            word_boundaries = view.word(view.sel()[0])
            actual_word = view.substr(word_boundaries)
            pre_word = get_pre_word(view, word_boundaries.a)
            full_word = pre_word + actual_word
            payload = None
            if full_word.find(".") == -1:
                if full_word[0].isupper():
                    payload = full_word + ",nil"
                else:
                    payload = "nil," + full_word
            else:
                payload = full_word.replace(".", ",")
            file_name = _alchemist_session.get_definitions(payload)[0]
            if file_name != '':
                final_file_name = None
                if file_name.startswith("/private/tmp"):
                    regex = r'/private/tmp/.+/lib'
                    final_file_name = re.sub(regex, _elixir_source, file_name)
                else:
                    final_file_name = file_name
                sublime.active_window().open_file(final_file_name)
                # lookup definition in file, lookup definition in local file if
                # file isn't found.
            else:
                return None
        else:
            return None
