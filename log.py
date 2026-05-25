"""Minimal structured logger with ANSI color + spinner animation."""
import sys, threading, time, itertools

# ── ANSI colors ──
R  = '\033[0m'       # reset
B  = '\033[1m'       # bold
DIM= '\033[2m'
C  = {
    'green':  '\033[92m',
    'red':    '\033[91m',
    'yellow': '\033[93m',
    'cyan':   '\033[96m',
    'blue':   '\033[94m',
    'white':  '\033[97m',
    'grey':   '\033[90m',
}

_ICONS = {
    'ok':    ('green',  '✔'),
    'err':   ('red',    '✘'),
    'warn':  ('yellow', '⚠'),
    'info':  ('cyan',   '◆'),
    'nav':   ('blue',   '→'),
    'debug': ('grey',   '·'),
    'wait':  ('yellow', '⏳'),
}

def _fmt(kind, tag, msg):
    col, icon = _ICONS.get(kind, ('white', '•'))
    tag_s  = f"{DIM}[{tag}]{R}"
    icon_s = f"{C[col]}{icon}{R}"
    return f"  {icon_s} {tag_s} {msg}"

def ok   (tag, msg): print(_fmt('ok',    tag, msg))
def err  (tag, msg): print(_fmt('err',   tag, msg))
def warn (tag, msg): print(_fmt('warn',  tag, msg))
def info (tag, msg): print(_fmt('info',  tag, msg))
def nav  (tag, msg): print(_fmt('nav',   tag, msg))
def debug(tag, msg): print(_fmt('debug', tag, msg))

def section(title):
    bar = '─' * (len(title) + 4)
    print(f"\n{C['cyan']}{B}┌{bar}┐")
    print(f"│  {title}  │")
    print(f"└{bar}┘{R}")

# ── Spinner ──
class Spinner:
    _frames = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']

    def __init__(self, tag, msg):
        self._tag = tag
        self._msg = msg
        self._stop = threading.Event()
        self._t = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        for f in itertools.cycle(self._frames):
            if self._stop.is_set():
                break
            sys.stdout.write(f"\r  {C['cyan']}{f}{R} {DIM}[{self._tag}]{R} {self._msg}  ")
            sys.stdout.flush()
            time.sleep(0.08)
        sys.stdout.write('\r' + ' ' * 60 + '\r')
        sys.stdout.flush()

    def __enter__(self):
        self._t.start()
        return self

    def __exit__(self, *_):
        self._stop.set()
        self._t.join()
