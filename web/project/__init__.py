#################
#### imports ####
#################

from os.path import join, isfile

from flask import Flask, render_template, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
import pylibmc
from flask_session import Session
from flask_migrate import Migrate
import os


################
#### config ####
################

app = Flask(__name__, instance_relative_config=True)
if isfile(join('instance', 'flask_full.cfg')):
    app.config.from_pyfile('flask_full.cfg')
else:
    app.config.from_pyfile('flask.cfg')

app.secret_key = os.urandom(24)

app.config['SESSION_TYPE'] = 'filesystem'

print('Creating db!')
db = SQLAlchemy(app)

print('migrating db')
migrate = Migrate(app, db)

print('Creating cache!')
app.cache = Cache()

#cache_servers = app.config['CACHE_MEMCACHED_SERVERS']
print('cache servers: ', cache_servers)
#if cache_servers == None:
app.cache.init_app(app, config={'CACHE_TYPE': 'simple'})
print('simple cache')
#else:
#    cache_user = os.environ.get('CACHE_MEMCACHED_USERNAME') or ''
#    cache_pass = os.environ.get('CACHE_MEMCACHED_PASSWORD') or ''
#    cache.init_app(app,
#        config={'CACHE_TYPE': 'memcached',
#                'CACHE_MEMCACHED_SERVERS': ['172.19.0.4:11211'],
#                'CACHE_MEMCACHED_USERNAME': app.config['CACHE_MEMCACHED_USERNAME'],
#                'CACHE_MEMCACHED_PASSWORD': app.config['CACHE_MEMCACHED_PASSWORD']
#                })
#    print('memcached cache')
#    app.config.update(
#        SESSION_TYPE = 'memcached',
#        SESSION_MEMCACHED =
#            pylibmc.Client(['172.19.0.4:11211'], binary=True,
#                           username=cache_user, password=cache_pass,
#                           behaviors={
#                                # Faster IO
#                                'tcp_nodelay': True,
#                                # Keep connection alive
#                                'tcp_keepalive': True,
#                                # Timeout for set/get requests
#                                'connect_timeout': 2000, # ms
#                                'send_timeout': 750 * 1000, # us
#                                'receive_timeout': 750 * 1000, # us
#                                '_poll_timeout': 2000, # ms
#                                # Better failover
#                                'ketama': True,
#                                'remove_failed': 1,
#                                'retry_timeout': 2,
#                                'dead_timeout': 10,
#                           })
#    )
#
Session(app)

from project.models import Translation


####################
#### blueprints ####
####################

from project.translate.views import translate_blueprint

# register the blueprints
app.register_blueprint(translate_blueprint)


############################
#### custom error pages ####
############################

from project.models import ValidationError


@app.errorhandler(ValidationError)
def bad_request(e):
    response = jsonify({'status': 400, 'error': 'bad request',
                        'message': e.args[0]})
    response.status_code = 400
    return response


@app.errorhandler(400)
def page_not_found(e):
    return make_response(jsonify({'error': 'Not found'}), 400)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# @app.errorhandler(404)
# def not_found(e):
#     response = jsonify({'status': 404, 'error': 'not found', 'message': 'invalid resource URI'})
#     response.status_code = 404
#     return response


@app.errorhandler(403)
def page_not_found(e):
    return render_template('403.html'), 403


@app.errorhandler(410)
def page_not_found(e):
    return render_template('410.html'), 410
