import re
import sys

import requests

sys.setrecursionlimit(30000)

url_pattern = re.compile(r'''href=["']([^'"]+)["']''')

fetched = set()
target = set()
errors = set()

def get_link(url):
    if url in fetched:
        if url in errors:
            return None, "error"
    try:
        result = requests.get(url, allow_redirects=False)
        if result.status_code != 200:
            return None, result.status_code
        return result.content, 200
    except Exception as e:
        return None, e

def check(url):
    print('==== {} ===='.format(url))
    content, status_code = get_link(url)
    fetched.add(url)
    if not content:
        print('[Error: {}] '.format(status_code))
        return

    ms = url_pattern.findall(content)
    host = '/'.join(url.split('/')[:3])
    if url.endswith('/'):
        path = url
    else:
        path = '/'.join(url.split('/')[:-1]) + '/'
    for m in ms:
        sys.stdout.flush()
        m = m.split("#")[0]
        if m.startswith('http'):
            link = m
        elif m.startswith('//'):
            link = 'http:{}'.format(m)
        elif m.startswith('/'):
            link = '{}{}'.format(host, m)
        else:
            link = '{}{}'.format(path, m)
        c, s = get_link(link)
        if not c:
            print('{}: {}'.format(s, m))
            continue
        if link not in fetched:
            if link.startswith(host):
                target.add(link)
    if not target:
        return
    next_link = target.pop()
    if next_link:
        check(next_link)


def main():
    params = sys.argv
    if len(params) != 2:
        print("Usage: python link_checker.py [url]")
        return
    check(params[1])


if __name__ == '__main__':
    main()
