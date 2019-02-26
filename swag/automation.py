import re, logging, elements
from time import sleep
from random import randint

'''
Automates user login into a website, and visits a listing of videos.
Automatically select a set of videos to watch with the select_videos
command.
'''

error = ' %(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=error)

URL = 'http://www.swagbucks.com'

class User(object):

    # TODO: Since this is near the top level of the data model; it is here that 
    # TODO: it will be noted: timing randomization needs to be added largely
    # TODO: through-out the entire program. This should include both a random
    # TODO: sleep time in the proper locations + a for loop that performs a 
    # TODO: random (and large number) of iterations to offset the milliseconds
    # TODO: too.
    # TODO:
    # TODO: Add some better documentation for the class

    '''
    User class. This class is a composite class that has a Browser object. It's
    Browser keeps Page objects. The User has a name, and a password.
    
    User contains the following top level User interface methods:
        
        - login:
        
            The login method automatically launches the composite Broswer 
            object and logs the User into the website. It then attempts to 
            clear out the splash screen.
            
        - visit:
        
            The User objects Browser instance keeps a list of URLs that it 
            thinks that the User should visit. Invoking the visit method causes 
            the browser to randomly select a URL from that list & navigate to 
            that page. The browsers Page object will scrape video names from 
            the resulting page if valid name entires for videos exist on that 
            page.
            
        - select_video:
            
            The select video method is a delegation method. This method 
            ultimately will automatically select a video (usually at random) 
            for the user, at the current URL. Usually random, because nCrave 
            video randomization has not been built in yet. For nCrave videos: 
            the first video on the page (at least as I expect) is always 
            selected. All other selections are completely randomized. If the 
            method fails a print statement is sent to the terminal & control is 
            handed back to the top level.
            
                * the delegate sends to one of two psuedoprivate methods:
                    __main_selector handles most videos
                    __nCrave handles the nCrave videos
    ''' 
    def __init__(self):
        '''
        Initialize a User instance. Every User has a username, password, and
        web browser. Users can login, navigate pages, and click on videos.
        '''
        self.name  = ''
        self.passw = ''
        self.brows = elements.Browser()
        if self.name == '':
            self.name = input('Enter your user name: ')
        if self.passw == '':
            self.passw = input('Enter your password:  ')

    def login(self, url=URL+'/p/login'):
        '''      
        This method logs a User instance into the target urls website. It is 
        assumed that self refers to the User instance; an object whom has a 
        composite Browser object part.
            
            - User has a user name data attribute
            
            - User has a user password data attribute 
        '''
        splash_screen_attempts = 0 # prevent infinite halt after logging in.

        # Send the http get request to the webdriver.
        self.brows.get(url)

        # Populate the user name login forms user name field.
        # Populate the user password login forms password field.
        # Click the login form login button.
        self.brows.find_element_by_name('emailAddress').send_keys(self.name)  
        self.brows.find_element_by_name('password').send_keys(self.passw)
        self.brows.find_element_by_name('password').submit()

        while True: # Enter validation loop for pop-up closure.
            
            try:

                # Wait for the page to load, or take a time-out after a failure.
                sleep(randint(2, 8))

                # Attempt to close the pop-up.
                self.brows.find_element_by_id('swagButtonModalExit').click()

            except Exception as err: # Validation Failed to Pass

                splash_screen_attempts += 1
                
                    # After 5 unsuccessful pop-up closure attempts...
                    # ...terminate the loop & return flow of control to caller.
                if splash_screen_attempts >= 5:
                    logging.info('Error: failed to clear the splash screen')
                    break
                    
            else: # The pop-up was closed successfully.
                break

    def visit(self):
        '''
        - A url is selected at random from a list of urls, and then that url 
        page is navigated to. 
        
        - This method assumes that a User object is logged into the website 
        already. If operable navigation data does not exist in the Browser 
        objects data attributes then that Browser object (a component of the 
        assumed User object) will call its get_urls method. get_urls populates 
        a list (as an attribute of the Browser object) with valid urls.
        
        - This method ultimately assumes that a Browser object is responsible 
        for administrating & delegating urls.
        ''' 
        # If the Browser url attribute list is empty...
        # ...populate the Browser self.urls attribute with urls.
        if not self.brows.urls:    
            self.brows.get_urls()
        
        # Get maximum possible index value for the Browsers current url list.
        max_index = len(self.brows.urls)-1
       
        try:
        
            # Generate a random & valid index value.
            index = randint(0, max_index)
            
            # Pop a url from the list & assign that string to a variable.
            url = self.brows.urls.pop(index)
            
        except (ValueError, IndexError) as err:
            logging.info('{}'.format(err))
        
        # With url, send the http request to the webdriver.
        self.brows.get(url)

    def select_video(self):
        '''
        This method delegates it's call to the proper selection logic algorithm
        for its specfic use case based on the environments conditions.
        '''
        # nCrave videos are unidentifiable & have a special use case exception.
        if not self.brows.current_url.endswith('/ncrave'):
            self.__main_selector()              
        else:
            self.__nCrave()

    def __main_selector(self):
        '''
        select_video branch.
        
        This is the catch all video selection algorithm. Its logic is primarily 
        built around the Categories page. The end of the algorithm is marked 
        with an expected fail case for Sponsored videos.
            - uses the scraped page data to test ID names. In a variable, 
            'videos'
            - the anticipated video names are looped through, and tested at 
            random
            - a successful automated click terminates this algorithm
            - an ID is removed from the temporary list if that ID fails
            - each index value, for each test iteration, is generated randomly
            - semantic programming failure for flash videos
            - semantic programming failure for Sponsored videos; in the last 
            line, only
        '''
        # Get the current URL. Used to verify that the URL changed.
        url_temp = self.brows.current_url

        # Retrives the video element IDs list from the Page object.
        videos = self.brows.pages[
                 self.brows.current_window_handle
                 ].get_page_listing()

        # Each video element ID is removed from the list if its test fails, 
        # for each iteration.
        # Loop terminates if the list is exhausted (no videos were found).
        while videos:
        
            # Generate a random index within the valid range of values.
            choice = randint(0, len(videos)-1)
        
            try: # Attempt to actually click a video.
            
                video = self.brows.find_element_by_id(videos[choice])

                video.click()
        
            except Exception as err: # Video didn't exist
                logging.info('Error: {} failed.'.format(videos[choice]))
                
                videos.pop(choice) # Remove invalid ID from list; try again.
        
            else: # Video was clicked successfully
                break
        
        # Inoperable page displayed
        if self.brows.current_url.endswith('/upgrade-flash'):
            logging.info('Error: flash not installed')
        elif self.brows.current_url.endswith('/sponsored'): pass
        # Page never went to video.
        elif self.brows.current_url == url_temp:
            logging.info('Error: video selection failed.')

    def __nCrave(self):
        '''
        select_video branch.
        
        Solution for finding and clicking on an nCrave video. This is a simple
        algorithm. It sets up ActionChain commands and then applies them to the 
        nCrave page. Tabbing through the list of page elements to the first 
        video appears to be the only automated page navigation option. It might 
        be a good idea to collect a list of all of the invalid links along the 
        way, and save them to a txt file. This list, a black list, could then 
        (somehow) be cross checked against, before actually sending the 
        clicking action. If the position is bad then the action can use the 
        anticipated differential to offset its erroneous position.
        '''
        # Set up webdriver ActionChains for the browser. For sending TAB, and
        # RETURN keys directly to the browser, and not a specific page element.    
        action = elements.webdriver.common.action_chains.ActionChains(
                self.brows)
        action.send_keys(elements.Keys.TAB)
        select = elements.webdriver.common.action_chains.ActionChains(
                self.brows)
        select.send_keys(elements.Keys.RETURN)
        
        # There are 46 elements before the 1st nCrave video. TAB through these
        for i in range(40): action.perform()
        
        # Click on a video (by pressing the enter key)
        select.perform()
        
        sleep(randint(2, 8))
        
        # TODO: New browser frame is expected to be generated at this point.

class Robot(User):

    def __init__(self):
        User.__init__(self)
        self.memory = None
               
if __name__ == '__main__': # pass
    bot = Robot()
    bot.login()
    bot.visit()
