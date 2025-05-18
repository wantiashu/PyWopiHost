#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import importlib
import sys
import tkinter as tk
from io import StringIO
import django.core.management.commands.runserver
import wopi.urls
import wopi.middleware
import wopi.views
import socket
import threading
from django.core.management import execute_from_command_line
from pathlib import Path
from daphne.cli import CommandLineInterface
import cosite.settings
import cosite.asgi
import webbrowser
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cosite.settings')

class ConsoleRedirect:
    def __init__(self, text_widget):
        self.output = text_widget

    def write(self, message):
        self.output.insert(tk.END, "[sys:]" + message)
        self.output.see(tk.END)  # Auto-scroll
        self.output.update_idletasks()

    def flush(self):
        pass  # Required for compatibility

class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.insert(tk.END, "[log:]" + msg + "\n")
        self.text_widget.see(tk.END)

def start_server():
    if len(sys.argv) == 1:
        sys.argv += ["-b", "0.0.0.0", "-p", "8000", "cosite.asgi:application"]
    CommandLineInterface.entrypoint()

def open_url():
    url = "http://127.0.0.1:8000"
    webbrowser.open(url, new=2)

def main():
    # Create the GUI window
    root = tk.Tk()
    root.title("WOPI Host")

    message_1 = tk.Message(root,
        text="Please visit 127.0.0.1:8000",
        width=500, borderwidth=0, highlightthickness=0, relief="flat",
        font=("Helvetica",18), justify="center")
    message_1.pack(padx=5, pady=0)

    message_2 = tk.Message(root,
        text="for configuration and co-authoring",
        width=500, borderwidth=0, highlightthickness=0, relief="flat",
        font=("Helvetica",16), justify="center")
    message_2.pack(padx=5, pady=0)

    open_button = tk.Button(root, text="Visit it now", command=open_url)
    open_button.pack(pady=5)

    # Redirect stdout, stderr and logging
    text_box = tk.Text(root, wrap="word", height=15, width=50)
    text_box.pack(fill="both", expand=True)
    sys.stdout = ConsoleRedirect(text_box)
    sys.stderr = ConsoleRedirect(text_box)
    text_handler = TextHandler(text_box)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    text_handler.setFormatter(formatter)
    logging.getLogger().addHandler(text_handler)
    logging.getLogger().setLevel(logging.DEBUG)

    # Start the server in a separate daemon thread.
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Start the Tkinter event loop.
    root.mainloop()

if __name__ == '__main__':
    main()
