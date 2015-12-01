# Interactive monoalphabetic substitution tool
import curses
from curses import wrapper

from trans import trans

##### Support

class Application(object):
    DEFAULT_MODE_CLS = None  # Set later
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.stdscr.keypad(1)
        self.key = {}
        self.obuf = None
        self.nbuf = None
        self.scroll = (0, 0)
        self.mode = self.DEFAULT_MODE_CLS(self)
        self.echotxt = ''
        self.running = True
        self.layout()
    def quit(self):
        self.running = False
    def layout(self):
        self.sh, self.sw = self.stdscr.getmaxyx()
        self.obufwin = curses.newwin(self.sh - 4, self.sw / 2, 0, 0)
        self.nbufwin = curses.newwin(self.sh - 4, self.sw - self.sw / 2, 0, self.sw / 2)
        self.keywin = curses.newwin(2, self.sw, self.sh - 4, 0)
        self.modewin = curses.newwin(1, self.sw, self.sh - 2, 0)
        self.statwin = curses.newwin(1, self.sw, self.sh - 1, 0)
    def getobuf(self):
        return self.buf.instr(0, 0)
    def getnbuf(self):
        return trans(self.getobuf(), self.key)
    def update(self, echotxt=''):
        self.modewin.erase()
        self.modewin.addstr(0, 0, self.mode.name())
        self.modewin.noutrefresh()
        self.statwin.erase()
        self.statwin.addstr(0, 0, echotxt)
        self.statwin.noutrefresh()
        self.keywin.erase()
        items = sorted(self.key.items(), key=lambda pair: pair[0])
        for idx, pair in enumerate(items):
            self.keywin.addstr(0, idx, pair[0])
            self.keywin.addstr(1, idx, pair[1])
        self.keywin.noutrefresh()
        self.obufwin.erase()
        self.nbufwin.erase()
        if self.obuf is not None:
            self.nbuf.erase()
            self.nbuf.addstr(0, 0, self.getnbuf())
            my, mx = self.obufwin.getmaxyx()
            self.obuf.overwrite(self.obufwin, self.scroll[0], self.scroll[1], 0, 0, my, mx)
            my, mx = self.nbufwin.getmaxyx()
            self.nbuf.overwrite(self.nbufwin, self.scroll[0], self.scroll[1], 0, 0, my, mx)
        self.obufwin.noutrefresh()
        self.nbufwin.noutrefresh()
        curses.doupdate()
    def loadobuf(self, f):
        val = f.read()
        lines = val.count('\n')
        self.obuf = curses.newpad(2 * lines, self.sw)
        self.obuf.addstr(val)
    def saveobuf(self, f):
        f.write(self.getobuf())
        f.flush()
    def savenbuf(self, f):
        f.write(self.getnbuf())
        f.flush()
    def loadkey(self, f):
        frm = f.readline()
        to = f.readline()
        self.key = dict(zip(frm, to))
    def savekey(self, f):
        items = sorted(self.key.items(), key=lambda pair: pair[0])
        f.write(''.join([i[0] for i in items])+'\n')
        f.write(''.join([i[1] for i in items])+'\n')
        f.flush()
    def clrobuf(self):
        self.obuf = None
    def clrkey(self):
        self.key = {}
    def clrstat(self):
        self.echotxt = ''
    def echo(self, txt):
        if self.echotxt:
            self.echotxt += ' | '+txt
        else:
            self.echotxt += txt
    def prompt(self, prompt):
        self.statwin.erase()
        self.statwin.move(0, 0)
        self.statwin.addstr(prompt)
        self.statwin.refresh()
        return self.statwin.getstr()
    def loop(self):
        while self.running:
            self.update(self.echotxt)
            self.clrstat()
            kp = self.stdscr.getch()
            try:
                res = self.mode(kp)
            except Exception as e:
                self.echo('Error occurred: %r'%(e,))
            else:
                if res is not None:
                    self.mode = res

class Mode(object):
    def __init__(self, app):
        self.app = app
    def __call__(self, kp):
        val = getattr(self, 'kd_%d'%(kp,), None)
        if val is None:
            val = getattr(self, 'kx_%x'%(kp,), None)
        if val is None:
            val = getattr(self, 'kc_%s'%(chr(kp),), None)
        if val is None:
            val = self.k_unknown
        return val(kp)
    def k_unknown(self, kp):
        self.app.echo('Unknown keypress: %d/%x'%(kp, kp))
    def name(self):
        return repr(self)

def try_chr(i):
    try:
        return chr(i)
    except ValueError:
        return None

##### Input modes

class NormalMode(Mode):
    def name(self):
        return 'Normal'
    def kc_q(self, kp):
        self.app.quit()
    def kc_s(self, kp):
        return SaveMode(self.app)
    def kc_l(self, kp):
        return LoadMode(self.app)
    def kc_c(self, kp):
        return ClearMode(self.app)
    def kc_m(self, kp):
        return MapMode(self.app)

class SaveMode(Mode):
    def name(self):
        return 'Save <[o]ld buffer, [n]ew buffer, [k]ey>?'
    def kc_o(self, kp):
        self.app.saveobuf(open(self.app.prompt('Filename (save old buffer): '), 'w'))
        return NormalMode(self.app)
    def kc_n(self, kp):
        self.app.savenbuf(open(self.app.prompt('Filename (save new buffer): '), 'w'))
        return NormalMode(self.app)
    def kc_k(self, kp):
        self.app.savekey(open(self.app.prompt('Filename (save key): '), 'w'))
        return NormalMode(self.app)

class LoadMode(Mode):
    def name(self):
        return 'Load <[o]ld buffer, [k]ey>?'
    def kc_o(self, kp):
        self.app.loadobuf(open(self.app.prompt('Filename (load old buffer): '), 'r'))
        return NormalMode(self.app)
    def kc_k(self, kp):
        self.app.loadkey(open(self.app.prompt('Filename (load key): '), 'r'))
        return NormalMode(self.app)

class ClearMode(Mode):
    def name(self):
        return 'Clear <[o]ld buffer, [k]ey>?'
    def kc_o(self, kp):
        self.app.clrobuf()
        return NormalMode(self.app)
    def kc_k(self, kp):
        self.app.clrkey()
        return NormalMode(self.app)

class MapMode(Mode):
    def name(self):
        return 'Map <from>?'
    def k_unknown(self, kp):
        if try_chr(kp) is None:
            self.echo('Not a printable character: %d/%x'%(kp, kp))
            return
        return Map2Mode(self.app, kp)

class Map2Mode(Mode):
    def __init__(self, app, kp):
        super(self, Map2Mode).__init__(app)
        self.kp = kp
    def name(self):
        return 'Map %s -> <to>?'%(chr(self.kp),)
    def k_unknown(self, kp):
        if try_chr(kp) is None:
            self.echo('Not a printable character: %d/%x'%(kp, kp))
            return
        self.app.key[chr(self.kp)] = chr(kp)
        return NormalMode(self.app)

##### Main program

Application.DEFAULT_MODE_CLS = NormalMode

def main(stdscr):
    app = Application(stdscr)
    app.loop()

if __name__ == '__main__':
    wrapper(main)
