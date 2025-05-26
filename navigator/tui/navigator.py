from blessed import Terminal
import os

term = Terminal()

class NavigatorTUI:
    def __init__(self, navigator):
        self.navigator = navigator
        self.selected = 0
        self.viewing_file = False
        self.file_content_lines = []
        self.file_line_offset = 0
        self.file_path = ""

    def run(self):
        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            height, width = term.height, term.width
            self.draw(height, width)
            while True:
                key = term.inkey()

                if key.lower() == 'q':
                    break

                if self.viewing_file:
                    if key.name == 'KEY_UP':
                        self.scroll_file(-1, height)
                    elif key.name == 'KEY_DOWN':
                        self.scroll_file(1, height)
                    elif key.name == 'KEY_PPAGE':
                        self.scroll_file(-(height - 2), height)
                    elif key.name == 'KEY_NPAGE':
                        self.scroll_file(height - 2, height)
                    elif key.name in ('KEY_BACKSPACE', 'KEY_ESCAPE'):
                        self.viewing_file = False
                    self.draw(height, width)
                    continue

                if key.name == 'KEY_UP':
                    self.selected = max(0, self.selected - 1)
                elif key.name == 'KEY_DOWN':
                    self.selected = min(len(self.navigator.entries) - 1, self.selected + 1)
                elif key.name == 'KEY_ENTER' or key == '\n':
                    res = self.navigator.enter(self.selected)
                    if res:
                        # Viewing a JSON file, read contents
                        self.file_content_lines = self.navigator.read_file(res)
                        self.file_line_offset = 0
                        self.file_path = res
                        self.viewing_file = True
                    else:
                        # Directory changed, reset selection
                        self.selected = 0
                elif key.name == 'KEY_BACKSPACE':
                    self.navigator.go_up()
                    self.selected = 0
                self.draw(height, width)

    def draw(self, height, width):
        print(term.home + term.clear)
        if self.viewing_file:
            self.draw_file_view(height, width)
        else:
            self.draw_directory_view(height, width)
        print(term.move(height - 1, 0) + term.reverse(' Press q to quit, Enter to open, Backspace to up ') + term.normal)

    def draw_directory_view(self, height, width):
        title = f'Directory: {self.navigator.current_path}'
        print(term.move(0, 0) + term.bold(title[:width]))
        max_display = height - 2
        start = max(0, self.selected - max_display + 1) if self.selected >= max_display else 0
        for i, entry in enumerate(self.navigator.entries[start:start+max_display]):
            focused = (start + i == self.selected)
            entry_path = os.path.join(self.navigator.current_path, entry if entry != '..' else os.pardir)
            line = entry + ('/' if os.path.isdir(entry_path) else '')
            if focused:
                print(term.move(i+1, 0) + term.reverse(line[:width]))
            else:
                print(term.move(i+1, 0) + line[:width])

    def draw_file_view(self, height, width):
        title = f'Viewing file: {self.file_path}'
        print(term.move(0, 0) + term.bold(title[:width]))
        max_display = height - 2
        lines_to_show = self.file_content_lines[self.file_line_offset:self.file_line_offset + max_display]
        for i, line in enumerate(lines_to_show):
            if len(line) > width:
                line = line[:width-3] + '...'
            print(term.move(i + 1, 0) + line)
        status = f'Lines {self.file_line_offset + 1} - {min(self.file_line_offset + max_display, len(self.file_content_lines))} of {len(self.file_content_lines)}'
        print(term.move(height - 1, 0) + term.reverse(status.ljust(width)) + term.normal)

    def scroll_file(self, direction, height):
        max_display = height - 2
        new_offset = self.file_line_offset + direction
        if new_offset < 0:
            new_offset = 0
        elif new_offset > max(0, len(self.file_content_lines) - max_display):
            new_offset = max(0, len(self.file_content_lines) - max_display)
        self.file_line_offset = new_offset