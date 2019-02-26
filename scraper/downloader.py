# -*- coding: utf-8 -*-
import random, urllib2, urlparse, socket, httplib, ssl, logging, os
from throttle import Throttle
from cache import MongoCache
try:
    from user_agent import user_agent
except ImportError:
    user_agent = 'wswp'
    
if os.path.exists('error_log'):
    os.remove('error_log')
    
logging.basicConfig(
    filename='error_log',
    level=logging.ERROR, 
    format=' %(asctime)s - %(levelname)s - %(message)s')
    
DEFAULT_DELAY = 1
DEFAULT_AGENT = user_agent
DEFAULT_RETRIES = 2
DEFAULT_CACHE = MongoCache()
DEFAULT_PROXIES = None
DEFAULT_OPENER = None
DEFAULT_TIMEOUT = 60

class Downloader:

    def __init__(self, delay=DEFAULT_DELAY, user_agent=DEFAULT_AGENT, 
                num_retries=DEFAULT_RETRIES, cache=DEFAULT_CACHE, 
                proxies=DEFAULT_PROXIES, opener=DEFAULT_OPENER, 
                timeout=DEFAULT_TIMEOUT):
        socket.setdefaulttimeout(timeout)
        self.throttle = Throttle(delay)
        self.user_agent = user_agent
        self.proxies = proxies
        self.num_retries = num_retries
        self.cache = cache
        self.opener = opener

    def __call__(self, url):
        result = None
        if self.cache:
            try:
                result = self.cache[url]
            except KeyError:
                pass
            else:
                if self.num_retries > 0 and 500 <= result['code'] < 600:
                    result = None
        if result is None:
            self.throttle.wait(url)
            proxy = random.choice(self.proxies) if self.proxies else None
            headers = {'user-agent': self.user_agent}
            result = self.download(url, headers, proxy, self.num_retries)
            if self.cache:
                self.cache[url] = result
        return result['html']

    def download(self, url, headers, proxy, num_retries, data=None):
        print 'Downloading:', url
        request = urllib2.Request(url, data, headers or {})
        opener = self.opener or urllib2.build_opener()
        if proxy:
            proxy_params = {urlparse.urlparse(url).scheme: proxy}
            opener.add_handler(urllib2.ProxyHandler(proxy_params))
        try:
            response = opener.open(request)
            html = response.read()
            code = response.code
        except urllib2.URLError as e:
            print 'Download error:', str(e)
            logging.error(str(e))
            html = ''
            if hasattr(e, 'code'):
                code = e.code
                if num_retries > 0 and 500 <= code < 600:
                    return self.download(url, headers, proxy, num_retries-1, data)
            else:
                code = None
        except (socket.error, httplib.BadStatusLine, httplib.IncompleteRead,
                socket.timeout, ssl.SSLError) as e:
            print 'Download error:', str(e)
            logging.error(str(e))
            html, code = '', None
            if num_retries > 0:
                return self.download(url, headers, proxy, num_retries-1, data)
        return {'html': html, 'code': code}
