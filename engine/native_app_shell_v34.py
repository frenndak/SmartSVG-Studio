"""Shared native window and retained workspace navigation (V34-041/046 subset).

Injected Tk APIs keep the isolated bootstrap independent of a GUI session.
This shell owns display state only: no archive reader, writer or job launcher.
"""
from __future__ import annotations


class NativeAppShell:
    """One window; registered workspaces keep their widgets and local drafts."""

    def __init__(self, root, tk, ttk):
        self.root, self.ttk = root, ttk
        self.pages = {}
        self.buttons = {}
        self.labels = {}
        self.active_page = None
        root.title('SmartSVG Studio V3.4 — prototype autonome')
        root.geometry('1100x760')
        root.minsize(900, 650)
        frame = ttk.Frame(root, padding=16)
        frame.pack(fill='both', expand=True)
        header = ttk.Frame(frame)
        header.pack(fill='x', pady=(0, 12))
        ttk.Label(header, text='SmartSVG Studio', font=('Segoe UI', 20, 'bold')).pack(anchor='w')
        ttk.Label(header, text='Votre espace de création local · prototype autonome sans ComfyUI',
                  wraplength=760).pack(anchor='w', pady=4)
        # Reserve the capability notice before packing the expanding work area.
        footer = ttk.Frame(frame)
        footer.pack(side='bottom', fill='x', pady=(10, 0))
        ttk.Separator(footer).pack(fill='x', pady=(0, 6))
        ttk.Label(footer, text=(
            'Projet en lecture seule · gabarits théoriques sans export · sans IA\n'
            'Édition, sauvegarde et installation Windows : intégration à venir.'),
            wraplength=820).pack(anchor='w')
        body = ttk.Frame(frame)
        body.pack(fill='both', expand=True)
        self.navigation = ttk.Frame(body, padding=(0, 0, 16, 0))
        self.navigation.pack(side='left', fill='y')
        ttk.Label(self.navigation, text='ESPACES', font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 10))
        self.content = ttk.Frame(body)
        self.content.pack(side='left', fill='both', expand=True)
        ttk.Label(self.navigation, text='Ctrl+1 à Ctrl+4\npour naviguer\nCtrl+O : ouvrir\nF5 : réexaminer',
                  wraplength=140).pack(side='bottom', anchor='w', pady=12)

    def add_page(self, key, label):
        """Register content once; the caller mounts its existing tool in it."""
        if key in self.pages:
            raise ValueError('Workspace already registered')
        page = self.ttk.Frame(self.content, padding=(12, 0, 0, 0))
        button = self.ttk.Button(self.navigation, text=label, width=16,
                                 command=lambda: self.show(key, focus=True))
        button.pack(fill='x', pady=4)
        self.pages[key], self.buttons[key], self.labels[key] = page, button, label
        number = len(self.pages)
        if number <= 4:
            self.root.bind(f'<Control-Key-{number}>', lambda _event, target=key: self.show(target, focus=True))
        return page

    def show(self, key, *, focus=False):
        """Change visibility only; even re-selecting a page has no tool effects."""
        if key not in self.pages:
            raise ValueError('Unknown workspace')
        if self.active_page != key:
            if self.active_page is not None:
                self.pages[self.active_page].pack_forget()
                self.buttons[self.active_page].configure(text=self.labels[self.active_page])
            self.pages[key].pack(fill='both', expand=True)
            self.buttons[key].configure(text='› ' + self.labels[key])
            self.active_page = key
        if focus:
            self.buttons[key].focus_set()
        return 'break'
