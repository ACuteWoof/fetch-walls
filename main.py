#!/bin/python3

import gi
import os
import requests
import random

from threading import Thread
from fetcher import WallpaperFetcher

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Gio

if os.getenv("TEMP_WALLPAPER_FOLDER") == None:
    os.environ["TEMP_WALLPAPER_FOLDER"] = "~/Pictures/wallpapers/.temp"

wallpaper_folder = os.getenv("TEMP_WALLPAPER_FOLDER")

### TODO: Add buttons on the header to scroll between images using page numbers as self.page_number


class Window(Gtk.Window):
    def __init__(self):
        self.wallpaper_fetcher = WallpaperFetcher(wallpaper_folder)

        super().__init__(title="Wallpaper fetcher")
        self.set_border_width(10)
        self.set_default_size(700, 400)

        self.wallpaper_search_query_entry = Gtk.Entry()
        self.search_btn = Gtk.Button()
        icon = Gio.ThemedIcon(name="system-search-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        self.search_btn.add(image)
        self.search_btn.connect(
            "clicked",
            self.handle_search_btn_click,
        )

        self.header = Gtk.HeaderBar()
        self.header.add(self.wallpaper_search_query_entry)
        self.header.add(self.search_btn)
        self.wallpaper_search_query_entry.set_hexpand(True)

        self.set_titlebar(self.header)

        self.show_all()

    def get_wallpaper_image(self, wallpaper):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            wallpaper,
            width=self.get_size()[0],
            height=self.get_size()[1],
            preserve_aspect_ratio=True,
        )

        image = Gtk.Image()
        image.set_from_pixbuf(pixbuf)
        return image

    def display_wall(self, image):
        self.add(image)
        self.show_all()

    def handle_search_btn_click_threaded_functions(self, query, *_):
        wallpaper_online_path = self.wallpaper_fetcher.search(query, 0)
        wallpaper_location = self.wallpaper_fetcher.download_image(
            wallpaper_online_path
        )
        wallpaper_preview = self.display_wall(
            self.get_wallpaper_image(wallpaper_location)
        )

    def handle_search_btn_click(self, *_):
        query = (self.wallpaper_search_query_entry.get_text(),)
        thread = Thread(
            target=self.handle_search_btn_click_threaded_functions,
            args=query,
            daemon=True,
        )
        thread.start()


###
def main():
    win = Window()
    win.connect("destroy", Gtk.main_quit)
    win.show()
    Gtk.main()


if __name__ == "__main__":
    main()
