import random
import re

import requests

cf_url_list = [
    "https://blog.cloudflare.com/cdn-cgi/trace",
    "https://dash.cloudflare.com/cdn-cgi/trace",
    "https://developers.cloudflare.com/cdn-cgi/trace"
]

headers = {
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}


def fetch_proxy_ip(proxy_str=None):
    proxies = None
    if proxy_str:
        proxies = {
            "http": proxy_str,
            "https": proxy_str
        }

    url = random.choice(cf_url_list)
    timeout = 5
    resp = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
    m = re.search('ip=(.*)', resp.text)
    return m.group(1) if m else ''


if __name__ == '__main__':
    proxy_str = 'socks5://192.168.50.88:40012'
    ip = fetch_proxy_ip(proxy_str)
    print(ip)
