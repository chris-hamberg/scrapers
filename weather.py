'''
author : Chris Hamberg
program: Stream Weather Forecast into Terminal

github  : https://github.com/chris-hamberg/
facebook: https://www.facebook.com/chris.hamberg.1

usage   : search for your local forecast at accuweather
          copy and paste the url in the url variable in the script

          ~$ python weather.py
'''
import requests, lxml.html, sys

############## your url goes here
url = 'http://www.accuweather.com/en/us/cincinnati-oh/45229/weather-forecast/350126'

user_agent = ("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:53.0) "
              "Gecko/20100101 Firefox/53.0")

keys = current,   tonight,   tomorrow,   future = (
      'current', 'tonight', 'tomorrow', 'future')

cssselectors = {
        
        current : {
            'header'     : '.bg-su > h3:nth-child(1) > a:nth-child(1)',
            'temperature': '.bg-su > div:nth-child(3) > div:nth-child(1) > '
                                'span:nth-child(1)', 
            'conditions' : '.bg-su > div:nth-child(3) > span:nth-child(2)'
                    },

        tonight : {
            'header'     : '.bg-cl > h3:nth-child(1) > a:nth-child(1)', 
            'temperature': '.bg-cl > div:nth-child(4) > div:nth-child(1) > '
                                'span:nth-child(1)',
            'conditions' : '.bg-cl > div:nth-child(4) > span:nth-child(2)'
                    },

        tomorrow: {
            'header'     : 'li.day:nth-child(3) > div:nth-child(1) > '
                                'h3:nth-child(1) > a:nth-child(1)',
            'temperature': 'li.day:nth-child(3) > div:nth-child(1) > '
                                'div:nth-child(4) > div:nth-child(1) > '
                                'span:nth-child(1)',
            'conditions' : 'li.day:nth-child(3) > div:nth-child(1) > '
                                'div:nth-child(4) > span:nth-child(2)'
                     },

        future : {
            'header'     : 'li.last:nth-child(4) > div:nth-child(1) > '
                                'h3:nth-child(1) > a:nth-child(1)',
            'temperature': 'li.last:nth-child(4) > div:nth-child(1) > '
                                'div:nth-child(4) > div:nth-child(1) > '
                                'span:nth-child(1)', 
             'conditions': 'li.last:nth-child(4) > div:nth-child(1) > '
                                'div:nth-child(4) > span:nth-child(2)'
                   }
        }
def request(url, user_agent):
    headers = {'user_agent': user_agent}
    try:
        response = requests.get(url, headers=headers)
        status = response.status_code
        assert status == 200, 'http error code: {status}'.format_map(
                vars())
        content = response.content.decode()
    except AssertionError as e:
        print(str(e))
    except AttributeError as e:
        print('error: could not decode response content')
    else:
        return content
    sys.exit(0)

def scrape(tree, cssselectors):
    parse = lambda selector: tree.cssselect(selector)[0].text_content()
    data = cssselectors
    for time_period in cssselectors:
        for data_field in cssselectors[time_period]:
            try:
                csselector = cssselectors[time_period][data_field]
                data[time_period][data_field] = parse(csselector)
            except IndexError as e:
                data[time_period][data_field] = ''
                continue
    return data

def display(data):
    print()
    for name in keys:
        print(' {0:<15}: {1:<3} | {2}'.format(
                data[name]['header'] or name.title(),
                data[name]['temperature'] or 'n/a',
                data[name]['conditions'].lower() or 'n/a',
                ))
    print()

def main(cssselectors):
    content = request(url, user_agent)
    tree = lxml.html.fromstring(content)
    data = scrape(tree, cssselectors)
    display(data)

if __name__ == '__main__':
    main(cssselectors)
