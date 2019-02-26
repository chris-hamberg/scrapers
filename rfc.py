from string import ascii_letters
import os, sys, random, socket

def rfc_number():
    try:
        return int(sys.argv[1])
    except (IndexError, ValueError):
        print('Must supply an RFC number as first argument')
        sys.exit(2)

def construct_packet(rfc_number, host, port):
    version = sys.version_info[0]
    return (f'GET /rfc/rfc{rfc_number}.txt HTTP/1.1\r\n'
            f'Host: {host}:{port}\r\n'
            f'User-Agent: Python {version}\r\n'
            'Connection: close\r\n'
            '\r\n')

def request(packet, host, port):
    sock = socket.create_connection((host, port))
    sock.sendall(packet.encode('ascii'))
    raw_response = b''
    while True:
        buffer = sock.recv(4096)
        if not len(buffer):
            break
        raw_response += buffer
    return raw_response.decode('utf-8')

def random_string():
    n = random.randint(20,40)
    return '.'+''.join(random.choice(ascii_letters) for _ in range(n))

def display(rfc, fname):
    with open(fname, 'w') as fhand:
        fhand.write(rfc)
    os.system(f'less {fname}')
    os.remove(f'{fname}')

def main():
    host, port = 'www.ietf.org', 80
    try:
        packet = construct_packet(rfc_number(), host, port)
        rfc = request(packet, host, port)
        fname = random_string()
        display(rfc, fname)
    except Exception as e:
        print(str(e))
        sys.exit(0)

if __name__ == '__main__':
    main()
