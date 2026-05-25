import asyncio
import threading
from turtle import update

import mistune
import ollama
from gi.repository import GLib, Gtk, WebKit

loop = asyncio.new_event_loop()

md_css = """/* General body styling */
body {
    margin: 0;
    padding: 16px; /* Some spacing from edges */
    background-color: #1e1e1e; /* Dark background matching Adwaita dark theme */
    color: #dcdcdc; /* Light text color for good contrast */
}

/* Markdown-specific styles */
h1, h2, h3, h4, h5, h6 {
    margin-top: 24px;
    margin-bottom: 12px;
    font-weight: bold;
}

p {
    line-height: 1.6;
}

a {
    color: #cfefff; /* Light blue for links */
    text-decoration: underline;
}

code {
    background-color: #2b2b2b; /* Dark background for code blocks */
    padding: 2px 4px;
    border-radius: 3px;
    font-family: monospace, sans-serif;
    color: #f0f0f0; /* Light gray for code text */
}

pre {
    background-color: #2b2b2b; /* Dark background for pre blocks */
    padding: 10px;
    border-radius: 4px;
    overflow-x: auto;
    font-family: monospace, sans-serif;
    color: #f0f0f0; /* Light gray for code text inside pre */
}

/* List styles */
ul, ol {
    margin-left: 20px;
    padding-left: 0;
}

li {
    line-height: 1.6;
}

/* Table styles */
table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 12px;
    margin-bottom: 12px;
}

th, td {
    border: 1px solid #444444;
    padding: 8px;
    text-align: left;
    background-color: #2b2b2b; /* Dark cell background */
}

/* Ensure images are responsive and have appropriate borders */
img {
    max-width: 100%;
    margin-bottom: 12px;
    border: 1px solid #444444;
    }
"""


def run_loop():
    # run asyncio loop and wait forever
    threading.Thread(target=loop.run_forever, daemon=True).start()


run_loop()


def webview_set_md(md, webview):
    html_response = mistune.html(md)
    html = (
        f"<html><head><style>{md_css}</style></head><body>{html_response}</body></html>"
    )
    webview.load_html(html)


# Source - https://stackoverflow.com/a/78897167
# Posted by user4815162342, modified by community. See post 'Timeline' for change history
# Retrieved 2026-05-25, License - CC BY-SA 4.0


async def chat_task(stream, webview):

    # Update once with this text
    GLib.idle_add(lambda: webview_set_md("Awaiting response...", webview))
    response = ""
    # Update as new chunks come in
    for chunk in stream:
        response += chunk["message"]["content"]
        html_response = mistune.html(response)
        html = f"<html><head><style>{md_css}</style></head><body>{html_response}</body></html>"
        # webview_set_md(html)
        GLib.idle_add(lambda: webview_set_md(html, webview))

    return response


"""
Renders a message response in a webview widget. This function is intended to be called from the main thread.
:param stream: The stream object containing the message data, from ollama.chat()
:param webview: The webview widget where the message will be rendered.
:return: None.
"""


def render_message_response(stream, webview, on_finished=lambda _: None):
    fut = asyncio.run_coroutine_threadsafe(chat_task(stream, webview), loop)
    fut.add_done_callback(lambda _: GLib.idle_add(lambda: on_finished(fut.result())))


def build_webview_widget():
    webview = WebKit.WebView(hexpand=True, vexpand=True)
    frame = Gtk.Frame(hexpand=True, vexpand=True)
    frame.set_child(webview)
    return frame
