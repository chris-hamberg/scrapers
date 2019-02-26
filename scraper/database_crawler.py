import itertools, urlparse
from downloader import Downloader

def crawl(url, callback=None):
    
    download = Downloader()
    num_errors, max_errors = 0, 5
    
    for page in itertools.count(1):
        if num_errors == max_errors:
            break
        num_errors += 1
        link = urlparse.urljoin(url, '%d'%page)
        html = download(link)
        if html:
            num_errors = 0
            # TODO callback(html)
