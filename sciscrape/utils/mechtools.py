'''
Utilities for emulating a web browser. The PubBrowser class
controls a mechanize.Browser instance to load pages, download
documents, redirect requests through library proxy servers,
and other miscellaneous utilities.
'''

# Import modules
import os
import re
import getpass
import urlparse
import mechanize
from pyquery import PyQuery

class PubBrowser(object):
        
    class NoHistory(object):
        '''Hack to disable history in mechanize module.
        Adapted from http://stackoverflow.com/questions/2393299/how-do-i-disable-history-in-python-mechanize-module'''
        
        def add(self, *a, **k): pass
        def clear(self): pass

    def __init__(self):
        
        # Initialize Browser
        self._b = mechanize.Browser(history=self.NoHistory())
        
        # Set headers
        self._b.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT)'),
        ]

        # Ignore robots.txt
        self._b.set_handle_robots(False)
    
    def get_docs(self):
        '''Extract raw and parsed text from browser.'''
        
        url = self.geturl()

        # Get base URL
        base_url = urlparse.urljoin(url, '_').strip('_')

        # Get browser text
        text = self._b.response().read()

        # Parse text
        try:
            qtext = PyQuery(text)\
                .make_links_absolute(base_url)\
                .xhtml_to_html()
        except:
            qtext = None
        
        # Return results
        return text, qtext
    
    # Expose methods of self._b

    def open(self, url, *args, **kwargs):
        
        self._b.open(url, *args, **kwargs)

    def geturl(self):
        
        return self._b.geturl()
    
class UMBrowser(PubBrowser):
    
    def __init__(self, user_file=None):
        
        # Call parent __init__
        super(UMBrowser, self).__init__()

        # Login to UM services
        self.login(user_file)
    
    def open(self, url):
        '''Open link through proxy.'''
        
        # Call super if URL has already gone through proxy
        if re.search('lib\.umich\.edu', url, re.I):
            super(UMBrowser, self).open(url)
            return
        
        # Get URL prefix
        if re.search('^(?:http|https|ftp)//:', url):
            prefix = 'http://'
        else:
            prefix = ''

        # Build proxy URL
        proxy_url = 'http://proxy.lib.umich.edu/login?url=%s%s' \
            % (prefix, url)
        
        # Open proxy URL
        super(UMBrowser, self).open(proxy_url)

    def check_proxy(self):
        '''Check whether browser is logged in to UM services.'''
        
        # Open UM login site
        super(UMBrowser, self).open('http://weblogin.umich.edu')

        # Check for redirect to UM services
        if self.geturl() == 'https://weblogin.umich.edu/services/':
            return True

        # Not logged in
        return False

    def login(self, user_file=None):
        '''Log in to UM services.'''
        
        # Quit if logged in
        if self.check_proxy():
            return
        
        # Select form
        self._b.select_form(nr=0)

        # Fill form fields
        if user_file and os.path.exists(user_file):
            userinfo = open(userfile, 'r').readlines()
            self._b['login'] = userinfo[0].strip()
            self._b['password'] = userinfo[1].strip()
        else:
            self._b['login'] = getpass.getpass('Username: ')
            self._b['password'] = getpass.getpass()

        # Submit login form
        self._b.submit()
