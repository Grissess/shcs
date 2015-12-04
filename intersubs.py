# Interactive monoalphabetic substitution tool
import sys
import traceback
import curses
from curses import wrapper

from trans import trans

##### Support

logfile = open('log.txt', 'w', 0)

def log(*args):
    for arg in args:
        if isinstance(arg, str):
            logfile.write(arg+' ')
        else:
            logfile.write(repr(arg)+' ')
    logfile.write('\n')

class Application(object):
    DEFAULT_MODE_CLS = None  # Set later
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.stdscr.keypad(1)
        self.key = {}
        self.obuf = None
        self.nbuf = None
        self.scroll = [0, 0]
        self.mode = self.DEFAULT_MODE_CLS(self)
        self.echotxt = ''
        self.running = True
        self.layout()
    def quit(self):
        self.running = False
    def layout(self):
        self.sh, self.sw = self.stdscr.getmaxyx()
        self.obufwin = self.stdscr.subwin(self.sh - 4, self.sw / 2, 0, 0)
        self.nbufwin = self.stdscr.subwin(self.sh - 4, self.sw - self.sw / 2, 0, self.sw / 2)
        self.keywin = self.stdscr.subwin(2, self.sw, self.sh - 4, 0)
        self.modewin = self.stdscr.subwin(1, self.sw, self.sh - 2, 0)
        self.statwin = self.stdscr.subwin(1, self.sw, self.sh - 1, 0)
    def getobuf(self):
        return self.obuf.instr(0, 0)
    def getnbuf(self):
        return trans(self.getobuf(), self.key)
    def scrx(self, dx):
        h, w = self.obuf.getmaxyx()
        wh, ww = self.obufwin.getmaxyx()
        if self.scroll[0] + dx < 0:
            self.scroll[0] = 0
        elif self.scroll[0] + dx > w - ww:
            self.scroll[0] = w - ww
        else:
            self.scroll[0] += dx
    def scry(self, dy):
        h, w = self.obuf.getmaxyx()
        wh, ww = self.obufwin.getmaxyx()
        if self.scroll[1] + dy < 0:
            self.scroll[1] = 0
        elif self.scroll[1] + dy > h - wh:
            self.scroll[1] = h - wh
        else:
            self.scroll[1] += dy
    def wclear(self):
        self.stdscr.clear()
    def wblit(self, win, txt=None, sx=0, sy=0):
        if txt is not None:
            win.clear()
            win.addstr(0, 0, txt)
        by, bx = win.getbegyx()
        my, mx = win.getmaxyx()
        win.overwrite(self.stdscr, sx, sy, by, bx, my, mx)
        log('Blitting window', win, 'begin', (by, bx), 'max', (my, mx), 'text', txt, 'to', (sx, sy))
        self.stdscr.noutrefresh()
    def update(self, echotxt=''):
        self.wclear()
        try:
            self.modewin.erase()
            self.modewin.addstr(0, 0, self.mode.name())
            self.modewin.noutrefresh()
            ##self.wblit(self.modewin, self.mode.name())
            self.statwin.erase()
            self.statwin.addstr(0, 0, echotxt)
            self.statwin.noutrefresh()
            ##self.wblit(self.statwin, echotxt)
            self.keywin.erase()
            items = sorted(self.key.items(), key=lambda pair: pair[0])
            for idx, pair in enumerate(items):
                self.keywin.addstr(0, idx, pair[0])
                self.keywin.addstr(1, idx, pair[1])
            self.keywin.noutrefresh()
            ##self.wblit(self.keywin)
            self.obufwin.erase()
            self.nbufwin.erase()
            self.obufwin.border()
            self.nbufwin.border()
            if self.obuf is not None:
                if self.nbuf is None:
                    self.nbuf = curses.newpad(*self.obuf.getmaxyx())
                self.nbuf.erase()
                self.nbuf.addstr(0, 0, self.getnbuf())
                by, bx = self.obufwin.getbegyx()
                my, mx = self.obufwin.getmaxyx()
                self.obuf.overwrite(self.obufwin, 1+self.scroll[0], 1+self.scroll[1], by, bx, my, mx)
                ##self.obuf.overwrite(self.obufwin)
                ##self.obuf.refresh(self.scroll[0], self.scroll[1], by, bx, my, mx)
                by, bx = self.nbufwin.getbegyx()
                my, mx = self.nbufwin.getmaxyx()
                self.nbuf.overwrite(self.nbufwin, 1+self.scroll[0], 1+self.scroll[1], by, bx, my, mx)
                ##self.nbuf.overwrite(self.nbufwin)
                ##self.nbuf.refresh(self.scroll[0], self.scroll[1], by, bx, my, mx)
            self.obufwin.noutrefresh()
            self.nbufwin.noutrefresh()
            ##self.wblit(self.obufwin, self.getobuf(), self.scroll[0], self.scroll[1])
            ##self.wblit(self.nbufwin, self.getnbuf(), self.scroll[0], self.scroll[1])
        except Exception as e:
            log(traceback.format_exc())
            self.statwin.erase()
            self.statwin.addstr(0, 0, 'Update error occurred: %r'%(e,))
            self.statwin.noutrefresh()
        curses.doupdate()
    def loadobuf(self, f):
        val = f.read()
        log('Read:', val)
        lines = val.count('\n')
        log('...lines:', lines)
        self.obuf = curses.newpad(2 * lines, self.sw)
        self.obuf.addstr(val)
        log('New pad dims:', self.obuf.getmaxyx())
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
        buf = ''
        ch = self.statwin.getkey()
        while ch != '\n':
            if ch == '\x7f':
                buf = buf[:-1]
            else:
                buf += ch
            self.statwin.erase()
            self.statwin.move(0, 0)
            self.statwin.addstr(prompt+buf)
            ch = self.statwin.getkey()
        return buf
    def loop(self):
        while self.running:
            self.update(self.echotxt)
            self.clrstat()
            kp = self.stdscr.getch()
            if kp == 0x1b:
                self.mode = self.DEFAULT_MODE_CLS(self)
                continue
            try:
                res = self.mode(kp)
            except Exception as e:
                log(traceback.format_exc())
                self.echo('Error occurred: %r'%(e,))
            else:
                if res is not None:
                    self.mode = res

def try_chr(i):
    try:
        return chr(i)
    except ValueError:
        return None

class Mode(object):
    def __init__(self, app):
        self.app = app
    def __call__(self, kp):
        val = getattr(self, 'kd_%d'%(kp,), None)
        if val is None:
            val = getattr(self, 'kx_%x'%(kp,), None)
        if val is None:
            val = getattr(self, 'kc_%s'%(try_chr(kp),), None)
        if val is None:
            val = self.k_unknown
        return val(kp)
    def k_unknown(self, kp):
        self.app.echo('Unknown keypress: %d/%x'%(kp, kp))
    def name(self):
        return repr(self)

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
    def kc_M(self, kp):
        return SpecialMapMode(self.app)
    def kx_102(self, kp):
        self.app.scry(1)
    def kx_103(self, kp):
        self.app.scry(-1)
    def kx_104(self, kp):
        self.app.scrx(-1)
    def kx_105(self, kp):
        self.app.scrx(1)

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

class SpecialMapMode(Mode):
    def name(self):
        return 'Map special <[l]owercase identity, [u]ppercase identity, [d]igit identity, [a]ll identity>?'
    def kc_l(self, kp):
        for c in 'abcdefghijklmnopqrstuvwxyz':
            self.app.key[c] = c
        return NormalMode(self.app)
    def kc_u(self, kp):
        for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            self.app.key[c] = c
        return NormalMode(self.app)
    def kc_d(self, kp):
        for c in '0123456789':
            self.app.key[c] = c
        return NormalMode(self.app)
    def kc_a(self, kp):
        for c in range(256):
            self.app.key[chr(c)] = chr(c)
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
        super(Map2Mode, self).__init__(app)
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
