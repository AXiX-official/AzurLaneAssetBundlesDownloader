import os

from textual.app import ComposeResult
from textual.containers import VerticalScroll, HorizontalScroll, Container
from textual.widget import Widget
from textual.widgets import Static, Log, Markdown, Button, SelectionList, ProgressBar, Label
from textual.reactive import Reactive

path = os.path.dirname(__file__)
path = os.path.join(path, "md")

MD = open("README.md", "r", encoding="utf-8").read()
Update_MD = open(os.path.join(path, "update.md"), "r", encoding="utf-8").read()
Init_MD = open(os.path.join(path, "init.md"), "r", encoding="utf-8").read()
FileUpdate_MD = open(os.path.join(path, "file_update.md"), "r", encoding="utf-8").read()


class LogView(Widget):
    DEFAULT_CSS = """
    LogView {
        height: 7;
        layout: vertical;
    }
    #logs-tittle {
    height: 1;
    }
    .logs-tittle-style{
        color: red;
        background: #add8e6;
    }
    #logs {

        height: 6;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("·Logs", id="logs-title", classes="logs-tittle-style")
        yield Log(id="logs")


class InitView(HorizontalScroll):
    DEFAULT_CSS = """
    #init-md {
        width: 1fr;
    }
    #init-button-container {
        width: 2fr;
    }
    """

    def compose(self) -> ComposeResult:
        yield Markdown(Init_MD, id="init-md")
        with Container(id="init-button-container"):
            yield Button("Init", id="init-button", disabled=True)
            yield Label("Progress Bar",id="init-label")
            yield ProgressBar(id="init-progressbar", show_eta=True)

class FileUpdate(HorizontalScroll):
    DEFAULT_CSS = """
    #md {
        width: 1fr;
        height: 100%;
        overflow: scroll;
    }
    #file-update-container {
        width: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        yield Markdown(FileUpdate_MD, id="md")
        with Container(id="file-update-container"):
            yield SelectionList[int](  
                ("az", 0, True),
                ("cv", 1, True),
                ("l2d", 2, True),
                ("pic", 3, True),
                ("bgm", 4, True),
                ("painting", 5, True),
                ("manga", 6, True),
                ("ciper", 7, True),
                id="file-update-selectionlist",
            )
            with HorizontalScroll(id="buttons"):
                yield Button("Check", id="check-button")
                yield Button("Download", id="download-button", disabled=True)
            yield Label("Progress Bar",id="file-update-label")
            yield ProgressBar(id="file-update-progressbar", show_eta=True)
