import extruct
import requests
import pprint
import json
import sys
from w3lib.html import get_base_url

if len(sys.argv) > 1:
    url = sys.argv[1]
else:
    url = 'https://www.theguardian.com/us-news/2020/jul/07/donald-trump-abuse-father-niece-mary-book'

pp = pprint.PrettyPrinter(indent=2)
r = requests.get(url)
base_url = get_base_url(r.text, r.url)
data = extruct.extract(r.text, base_url=base_url, syntaxes=['microdata'])

print(json.dumps(data, indent=4, sort_keys=True))