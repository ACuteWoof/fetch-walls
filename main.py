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
        # non gtk stuff
        self.wallpaper_fetcher = WallpaperFetcher(wallpaper_folder)
        self.page_number = 0

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

        icon = Gio.ThemedIcon(name="go-next-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        self.next_page_btn = Gtk.Button()
        self.next_page_btn.add(image)

        icon = Gio.ThemedIcon(name="go-previous-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        self.prev_page_btn = Gtk.Button()
        self.prev_page_btn.add(image)

        self.header.pack_end(self.next_page_btn)
        self.header.pack_end(self.prev_page_btn)

        self.next_page_btn.connect("clicked", self.move_wallpaper, "next")
        self.prev_page_btn.connect("clicked", self.move_wallpaper, "prev")

        self.set_titlebar(self.header)

        self.show_all()

    def move_wallpaper(self, _btn, pos):
        if pos == "next":
            self.page_number += 1
        if pos == "prev":
            self.page_number -= 1
        
        # and then create and start the thread! lesgooo
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
        for child in parent:
            parent.remove(child)

    def display_wall(self, image):
        # remove all elements of main container
        remove_all_elements(self.main_container)
        # add the image to the main container
        self.main_container.add(image)
        self.show_all()

    def handle_search_btn_click_threaded_functions(self, query, *_):
        wallpaper_online_path = self.wallpaper_fetcher.search(query, self.page_number) # get the url of the wallpaper
        wallpaper_location = self.wallpaper_fetcher.download_image(
            wallpaper_online_path
        ) # we cant directly use url to make an image so we gotta download this lmao
        wallpaper_preview = self.display_wall(
            self.get_wallpaper_image(wallpaper_location)
        ) # and then view the image! lesgooo

    def handle_search_btn_click(self, *_):
        self.query = (self.wallpaper_search_query_entry.get_text(),)
        thread = Thread(
            target=self.handle_search_btn_click_threaded_functions,
            args=self.query,
            daemon=True,
        )
        thread.start()


### SCRIPT HANDLING STUFF ###
def main():
    win = Window()
    win.connect("destroy", Gtk.main_quit)
    win.show()
    Gtk.main()


if __name__ == "__main__":
    main()

