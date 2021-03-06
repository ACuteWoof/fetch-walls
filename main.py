#!/bin/python3

import gi
import os
import requests
import random
from requests import get

from threading import Thread

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, GdkPixbuf

class WallpaperFetcher:
    def __init__(self, wallpaper_folder):
        self.files = []
        self.wallpaper_folder = wallpaper_folder.replace("~", os.getenv("HOME"))

    def search(self, query, page):
        query = query.replace(" ", "%20")
        print(query)
        url = f"https://wallhaven.cc/api/v1/search?q={query}"
        print(url)
        self.search_results = get(url).json()["data"][page]["path"]
        return self.search_results

    def filter_nsfw(self):
        filtered_search_results
        for i in self.search_results:
            if i["purity"] == "sfw":
                filtered_search_results.append(i)

        self.search_results = filtered_search_results

    def get_image(self, path):
        data = self.search_results if data == None else data
        pixbuf = GdkPixbuf.Pixbuf.new_from_at_scale(
            path, width=220, height=220, preserve_aspect_ratio=True
        )
        btn = Gtk.EventBox()
        btn.connect("button-press-event", self.get_preview_image, path)

    def download_temp_image(self, path):
        for file in os.listdir(self.wallpaper_folder):
            os.system(f"rm {self.wallpaper_folder}/{file}")

        response = get(path, stream=True)
        file_name = path.split("/")[-1]
        self.files.append(file_name)
        self.file_location = f"{self.wallpaper_folder}/.temp.{file_name.split('.')[-1]}"
        with open(self.file_location, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        return self.file_location

    def copy_to_folder(self, folder, filename):
        os.system(f"cp {self.file_location} {folder}/{filename}")

envs = {
    "TEMP_WALLPAPER_FOLDER": os.getenv("TEMP_WALLPAPER_FOLDER"),
    "DOWNLOADED_WALLPAPER_FOLDER": os.getenv("DOWNLOADED_WALLPAPER_FOLDER"),
}
defaults = {
    "TEMP_WALLPAPER_FOLDER": "~/Pictures/wallpapers/.temp",
    "DOWNLOADED_WALLPAPER_FOLDER": "~/Pictures/wallpapers/download",
}

os_temp_wal = os.getenv("TEMP_WALLPAPER_FOLDER")
os_down_wal = os.getenv("DOWNLOADED_WALLPAPER_FOLDER")

os.environ["TEMP_WALLPAPER_FOLDER"] = (
    os_temp_wal if os_temp_wal != None else defaults["TEMP_WALLPAPER_FOLDER"]
)
os.environ["DOWNLOADED_WALLPAPER_FOLDER"] = (
    os_down_wal if os_down_wal != None else defaults["DOWNLOADED_WALLPAPER_FOLDER"]
)

wallpaper_folder = os.getenv("DOWNLOADED_WALLPAPER_FOLDER").replace("~", os.getenv("HOME"))
temp_wallpaper_folder = os.getenv("TEMP_WALLPAPER_FOLDER").replace("~", os.getenv("HOME"))


class App(Gtk.Window):
    def __init__(self):
        # non gtk stuff
        self.wallpaper_fetcher = WallpaperFetcher(temp_wallpaper_folder)
        self.page_number = 0
        self.query = "dog"

        # init
        super().__init__(title="Wallpaper fetcher")
        self.set_border_width(10)
        self.set_default_size(700, 400)

        # main container
        self.main_container = Gtk.Box()
        self.add(self.main_container)

        # text box and buttons
        self.wallpaper_search_query_entry = Gtk.Entry()
        self.search_btn = Gtk.Button()

        self.attach_icon("system-search-symbolic", self.search_btn)
        self.search_btn.connect(
            "clicked",
            self.handle_search_btn_click,
        )

        self.header = Gtk.HeaderBar()
        self.wallpaper_search_query_entry.set_hexpand(True)

        start_items = [self.wallpaper_search_query_entry, self.search_btn]
        for item in start_items:
            self.header.pack_start(item)

        # icons (ref gtk3-icon-browser)
        self.next_page_btn = Gtk.Button()
        self.attach_icon("go-next-symbolic", self.next_page_btn)

        self.prev_page_btn = Gtk.Button()
        self.attach_icon("go-previous-symbolic", self.prev_page_btn)

        self.save_btn = Gtk.Button()
        self.attach_icon("folder-saved-search", self.save_btn)

        self.set_wallpaper_btn = Gtk.Button()
        self.attach_icon("emblem-ok-symbolic", self.set_wallpaper_btn)

        end_items = [self.next_page_btn, self.prev_page_btn, self.save_btn]
        for item in end_items:
            self.header.pack_end(item)

        # connect all buttons
        self.next_page_btn.connect("clicked", self.move_wallpaper, "next")
        self.prev_page_btn.connect("clicked", self.move_wallpaper, "prev")
        self.save_btn.connect("clicked", self.save_wallpaper)

        # change titlebar to our header
        self.set_titlebar(self.header)

        # display last temp image
        try:
            self.current_image_location = f"{temp_wallpaper_folder}/{os.listdir(temp_wallpaper_folder)[-1]}"
            self.current_image = self.get_wallpaper_image(self.current_image_location)
            self.display_wall(self.current_image)
        except:
            pass
    
        self.show_all()

    def attach_icon(self, icon_name, button):
        icon = Gio.ThemedIcon(name=icon_name)
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        return button

    def move_wallpaper(self, _btn, pos):
        if pos == "next":
            self.page_number += 1
        if pos == "prev":
            self.page_number -= 1

        # create and start the thread! lesgooo
        thread = Thread(
            target=self.handle_search_btn_click_threaded_functions,
            args=self.query,
            daemon=True,
        )
        thread.start()

    def get_wallpaper_image(self, wallpaper):
        # make a pixbuf from the file so we can have some more control than plain Gtk.Image
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            wallpaper,
            width=self.get_size()[0],
            height=self.get_size()[1],
            preserve_aspect_ratio=True,
        )
        image = Gtk.Image()
        image.set_from_pixbuf(pixbuf)
        return image

    def remove_all_elements(self, parent):
        for child in parent.get_children():
            parent.remove(child)

    def display_wall(self, image):
        # remove all elements of main container
        self.remove_all_elements(self.main_container)
        # add the image to the main container
        self.main_container.add(image)
        self.show_all()

    def handle_search_btn_click_threaded_functions(self, query, *_):
        self.wallpaper_online_path = self.wallpaper_fetcher.search(
            query, self.page_number
        )  # get the url of the wallpaper
        self.wallpaper_location = self.wallpaper_fetcher.download_temp_image(
            self.wallpaper_online_path
        )  # we cant directly use url to make an image so we gotta download this lmao
        self.current_image = self.get_wallpaper_image(self.wallpaper_location)
        self.display_wall(self.current_image)  # and then view the image! lesgooo

    def handle_search_btn_click(self, *_):
        self.query = (
            self.wallpaper_search_query_entry.get_text(),
        )  # get the text and store this in a tuple.
        thread = Thread(
            target=self.handle_search_btn_click_threaded_functions,
            args=self.query,
            daemon=True,
        )
        thread.start()

    def save_wallpaper(self, *_):
        print(wallpaper_folder)
        filenames = next(os.walk(wallpaper_folder), (None, None, []))[2]
        filenames.sort()
        last_file_name = "0000"
        try:
            print(int(filenames[-1].split(".")[0]))
            last_file_name = filenames[-1].split(".")[0]
            filename = str(int(last_file_name) + 1)
            number_of_0s = 4 - len(filename)
            if number_of_0s >= 0:
                filename = number_of_0s*"0" + filename
        finally:
            self.wallpaper_fetcher.copy_to_folder(
                wallpaper_folder,
                f"{filename}.{self.wallpaper_fetcher.file_location.split('.')[-1]}",
            )


### SCRIPT HANDLING STUFF ###
def main():
    win = App()
    win.connect("destroy", Gtk.main_quit)
    win.show()
    Gtk.main()


if __name__ == "__main__":
    main()
