import io
import os
import re
import hashlib
import json

from flask import Flask, render_template
from flask import request, redirect, url_for
from flask import Response, make_response
from flask import abort

from String2emoji import String2emoji

from apps       import config
from apps.cache import create as create_cache


app = Flask(__name__)

# enable debug mode if on development environment
app.debug = config.debug
app.jinja_env.globals['debug'] = config.debug

# compute JavaScript checksum
if not config.debug:
    app.jinja_env.globals['js_min_checksum'] = \
            hashlib.md5(open(config.js_min_path, 'rb').read()).hexdigest()

# setup image cache
if config.memcached_enabled:
    print('Use MemcachedCache')

cache = create_cache(
        config.memcached_enabled,
        config.cache_timeout,
        config.memcached_servers
        )

fonts_list = config.fonts

# -----------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.j2')

@app.route('/emoji')
def emoji():
    font_default = 'mplus-1p-black'
    font_key = request.args.get("font", default=font_default, type=str)
    text = request.args.get("text", default='test', type=str)
    color = request.args.get("color", default='000000', type=str).upper()
    font = fonts_list.get(font_key,font_default).get('file')
    if text is False:
        text = ' '
    if color is False:
        color = '000000'
    img_png = generate_emoji(text,font,color)

    if not img_png:
        return abort(400)

    res = make_response()
    res.data = img_png
    res.headers['Content-Type'] = 'image/png'
    return res

@app.route('/emoji_download')
def emoji_download():
    font_default = 'mplus-1p-black'
    font_key = request.args.get("font", default=font_default, type=str)
    text = request.args.get("text", default='test', type=str)
    color = request.args.get("color", default='000000', type=str).upper()
    font = fonts_list.get(font_key,font_default).get('file')
    if text is False:
        text = ' '
    if color is False:
        color = '000000'
    img_png = generate_emoji(text,font,color)
    disp = 'attachment;' + \
           'filename=\"' + re.sub(r'\s','_',text) + '.png\"'
    res = make_response()
    res.data = img_png
    res.headers['Content-Type'] = 'image/png'
    res.headers['Content-Disposition'] = disp.encode('utf-8')
    return res

@app.route('/api/fonts')
def api_fonts():
    font_items        = list(fonts_list.items())
    sorted_font_items = sorted(font_items, key=lambda item: item[1]['order'])
    fonts             = [
        { 'key': item[0], 'name': item[1]['name'] }
        for item in sorted_font_items
    ]

    res = make_response()
    res.data = json.dumps(fonts)
    res.headers['Content-Type'] = 'application/json'
    return res

def generate_emoji(text,font,color):
    global cache
    hash_text = text + ':' + color + ':' + font
    r = int(color[0] +color[1],16)
    g = int(color[2] +color[3],16)
    b = int(color[4] +color[5],16)
    cache_id = hashlib.md5(hash_text.encode('utf-8')).hexdigest()
    img_png = cache.get(cache_id)
    if img_png is None:
        lines = text.splitlines()

        if len(text) > 100: # XXX: 100 文字以上
            return None

        if len(lines) == 1 and len(lines[0]) > 10: # XXX: 1 列 10 文字以上
            return None

        if len(lines) > 10: # XXX: 10 行以上
            return None

        emoji = String2emoji(lines, 'assets/fonts/' + font,(r,g,b))
        img = emoji.getEmoji()
        output = io.BytesIO()
        img.save(output,format='png')
        img_png = output.getvalue()
        cache.set(cache_id,img_png)
    return img_png

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
