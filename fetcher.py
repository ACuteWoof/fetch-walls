import gi
import os
from requests import get

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf


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

    def download_image(self, path):
        response = get(path, stream=True)
        file_name = path.split("/")[-1]
        self.files.append(file_name)
        file_location = f"{self.wallpaper_folder}/temp.{file_name.split('.')[-1]}"
        with open(file_location, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        return file_location
