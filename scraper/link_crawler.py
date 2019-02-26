# -*- coding: utf-8 -*-
import time, urlparse, re, threading, random
from downloader import Downloader
from example_callback import Scraper

class Crawler:

    def __init__(self, seed_url='', link_regex='', callback=None, timeout=30, 
                max_threads=1, max_depth=-1, permitted_domains=[], disallow=[],
                limited=True):
        # if 'www.' not in seed_url.lower():
        #    seed_url = seed_url.split('//')[0]+'//www.'+seed_url.split('//')[1]
        self.seed_url = seed_url
        self.link_regex = link_regex
        self.queue = [self.seed_url]
        self.seen = dict()
        self.callback = callback
        self.timeout = timeout
        self.max_threads = max_threads
        self.max_depth = max_depth
        self.threads = list()
        self.permitted_domains = permitted_domains + self.queue
        if isinstance(disallow, str):
            disallow = [disallow]
        self.disallow = disallow + ['mailto:']
        self.download = Downloader()
        self.limited = limited

    def process_queue(self):
        '''This is the core crawling alogrithm.'''
        while True:
            try:
                url = self.queue.pop()
            except IndexError:
                break # queue is empty
            else:
                depth = self.seen.setdefault(url, 0)
                links = list() # link queue
                html = self.download(url)
                if self.callback:
                    links.extend(self.callback(url, html) or [])
                if depth != self.max_depth:
                    for link in self.get_links(html):
                        
                        if re.match(self.link_regex, link):
                            link = self.normalize(link)
                            links.append(link)
                        
                        '''
                        try:
                            for word in self.disallow:
                                assert not re.search(word.lower(), link.lower())
                            raise TypeError
                        except AssertionError:
                            continue
                        except TypeError:
                            if re.match(self.link_regex.lower(), link.lower()):
                                links.append(link)
                        '''
                for link in links:        
                    #link = self.normalize(link)
                    if link not in self.seen:
                        self.seen[link] = depth + 1
                        if self.permitted_domain(link):
                            self.queue.append(link)

    def start(self):
        while self.threads or self.queue:
            for thread in self.threads:
                if not thread.is_alive():
                    self.threads.remove(thread)
            while len(self.threads) < self.max_threads and self.queue:
                thread = threading.Thread(target=self.process_queue)
                thread.setDaemon(True)
                thread.start()
                self.threads.append(thread)
            time.sleep(random.random())

    def get_links(self, html):
        webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
        return webpage_regex.findall(html)
            
    def normalize(self, link):
        '''Normalize URL by removing hash, and adding domain'''
        link, _ = urlparse.urldefrag(link) # remove hash to avoid duplicates
        params = urlparse.urlparse(link).params
        query = urlparse.urlparse(link).query
        fragment = urlparse.urlparse(link).fragment
        for bad_string in (params, query, fragment):
            link = link.replace(bad_string, '')
        return urlparse.urljoin(self.seed_url, link.replace('?', ''))
        
    def permitted_domain(self, url):
        '''Return True if URL is permitted'''
        if self.limited:
            url = urlparse.urlparse(url).netloc.lower()
            for domain in self.permitted_domains:
                domain = urlparse.urlparse(domain).netloc.lower()
                if domain == url:
                    return True
            else: 
                return False
        else:
                return True
            
if __name__ == '__main__':
    url = 'http://example.webscraping.com/'
    scraper = Crawler(url, link_regex='/(index|view)/', 
                      max_threads=1,
                      callback=Scraper('data.csv'),
                      max_depth=3)
    scraper.start()
