from curl_cffi import requests as cureq

headers = {
    'Accept': 'application/x-clarity-gzip',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Length': '298',
    'Cookie': 'MUID=35A2F36F75E46BC324C4E7AE74E46ACD',
    'DNT': '1',
    'Host': 'e.clarity.ms',
    'Origin': 'https://sa.aqar.fm',
    'Referer': 'https://sa.aqar.fm/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
}
url = 'https://sa.aqar.fm/'
response = cureq.get(url, impersonate='chrome', headers=headers)

print(response.text)