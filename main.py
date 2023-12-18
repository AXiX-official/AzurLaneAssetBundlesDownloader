from loguru import logger

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Log, TabbedContent, Markdown, Static, Button, SelectionList
from textual.reactive import var
from textual import on
from textual.events import Mount

from gui import MD, Update_MD, LogView, InitView, FileUpdate
from downloader import Downloader


class DownloadManager(App):
    TITLE = "AzurLane AssetBundles Download Manager"
    SUB_TITLE = "Dev Version"
    CSS_PATH = "main.tcss"

    BINDINGS = [
        ("ctrl+q", "quit", "Quit")
    ]

    logs_show = var(True)

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent("README", "Update", "Init", "File Update", "Setting", id="tabbed-content"):
            yield Markdown(MD, id="readme")
            yield Markdown(Update_MD, id="update")
            yield InitView(id="init")
            yield FileUpdate(id="file-update")
            yield Static("setting", id="setting")
        yield LogView(id="logs-view")
        yield Footer()

    def on_mount(self) -> None:
        def sink(message):
            log = self.query_one(Log)
            if log:
                log.write_line(message)
                self.refresh()
        logger.add(sink, format="{message}")
        #self.auto_refresh = True
        self.dl = Downloader()
        if not self.dl.version_file_flag:
            self.query_one("#init-button").disabled = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "init-button":
            self.query_one("#init-button").disabled = True
            self.dl.download_remote_hashfiles()
            self.dl.update_version_json()
            self.dl.to_history(init_flag=True)
            return
        if event.button.id == "check-button":
            self.query_one("#check-button").disabled = True
            self.dl.check()
        if event.button.id == "download-button":
            self.query_one("#download-button").disabled = True
            l = self.query_one(SelectionList).selected
            self.dl.download_new_assetbundles(l)


        



if __name__ == "__main__":
    DownloadManager().run()
