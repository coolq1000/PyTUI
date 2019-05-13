
import curses, time

class Widget:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        self.SCREEN = None
        self.FOCUS  = False

    def init  (self): pass
    def update(self): pass
    def draw  (self): pass
    def event (self, event): pass

class Dropdown(Widget):

    def __init__(self, *args, **kwargs):
        self.X, self.Y = None, None
        self.ENTRIES = []
        self.SELECTED = 0
        return super().__init__(*args, **kwargs)

    def init(self, title, x, y):
        self.title = title
        self.X = x
        self.Y = y
    
    def event(self, event):
        if self.FOCUS:
            if event == curses.KEY_UP:
                self.SELECTED = (self.SELECTED + 1) % len(self.ENTRIES)
            
            elif event == curses.KEY_DOWN:
                self.SELECTED = (self.SELECTED - 1) % len(self.ENTRIES)
            
            elif event == curses.KEY_ENTER or event == 10:
                callback = self.ENTRIES[self.SELECTED][1]
                
                if callback:
                    self.ENTRIES[self.SELECTED][1]()
    
    def update(self):
        if not self.FOCUS:
            self.SELECTED = 0

    def draw(self):

        if not self.FOCUS:
            self.SCREEN.screen.attron(curses.A_UNDERLINE)
        self.SCREEN.write_at(self.title, self.X, self.Y)
        if not self.FOCUS:
            self.SCREEN.screen.attroff(curses.A_UNDERLINE)

        if self.FOCUS:
            if self.ENTRIES:
                w = max([len(x[0]) for x in self.ENTRIES])
            else:
                w = 3

            self.SCREEN.write_at('{}{}{}'.format('+', '-'*w, '+'), self.X, self.Y + 1)

            if self.ENTRIES:
                for i, entry in enumerate(self.ENTRIES):
                    text = '{}{}'.format(entry[0], ' '*(w - len(entry[0])))
                    self.SCREEN.write_at('|', self.X, self.Y + i + 2)
                    if i == self.SELECTED:
                        self.SCREEN.screen.attron(curses.A_REVERSE)
                    self.SCREEN.write_at(text, self.X + 1, self.Y + i + 2)
                    if i == self.SELECTED:
                        self.SCREEN.screen.attroff(curses.A_REVERSE)
                    self.SCREEN.write_at('|', self.X + len(text) + 1, self.Y + i + 2)

            self.SCREEN.write_at('{}{}{}'.format('+', '-'*w, '+'), self.X, self.Y + len(self.ENTRIES) + 2)
    
    def add_entry(self, text, callback=None):
        self.ENTRIES.append([text, callback])

class Screen:

    FORCE_RES = False
    WIDTH, HEIGHT = None, None
    FPS = -1

    SCENE = []
    FOCUSED = None

    def __init__(self, w=None, h=None):
        self.screen = curses.initscr()

        self.screen.timeout(1000 // self.FPS)
        curses.cbreak()
        curses.noecho()
        self.screen.keypad(True)

        sy, sx = self.screen.getmaxyx()
        if w is None:
            w = sx

        if h is None:
            h = sy
        
        if w is None or h is None:
            self.FORCE_RES = True
        
        self.WIDTH, self.HEIGHT = w, h

        self.resize(self.WIDTH, self.HEIGHT)

        self.init()
        self.mainloop()
    
    def init  (self): pass
    def update(self): pass
    def draw  (self): pass
    
    def event(self):
        event = self.screen.getch()
        curses.flushinp()

        if event == ord('q'):
            exit()
        
        elif event == ord('\t'):
            self.focus_next()
        
        for widget in self.SCENE:
            widget.event(event)

    def resize(self, w, h):
        try:
            curses.resize_term(h, w)
        except curses.error:
            pass

    def clear(self):
        self.screen.clear()

    def set_at(self, char, x, y):
        try:
            self.screen.addch(y, x, char)
        except curses.error:
            pass
    
    def write_at(self, s, x, y):
        for i, char in enumerate(s):
            self.set_at(char, x + i, y)

    def add_widget(self, widget):
        widget.SCREEN = self
        self.SCENE.append(widget)
        widget.init(*widget.args, **widget.kwargs)

    def cycle(self):

        for i, widget in enumerate(self.SCENE):
            self.SCENE[i].FOCUS = i == self.FOCUSED
            widget.update()

        self.update()
        self.clear()

        for widget in self.SCENE:
            widget.draw()

        self.draw()
        self.screen.refresh()

        if not self.FORCE_RES:
            self.resize(0, 0)
            sy, sx = self.screen.getmaxyx()
            self.WIDTH, self.HEIGHT = sx, sy
            self.resize(self.WIDTH, self.HEIGHT)

        self.event()
    
    def focus_next(self):
        if self.FOCUSED == None:
            self.FOCUSED = 0
        else:
            self.FOCUSED += 1
        if self.FOCUSED >= len(self.SCENE):
            self.FOCUSED = None

    def mainloop(self):
        while True:
            self.cycle()
