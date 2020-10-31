import sys
import requests
from pprint import pprint
from progressbar import ProgressBar

if len(sys.argv) < 2:
    print("Error: No URL specified.")
    sys.exit(0)

url = sys.argv[1]

if not url.startswith("https://tvfplay.com/"):
    print("Specified URL appears to be invalid or not supported.")
    sys.exit(0)

tvfapi_url = url.replace("https://tvfplay.com/")

tvfapi_response = requests.get(tvfapi_url)

if tvfapi_response.status_code != 200:
    print("Error: Unable to fetch",url)
    sys.exit(0)

try:
    tvfapi_json = tvfapi_response.json()
    account_id = tvfapi_json['episode']['video_account_id']
    video_id = tvfapi_json['episode']['brightcove_video_id']
except:
    print("Invalid response received.")
    sys.exit(0)

brightcove_url = "https://edge.api.brightcove.com/playback/v1/accounts/%s/videos/%s" % (account_id, video_id)

headers = headers = {
    "User-Agent":"Mozilla/5.0 (Linux; Android 10; SM-J400F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36",
    "Referer":"https://www.zee5.com",
    "Accept":"*/*",
    "Accept-Encoding":"gzip, deflate, br",
    "Accept-Language":"en-US,en;q=0.9",
    "Origin":"https://www.zee5.com",
    "sec-fetch-dest":"empty",
    "sec-fetch-mode":"cors",
    "sec-fetch-site":"same-site",
}

brightcove_response = requests.get(brightcove_url, headers=headers)

video_streams = []

try:
    brightcove_json = brightcove_response.json()
    for src in brightcove_json['sources']:
        if ('container' in src.keys() and src['container']=='MP4'):
            video_streams.append({
                'width': src['width'],
                'height' : src['height'],
                'resolution' : "%sx%s" % (src['width'], src['height']),
                'src': src['src'],
                })
except:
    print("Invalid response received.")
    sys.exit(0)

print("Choose the stream to download from :")

for index, url in enumerate(video_streams):
    print('[%d] (%s) %s' % (index + 1, url['resolution'], url['src']))

index = int(input())

r = requests.get(video_streams[index - 1]['src'], stream=True);
size = int(r.headers['Content-Length'])
size = size // 10**5
pbar = ProgressBar(max_value=100)
filename = '%s.mp4' % video_id
print("Saving to", filename)
with open(filename,'wb') as f:
    for i, chunk in enumerate(r.iter_content(chunk_size=10**5)):
        f.write(chunk)
        pbar.update(int((i / size) * 100))
    


            
