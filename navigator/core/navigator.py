import os

class FileNavigator:
    def __init__(self, base_dir):
        self.base_dir = os.path.abspath(base_dir)
        self.current_path = self.base_dir
        self.entries = []

    def update_entries(self):
        try:
            entries = os.listdir(self.current_path)
            entries.sort(key=lambda e: (not os.path.isdir(os.path.join(self.current_path, e)), e.lower()))
            if self.current_path == self.base_dir:
                # Filter to only chapter_x directories at top level
                entries = [e for e in entries if os.path.isdir(os.path.join(self.current_path, e)) and e.startswith('chapter_')]
                self.entries = entries
            else:
                self.entries = ['..'] + entries
        except PermissionError:
            self.entries = []
    
    def go_up(self):
        if self.current_path != self.base_dir:
            self.current_path = os.path.dirname(self.current_path)
            self.update_entries()

    def enter(self, selected_index):
        if selected_index < 0 or selected_index >= len(self.entries):
            return None
        entry = self.entries[selected_index]
        if entry == '..':
            self.go_up()
            return None
        path = os.path.join(self.current_path, entry)
        if os.path.isdir(path):
            self.current_path = path
            self.update_entries()
            return None
        elif path.endswith('.json') and os.path.isfile(path):
            return path
        return None

    def read_file(self, path):
        try:
            with open(path, 'r') as f:
                content = f.read()
            return content.splitlines()
        except Exception as e:
            return [f'Error reading file: {e}']