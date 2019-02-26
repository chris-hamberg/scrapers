'''
Author: Chris Hamberg
Facebook: https://www.facebook.com/chris.hamberg.1
Github: https://github.com/morphine-html/
install file creates user config bash alias "define" if it doesnt exist
on linux only
other os have to use cmd line interface as normal python script
install on linux: ~$ python define.py
use: define <term>
use on win or OSx: python define.py <term>
'''
import requests, lxml.html, shutil, sys, os
from collections import namedtuple

def build_selectors():
    Selector = namedtuple('Selector', ('abstract', 'selector'))
    result   = Selector('definition',
                        '._Jig > div:nth-child(1) > span:nth-child(1)')
    spelling = Selector('spelling',
                        '#fprsl > b:nth-child(1) > i:nth-child(1)')
    return spelling, result

def parse_cmd():
    if len(sys.argv) == 1:
        print('Usage:\n~$ define <search term>')
        return False
    try: return '+'.join(sys.argv[1:])
    except IndexError as e: return False

def scrape(url, word, user_agent):
    spelling, result = build_selectors()
    try:
        data = requests.get(url.format_map(vars()),
                            headers=user_agent).content
        tree = lxml.html.fromstring(data)
        definition = tree.cssselect(result.selector)
    except Exception as e: definition = []
    else:
        try: word = tree.cssselect(spelling.selector)[0].text
        except Exception: pass
    finally: return word, definition

def display(word, definition):
    linux, folder = 'lin', '.programs'
    word = word.replace('+', ' ').title()+'\n'
    fpath = os.path.join(folder, word)
    path_existed = True
    if not os.path.exists(folder):
        os.mkdir(folder)
        path_existed = False
    open(fpath, 'w'
            ).write(word) if linux in sys.platform else print(word)
    if definition == []: 
        message = '\t- No definition found for {}'.format(word)
        print(message) if not linux in sys.platform else input(message)
    else:
        with open(fpath, 'a') as fhand:
            for item in definition:
                data = '\t- '+item.text
                if linux in sys.platform:
                    fhand.write(data+'\n')
                else: print(data)
            fhand.write('\n[Q] to quit\n')
        if linux in sys.platform:
            os.system('less "{fpath}"'.format_map(vars()))
        else:
            input('\n[enter] to exit...')
    try:
        os.remove(fpath)
    except FileNotFoundError:
        pass
    if not path_existed: shutil.rmtree(folder)

def main():
    url = 'https://www.google.com/search?q=define+{word}'
    command = 'cls' if 'win' in sys.platform else 'clear'
    user_agent = {'user-agent':
            ('Mozilla/5.0 (X11; Linux i686)'
             ' AppleWebKit/537.17 (KHTML, like Gecko)'
             'Chrome/24.0.1312.27 Safari/537.17')
                 }
    if 'lin' in sys.platform:
        try: 
            import install
            install.alias(command, silent=True)
        except ImportError as e:
            print(str(e))
    os.system(command)
    word = parse_cmd()
    if word:
        word, definition = scrape(url, word, user_agent)
        display(word, definition)
        os.system(command)

if __name__ == '__main__': main()