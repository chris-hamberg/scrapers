import time, random, re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class Browser(webdriver.Firefox):
    '''
    This class IS a web browser. It contains dict data on pages visited, and a
    list of items that are a collection of urls to visit (extracted from a 
    preconfigured text file of carriage return seperated urls.)
    
    Class includes all of the selenium webdriver inherited methods.
    
        *note:
            - the get_urls method reads urls from a .txt file
            - the update_page method invokes the Page class scraper
            - the default webdriver get method is over written so that each get 
            call scrapes the new page (if the data exists on the page.)
    '''
    def __init__(self):
        super(Browser, self).__init__() # Initialize the inherited webdriver
        self.pages = {} # A browser contains pages.
        self.urls  = self.get_urls() # urls to visit.
        self.win_main = self.current_window_handle
        self.pop_win1 = None
        self.pop_win2 = None
        
    def get(self, url):
        '''
        Overides the default webdriver get method. The modification add a 
        method call from the Browser class: self.update_page() 
            
            - creates a new Page instance when the get method
            is called
            
            - the Page instance is stored as the value to the  self.pages 
            dictionary, whose key is the Browser objects current frame ID. 
        
        A browser can only display one page at a time, so each get method 
        invocation overwrites the old Page instance with a new page instance 
        on each get call.
        
        Page instances Automatically scrape the actual webpage upon  
        instantiation.
        '''
        super(Browser, self).get(url) 
        self.update_page()
        
    def get_urls(self):
        '''
        This method gets a list of urls that the user should visit during a
        session.
        '''
        with open('urls.txt') as urls:
            self.urls = [url.rstrip() for url in urls]

    def update_page(self):
        '''
        - This method instantiates a new Page object. The page instance 
        represents the current webpage navigated to by a Browser get 
        request.
        
        - The Page instance created by this call is stored in the 
        self.pages data attribute.
        
        - The Page instance is associated with the current window handle 
        of the webdriver. Old pages are over written by new pages.
        
        self.current_window_handle is the dict key for the Page.
        
        - self.page_source is the data used for scraping the new page
        '''
        self.pages[
                    
                    self.current_window_handle
                  
                  ] = Page(self.page_source, self.current_url)
        
class Page(list):
    '''
    This class represents a webpage. It contains page data including:
        - url
        - source code
        - scraped page data relevant to the user
    '''
    def __init__(self, source, url):
        self.url    = url
        self.source = source # The webpages source code
        
        # Automatically attempts to scrape new pages
        try:
            self.scrape_page_data()
        except Exception as err:
            pass # Data not on page
           
    def get_page_listing(self):
        '''
        This method is used to return scraped data to a caller
        '''
        return self # a list of scraped data
        
    def get_num_ids(self):
        return self.num_ids

    def scrape_page_data(self):
        '''
        Delegation method. For scraping the webpage data.
        '''
        self.scrape_numeric_IDs()
        self.scrape_textual_component()
        self.build_listing()
    
    # TODO: Perhaps make a new class Scraper & as a composite to Page
    # TODO: This seems more like a Robot class set of methods.
    '''
    The rest of this class handles scraping page data.
    Videos on the website are listed in a graphical grid matrix layout. This 
    class gets the names for each video listed; constructing the specific 
    video name for each video in the grid.
        
        *This process includes:
            
            - getting each unique numeric video ID for each video displayed on 
            the webpage.
              
            - from that data set: a comprehensive list of all of the existing 
            & valid names are generated. 
              
            - the list of names is then stored in the object instance as a 
            data attribute referred to as 'self'. 
              
            - 'self' is a list of strings.
        
        **General:
            - The Page class assumes that page source code will be passed to 
            its constructor.
    '''
    def scrape_numeric_IDs(self):       
        '''       
        Collect the numerical ID values for each video on the page.
      
        '''
        # In the source code, find the approximate ends of the data.
        index  = self.source.find('initialCardLoad')
        offset = self.source[index:].find('\n')  # (index + offset = end index)

        # Truncate the excessive data overflow.
        data   = self.source[index:index+offset] # (index + offset = end index)
        index  = data.find('{')
        data   = data[index:]

        # Extract the complete data {set} using regex matches.
        reObj  = re.compile('cardId: \d+,') 
        collection = reObj.findall(data)
 
        # Format each number and place them all into a list.
        self.num_ids = list(
            string.split()[1].rstrip(',')
            for string in collection)
        '''
                *Generator comprehension notes:
               
                - string.split() is used because each 'string' begins with a 
                superfluous set of characters: 'cardID'
            
                - an erroneous comma is stripped off the end of each 'string'
        '''
    def scrape_textual_component(self):
        '''
        Get the data required for, and built the video name template.
            
            - this is done because the surrounding textual components of the 
            name (non-decimal parts) might be variant for each scrape session
        '''
            # Decide which logic to deploy.
        if self.url.endswith('/watch/sponsored'):
            
            # Deploy sponsored logic.
            number, data = self.sponsored()
        elif self.url.endswith('/ncrave'):
            pass
        else:
        
            # Deploy categories logic.
            number, data = self.categories()
        
        # Transform the scraped name into a generic format string
        self.format_string = data.replace(number, '%s')
        '''
            " <name>%s-<series of static numbers> "
        '''
            
    def build_listing(self):     
        '''
        Format each numeric value in the self.num_ids list into the generic
        format string. Then collect each formatted string into the List objects
        inherited collection container.
            
            *Generator comprehension notes:
                
                - the self.format_string variable is the instances format 
                string: 
                            " <name>%s-<series of static numbers> "   
        ''' 
        # Extend instances data members with scraped & formatted Page content
        self.extend(
        self.format_string % num 
        for num in self.num_ids
        )

    def sponsored(self):
        '''
        Abstraction for the scrape_textual_component.
        Deploys the scrape logic for the 'sponsored' URL.
        '''
        # Try to find the format string in the source code.
        for number in self.num_ids:
            string = r'sbTrayListItemHeader%s-\d+' % number
            reObj  = re.compile(string)
            try:
                data = reObj.search(self.source).group(0)
            except: continue # string not found, try next
            else: break # string found, exit loop
        return number, data # to caller to finish building the format string

    def categories(self):
        '''
        Abstraction for the scrape_textual_component.
        Deploys the scrape logic for the categories URL.
        '''
        # Extract a numeric ID from the scraped numeric data.
        number = self.num_ids[0]

        # With number, build a regex for scraping the name template.
        string = r'<section id="\D+%s-\d+' % number
        reObj  = re.compile(string)
        data   = reObj.search(self.source).group(0)
        
        # Zero in on the taregt & truncate the excess data.
        return number, data[data.find('"')+1:] # [-1] is the last numeric value
