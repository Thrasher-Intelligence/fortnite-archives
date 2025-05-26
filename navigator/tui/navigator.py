from blessed import Terminal
import os
import sys
from navigator.tui.editor import EditorTUI

term = Terminal()

class NavigatorTUI:
    def __init__(self, navigator):
        self.navigator = navigator
        self.selected = 0
        self.viewing_file = False
        self.file_content_lines = []
        self.file_line_offset = 0
        self.file_path = ""

        self.search_mode = False
        self.search_query = ""
        self.search_results = []
        self.search_selected = 0
        self.in_search_results_view = False

    def execute_search(self):
        self.search_results = []
        self.search_selected = 0
        if self.search_query.strip():
            results = self.navigator.search_locations(self.search_query)
            self.search_results = results
        self.search_mode = False
        self.in_search_results_view = len(self.search_results) > 0
        # Force redraw at current terminal size
        height, width = term.height, term.width
        self.draw(height, width)

    def run(self):
        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            height, width = term.height, term.width
            self.draw(height, width)
            while True:
                if self.search_mode:
                    key = term.inkey()
                    if key.name == 'KEY_ESCAPE':
                        self.search_mode = False
                        self.search_query = ""
                        self.search_results = []
                        self.draw(height, width)
                        continue
                    elif key.name == 'KEY_ENTER' or key == '\n':
                        self.execute_search()
                        # execute_search now handles drawing
                        continue
                    elif key.name == 'KEY_BACKSPACE':
                        self.search_query = self.search_query[:-1]
                        self.draw(height, width)
                        continue
                    else:
                        if key.is_sequence or key == '':
                            continue
                        self.search_query += key
                        self.draw(height, width)
                        continue

                key = term.inkey()

                if key.lower() == 'q':
                    break

                if key.lower() == 'f':
                    self.search_mode = True
                    self.search_query = ""
                    self.draw_search_prompt(height, width)
                    continue

                if self.viewing_file:
                    if key.name == 'KEY_UP':
                        self.scroll_file(-1, height)
                    elif key.name == 'KEY_DOWN':
                        self.scroll_file(1, height)
                    elif key.name == 'KEY_PPAGE':
                        self.scroll_file(-(height - 2), height)
                    elif key.name == 'KEY_NPAGE':
                        self.scroll_file(height - 2, height)
                    elif key.lower() == 'e':
                        self.edit_current_file()
                        self.draw(height, width)
                        continue
                    elif key.name in ('KEY_BACKSPACE', 'KEY_ESCAPE'):
                        self.viewing_file = False
                        self.draw(height, width)
                        continue

                if self.in_search_results_view:
                    if key.name == 'KEY_UP':
                        self.search_selected = max(0, self.search_selected - 1)
                    elif key.name == 'KEY_DOWN':
                        self.search_selected = min(len(self.search_results) - 1, self.search_selected + 1)
                    elif key.name == 'KEY_ENTER' or key == '\n':
                        # Instead of opening file, enter the directory selected in search results
                        selected_dir = self.search_results[self.search_selected]
                        if isinstance(selected_dir, tuple) or isinstance(selected_dir, list):
                            selected_dir = selected_dir[0]  # handle if list of tuples
                        # Set navigator current path to selected directory
                        new_path = os.path.join(self.navigator.base_dir, selected_dir)
                        if os.path.isdir(new_path):
                            self.navigator.current_path = new_path
                            self.navigator.update_entries()
                            self.selected = 0
                        self.in_search_results_view = False
                        self.search_results = []
                    elif key.name in ('KEY_BACKSPACE', 'KEY_ESCAPE'):
                        self.in_search_results_view = False
                        self.search_results = []
                        self.selected = 0
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
        if self.search_mode:
            self.draw_search_prompt(height, width)
        elif self.in_search_results_view and self.search_results:
            self.draw_search_results(height, width)
        elif self.viewing_file:
            self.draw_file_view(height, width)
        else:
            self.draw_directory_view(height, width)
        if self.viewing_file:
            print(term.move(height - 1, 0) + term.reverse(' Press q to quit, e to edit, Backspace to return ') + term.normal)
        else:
            print(term.move(height - 1, 0) + term.reverse(' Press q to quit, Enter to open, Backspace to up, f to search ') + term.normal)

    def draw_search_prompt(self, height, width):
        prompt = "Search locations: " + self.search_query
        print(term.move(height // 2, max(0, (width - len(prompt)) // 2)) + term.reverse(prompt) + term.normal)

    def draw_search_results(self, height, width):
        title = f"Search results for '{self.search_query}' (Press Backspace to cancel)"
        print(term.move(0, 0) + term.bold(title[:width]))
        if not self.search_results:
            print(term.move(2, 0) + "No results found.")
            return
            
        max_display = height - 3
        start = max(0, self.search_selected - max_display + 1) if self.search_selected >= max_display else 0
        
        for i, (chapter_season, updates) in enumerate(self.search_results[start:start + max_display]):
            focused = (start + i == self.search_selected)
            
            # Format as "chapter_x/season_y    [update1, update2, ...]"
            updates_str = f"[{', '.join(updates)}]"
            
            # Calculate available width for main text and updates
            display_width = width - 4  # Leave some margin
            
            # If combined length is too long, truncate updates list
            if len(chapter_season) + len(updates_str) + 4 > display_width:
                max_updates_width = display_width - len(chapter_season) - 8
                if max_updates_width > 10:  # Only if we have reasonable space
                    updates_str = updates_str[:max_updates_width] + "...]"
            
            # Format with updates right-aligned
            padding = display_width - len(chapter_season) - len(updates_str)
            line = chapter_season + " " * max(1, padding) + updates_str
            
            if len(line) > width:
                line = line[:width - 3] + "..."
                
            if focused:
                print(term.move(i + 1, 0) + term.reverse(line))
            else:
                print(term.move(i + 1, 0) + line)

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
        
    def edit_current_file(self):
        """Launch the editor for the current file"""
        if not self.viewing_file or not self.file_path:
            return
            
        # Exit fullscreen mode temporarily and show cursor
        print(term.normal_cursor)
        
        try:
            # Launch editor with current file content
            updated_content = EditorTUI(self.file_path, self.file_content_lines, term).run()
            
            if updated_content:
                # Save changes to file
                try:
                    with open(self.file_path, 'w') as f:
                        f.write('\n'.join(updated_content))
                    self.file_content_lines = updated_content
                except Exception as e:
                    # If we can't save, at least update the in-memory view
                    self.file_content_lines = [f"Error saving file: {str(e)}"] + updated_content
        finally:
            # Make sure we hide the cursor again when done
            print(term.hidden_cursor)