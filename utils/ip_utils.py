import random
import re
from curl_cffi.requests import AsyncSession

import requests
from loguru import logger

cf_url_list = [
    "https://blog.cloudflare.com/cdn-cgi/trace",
    "https://dash.cloudflare.com/cdn-cgi/trace",
    "https://developers.cloudflare.com/cdn-cgi/trace"
]


def fetch_proxy_ip(proxy_str=None):
    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    try:
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
    except Exception as e:
        logger.error(f'fetch proxy: {proxy_str} ip failed, err: {e}')
        return ''

    return m.group(1) if m else ''

async def async_fetch_proxy_ip(proxy_str=None):
    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    proxies = None
    if proxy_str:
        proxies = {
            "http": proxy_str,
            "https": proxy_str
        }

    url = random.choice(cf_url_list)
    timeout = 5

    try:
        async with AsyncSession() as session:
            resp = await session.get(url, headers=headers, proxies=proxies, timeout=timeout)
            m = re.search(r'ip=(.*)', resp.text)
            return m.group(1) if m else ''
    except Exception as e:
        logger.error(f'fetch proxy: {proxy_str} ip failed, err: {e}')
        return ''

if __name__ == '__main__':
    proxy_str = 'http://192.168.50.88:40042'
    ip = fetch_proxy_ip(proxy_str)
    print(ip)
