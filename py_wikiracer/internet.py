from urllib.request import urlopen
from pathlib import Path
import base64
import ssl

FILE_CACHE_DIR = "wiki_cache"

context = ssl._create_unverified_context()

class Internet:
    DISALLOWED = [":", "#", "/", "?"]

    def __init__(self):
        self.requests = []

    def get_page(self, page):
        if page[:6] != "/wiki/":
            raise ValueError(f"Links must start with /wiki/. {page} is not valid.")
        if any(i in page[6:] for i in Internet.DISALLOWED):
            raise ValueError(f"Link cannot contain disallowed character. {page} is not valid.")
        self.requests.append(page)
        return Internet.__get_page_internal(page)

    def get_random(self):
        return urlopen(f"https://en.wikipedia.org/wiki/Special:Random", context=context).read().decode('utf-8')

    @staticmethod
    def __get_page_internal(page):
        # First see if we have it in the local cache, to reduce the number of spam requests to Wikipedia
        file_cache_dir_path = Path(FILE_CACHE_DIR)
        if not file_cache_dir_path.is_dir():
            file_cache_dir_path.mkdir()

        # Convert page to a filesystem safe name
        safe_name = base64.urlsafe_b64encode(page.encode("utf-8")).decode("utf-8")

        local_path = file_cache_dir_path / safe_name

        if local_path.is_file():
            return local_path.read_text(encoding="utf-8")

        html = urlopen(f"https://en.wikipedia.org{page}", context=context).read().decode('utf-8')

        # write to file cache
        local_path.write_text(html, encoding="utf-8")

        return html
