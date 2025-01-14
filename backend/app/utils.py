import re

def is_url_valid(url: str):
    regex = r'^(?:http|ftp)s?://(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+(/[^ ]*)?$'
    return re.match(regex, url) is not None