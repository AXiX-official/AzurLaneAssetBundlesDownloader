from threading import Thread
from loguru import logger

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Log, TabbedContent, Markdown, Static, Button, SelectionList, ProgressBar, Label
from textual.reactive import var
from textual import on
from textual.events import Mount

from ui import MD, Update_MD, LogView, InitView, FileUpdate
from downloader import Downloader


class DownloadManager(App):
    TITLE = "AzurLane AssetBundles Download Manager"
    SUB_TITLE = "Dev Version"
    CSS_PATH = "main.tcss"

    BINDINGS = [
        ("ctrl+q", "quit", "Quit")
    ]

    logs_show = var(True)
    need_file_update = var(True)

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
        else:
            self.query_one("#init-label").update("No need to init")
            self.query_one("#init-progressbar").visible = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        buttons = self.query(Button)
        original_states = {button.id: button.disabled for button in buttons}

        for button in buttons:
            button.disabled = True

        if event.button.id == "init-button":
            original_states["init-button"] = True

            label = self.query_one("#init-label")
            label.update("Initing...")

            button_react_thread = Thread(target=self.init_thread)
            button_react_thread.start()

        elif event.button.id == "check-button":
            original_states["check-button"] = True
            original_states["download-button"] = False

            label = self.query_one("#file-update-label")
            label.update("Checking...")

            button_react_thread = Thread(target=self.check_thread)
            button_react_thread.start()

        elif event.button.id == "download-button":
            original_states["download-button"] = True

            label = self.query_one("#file-update-label")
            label.update("Downloading...")

            l = self.query_one(SelectionList).selected

            button_react_thread = Thread(target=self.download_thread, args=(l,))
            button_react_thread.start()
        
        for button_id, original_state in original_states.items():
            button = self.query_one(f"#{button_id}")
            wait_thread = Thread(target=self.wait_and_update, args=(button_react_thread, button_id, original_state))
            wait_thread.start()
    
    def init_thread(self):
        pb = self.query_one("#init-progressbar")
        label = self.query_one("#init-label")

        pb.update(total=8)

        for i in self.dl.download_remote_hashfiles():
            label.update(i)
            pb.advance(1)
        self.notify("Hashfiles downloaded")
        self.dl.update_version_json()
        self.notify("Version json updated")
        self.dl.to_history(init_flag=True)
        self.notify("History updated")

    def check_thread(self):
        pb = self.query_one("#file-update-progressbar")
        label = self.query_one("#file-update-label")

        pb.update(total=16)

        for i in self.dl.check():
            if i.startswith("info:"):
                self.notify(i[5:])
            elif i.startswith("warn:"):
                self.notify(i[5:],severity="warning",title="No need to update")
                self.need_file_update = False
                return
            else:
                label.update(i)
                pb.advance(1)

    def download_thread(self, l):
        pb = self.query_one("#file-update-progressbar")
        label = self.query_one("#file-update-label")

        file_num = sum(self.dl.diff_list[i] for i in l)

        pb.update(total=file_num, progress=0)

        for i in self.dl.download_new_assetbundles(l):
            if i.startswith("info:"):
                self.notify(i[5:])
            else:
                label.update(i)
                pb.advance(1)



    def wait_and_update(self, test_thread, button_id, original_state):
        test_thread.join()
        button = self.query_one(f"#{button_id}")
        if button:
            button.disabled = original_state
        if not self.need_file_update:
            self.query_one("#download-button").disabled = True


if __name__ == "__main__":
    DownloadManager().run()
