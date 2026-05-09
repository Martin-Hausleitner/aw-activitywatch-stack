#!/usr/bin/env python3
import json, urllib.request
buckets=json.load(urllib.request.urlopen('http://127.0.0.1:5600/api/0/buckets/'))
for k,v in sorted(buckets.items()):
    if any(s in k.lower() for s in ('whoop','screentime','import')):
        print(k, v.get('type'), v.get('created'))
