#!/usr/bin/python
#coding:utf-8
import base64
import json
import os
import requests

def detect_text(dirId, imId):
    cache = "json{0:02d}".format(dirId) + "/image{}.json".format(imId)
    if os.path.isfile(cache):
        with open(cache, 'r') as f:
            result = json.load(f)
        if 'textAnnotations' in result['responses'][0]:
            return (result['responses'][0]['textAnnotations'][0]['description'])
        else:
            return ""
    path = "images{0:02d}".format(dirId)  + "/image{}.jpg".format(imId)
    with open(path, 'rb') as image_file:
        content = base64.b64encode(image_file.read())
        content = content.decode('utf-8')

    api_key = "hogehoge"
    url = "https://vision.googleapis.com/v1/images:annotate?key=" + api_key
    headers = { 'Content-Type': 'application/json' }
    request_body = {
        'requests': [
            {
                'image': {
                    'content': content
                },
                'features': [
                    {
                        'type': "TEXT_DETECTION",
                        'maxResults': 10
                    }
                ]
            }
        ]
    }
    response = requests.post(
        url,
        json.dumps(request_body),
        headers
    )
    result = response.json()
    with open(cache, 'w') as f:
        json.dump(result, f)
    if 'textAnnotations' in result['responses'][0]:
        return (result['responses'][0]['textAnnotations'][0]['description'])
    else:
        return ""

if __name__ == '__main__':
  detect_text(0, 1461)
