# -*- encoding: utf-8 -*-

import os
import yaml

# 'development' or 'production'
env   = os.getenv('FLASK_ENV', 'development')
debug = env == 'development'

config_path = \
    os.path.join(os.path.dirname(__file__), '../config/common.yml')

# 'config/development.py' or $FLASK_CONFIG_PATH
env_config_path = os.getenv(
    'FLASK_CONFIG_PATH',
    os.path.join(os.path.dirname(__file__), '../config/development.yml')
    )

# bundled JavaScript path
js_min_path = os.path.join(os.path.dirname(__file__), '../static/js/bundle.min.js')

# configs from YAML file
_config     = yaml.load(open(config_path, 'r', encoding='utf-8'))
_env_config = yaml.load(open(env_config_path, 'r', encoding='utf-8'))

cache_timeout     = _env_config['cache']['timeout']
memcached_enabled = _env_config['cache']['memcached']['enabled']
memcached_servers = _env_config['cache']['memcached']['servers']

fonts = _config['fonts']
