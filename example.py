
import PyTUI as tui

class App(tui.Screen):

    def init(self):
        dd = tui.Dropdown('File', 10, 10)
        dd.add_entry('Save', lambda: exit())
        dd.add_entry('Open')
        self.add_widget(
            dd
        )

        dd = tui.Dropdown('View', 15, 10)
        dd.add_entry('Show editor')
        dd.add_entry('Hide debugger')
        self.add_widget(
            dd
        )

App()
