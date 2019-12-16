from lxml.html import fromstring, tostring
import datetime, os, random, requests, shelve, sys, time


URL = 'http://compoasso.free.fr/primelistweb/page/prime/liste_online_en.php'
DATA = os.path.join('data', 'pdata')


if not os.path.exists(DATA):
    try:
        os.mkdir('data')
    except FileExistsError:
        pass
PRIMES = shelve.open(DATA, writeback=True)


def maxfile():
    print('INFO: Getting most recent html doc.')
    files = os.listdir('html')
    files.remove('home.html')
    files.sort(key=lambda n: int(n.split('.')[0]))
    return read(files[-2])


def uagent():
    with open('useragents') as fhand:
        dat = fhand.read()
    dat = dat.split('\n')
    return random.choice(dat)


def home():
    try:
        headers = {'User-Agent': uagent()}
        response = requests.get(URL, headers=headers)
        assert response.status_code == 200
    except AssertionError as fail:
        print('home() failed.')
        sys.exit(0)
    else:
        html = response.text
        write(html, 'home.html')
        return html


def write(html, name):
    with open(os.path.join('html', name), 'w') as fhand:
        fhand.write(html)


def read(name):
    with open(os.path.join('html', name)) as fhand:
        print(f'INFO: [READ] - {name}')
        return fhand.read()


def sniff(tree):

    try:
        xpath = '/html/body/table/tr/td[2]/div[2]/form/input[6]'
        lastPrimeHidden = tree.xpath(xpath)[0].value
    except Exception as error:
        print(str(error))
        sys.exit(0)
    else:
        return int(lastPrimeHidden)


def request(html, headers, number):

    tree     = parse(html)
    number   = sniff(tree)
    name     = str(number) + '.html'
    data     = {'numberInput': number}
    path     = os.path.join('html', name)

    if os.path.exists(path):
        html = read(name)
    else:
        response = requests.post(URL, headers=headers, data=data)
        print(f'INFO: <[{response.status_code}]> - {number}')
        assert response.status_code == 200
        html = response.text
        write(html, name)
        time.sleep(1)

    return html, headers, number


def lunch(epoch):
    if (datetime.datetime.utcnow() - epoch).total_seconds() > 60 * 15:
        denotation  = list(PRIMES['p'])[-10:]
        cardinality = len(PRIMES['p'])
        print(f'INFO:[DATA]: {denotation}')
        print(f'INFO:[CARDINALITY]: {cardinality}')
        print('INFO: Taking a 5 minute break.')
        time.sleep(60 * 5)
        print('INFO: Resuming Operations for 15 minutes, before next break.')
        return datetime.datetime.utcnow()
    return epoch
    

def crawl(site):

    print('INFO: Begin Crawl.')

    html      = site
    headers   = {'User-Agent': uagent()}
    number    = 0
    epoch     = datetime.datetime.utcnow()

    try:
        html = maxfile()
    except IndexError as error:
        print(str(error))

    while number < 1000000000000:
        try:
            html, headers, number = request(html, headers, number)
        except AssertionError as error:
            print(str(error))
        finally:
            epoch = lunch(epoch)

    sys.exit('Finished.')


def parse(html):
    tree = fromstring(html)
    for i in range(1, 21):
        for j in range(1, 11):
            try:
                xpath = ('/html/body/table/tr/td[2]/div[2]'
                         f'/form/table/tr[{i}]/td[{j}]')
                prime = tree.xpath(xpath + '/text()')
                if not prime:
                    prime = tree.xpath(xpath + '/u/b/text()')
                if isinstance(prime, list):
                    prime = int(prime[0])
                else:
                    prime = int(prime)
            except Exception as error:
                print(str(error))
            else:
                PRIMES['p'].add(prime)
    return tree


def main():

    index = os.path.join('html', 'home.html')
    
    try:
        assert isinstance(PRIMES['p'], set)
    except (KeyError, AssertionError):
        PRIMES['p'] = set()
    
    if not os.path.exists(index):
        try:
            os.mkdir('html')
        except FileExistsError:
            pass
        finally:
            site = home()
            time.sleep(1)
    else:
        with open(index) as fhand:
            site = fhand.read()

    try:
        denotation  = list(PRIMES['p'])[-10:]
        cardinality = len(PRIMES['p'])
        print(f'INFO:[DATA]: {denotation}')
        print(f'INFO:[CARDINALITY] {cardinality}')
        input('[ENTER] to continue...\n> ')
        crawl(site)
    except Exception as error:
        print(str(error))
    finally:
        PRIMES.close()


if __name__ == '__main__':
    main()
