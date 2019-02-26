from __future__ import print_function
import requests, lxml.html

headers = {'user-agent': 'taco'}
urls_to_check = [
    'http://www.packtpub.com/application-development/python-data-structures-and-algorithm',
    'https://www.packtpub.com/big-data-and-business-intelligence/learning-data-mining-python-second-edition',
    'https://www.packtpub.com/big-data-and-business-intelligence/neural-network-programming-python',
    'https://www.packtpub.com/application-development/python-programming-blueprints'
                ]
print()
for url in urls_to_check:
    title = url.split('/')[-1].replace('-', ' ').title()
    print('Checking for title: %s'%title)
    page = requests.get(url, headers=headers).content
    tree = lxml.html.fromstring(page)
    if not tree.cssselect('.title-preorder') and not tree.cssselect('.alpha-text'):
        print('\t\n%s [READY FOR DOWNLOAD]\n'%title)
    else:
        print('\t\t\t\t\t\t\t(negative)')
    
url = 'https://www.packtpub.com/packt/offers/free-learning'
print('Checking the [FREE] title...')
page = requests.get(url, headers=headers).content
tree = lxml.html.fromstring(page)
print('\n\tFree Book: %s\n'%tree.cssselect('.dotd-title h2')[0].text_content().strip())
