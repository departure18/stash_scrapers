import sys
import json
from urllib.parse import urlparse
import requests_cache
from selectolax.parser import HTMLParser


def debug_print(*s):
    print(*s, file=sys.stderr)


STUDIO_NAMES = {
    'www.williamhiggins.com': 'William Higgins',
    'www.str8hell.com': 'Str8 Hell',
    'www.swnude.com': 'Submission Wrestling Nude',
    'www.ambushmassage.com': 'Ambush Massage',
    'www.cfnmeu.com': 'CFMN Europe',
    'www.malefeet4u.com': 'Male Feet 4U',
}

json_frag = json.load(sys.stdin)

debug_print(json_frag)
debug_print(sys.argv)

if sys.argv[1] == 'scene':
    parsed_url = urlparse(json_frag['url'])
    host = parsed_url.netloc
    split_path = parsed_url.path.split('/')
    scene_id = split_path[-1] if split_path[-1] != '' else split_path[-2]
    debug_print(scene_id)
    session = requests_cache.CachedSession('demo_cache')
    session.headers.update(
        {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.99 Safari/537.36'
        }
    )
    query = {'setid': scene_id}
    resp = session.get(f'https://{host}/api/set/data', params=query)
    r_json = resp.json()
    debug_print(r_json)
    date = r_json['data']['public_date'].split('/')
    date = '{}-{}-{}'.format(date[2], date[1], date[0])
    image_url = r_json['data']['main_image']
    if urlparse(image_url).netloc == '':
        image_url = f'https://{host}/{image_url}'
        debug_print(image_url)
    scene = {
        'title': r_json['data']['name']
        + ' - '
        + r_json['data']['category_name'],
        'details': r_json['data']['info'],
        'image': image_url,
        'studio': {'name': STUDIO_NAMES[host]},
        'date': date,
    }

    performer_box = session.get(
        f'https://{host}/api/set/set-model-info',
        params={'id': r_json['data']['id']},
    )
    debug_print(performer_box.url)
    box_parser = HTMLParser(performer_box.text)
    performer_names = []
    for t in box_parser.css('table'):
        debug_print(t.css('a')[1].html)
        performer_names.append(
            {'name': t.css('a')[1].text(), 'gender': 'male'}
        )
    scene['performers'] = performer_names

    debug_print(scene)
    print(json.dumps(scene))
