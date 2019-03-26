from flask import Flask, render_template, flash, request, url_for
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
import pylibmc
from flask_session import Session
import os
import json
from config import DevelopmentConfig, ProductionConfig

# App config.
DEBUG = True
config = DevelopmentConfig()
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.cache = Cache()

cache_servers = os.environ.get('MEMCACHIER_SERVERS')
if cache_servers == None:
    app.cache.init_app(app, config={'CACHE_TYPE': 'simple'})
    print('simple cache')
else:
    cache_user = os.environ.get('MEMCACHIER_USERNAME') or ''
    cache_pass = os.environ.get('MEMCACHIER_PASSWORD') or ''
    app.cache.init_app(app,
        config={'CACHE_TYPE': 'memcached',
                'CACHE_MEMCACHED_SERVERS': cache_servers.split(','),
                'CACHE_MEMCACHED_USERNAME': cache_user,
                'CACHE_MEMCACHED_PASSWORD': cache_pass
                #'CACHE_OPTIONS': { 'behaviors': {
                #    # Faster IO
                #    'tcp_nodelay': True,
                #    # Keep connection alive
                #    'tcp_keepalive': True,
                #    # Timeout for set/get requests
                #    'connect_timeout': 2000, # ms
                #    'send_timeout': 750 * 1000, # us
                #    'receive_timeout': 750 * 1000, # us
                #    '_poll_timeout': 2000, # ms
                #    # Better failover
                #    'ketama': True,
                #    'remove_failed': 1,
                #    'retry_timeout': 2,
                #    'dead_timeout': 10}}
                })
    print('memcached cache')
    app.config.update(
	    SESSION_TYPE = 'memcached',
	    SESSION_MEMCACHED =
	        pylibmc.Client(cache_servers.split(','), binary=True,
	                       username=cache_user, password=cache_pass,
	                       behaviors={
	                            # Faster IO
	                            'tcp_nodelay': True,
	                            # Keep connection alive
	                            'tcp_keepalive': True,
	                            # Timeout for set/get requests
	                            'connect_timeout': 2000, # ms
	                            'send_timeout': 750 * 1000, # us
	                            'receive_timeout': 750 * 1000, # us
	                            '_poll_timeout': 2000, # ms
	                            # Better failover
	                            'ketama': True,
	                            'remove_failed': 1,
	                            'retry_timeout': 2,
	                            'dead_timeout': 10,
	                       })
	)

Session(app)


#from database import db_session
from models import Translation
from communication import Publisher
from forms import ReusableForm

def is_post():
    return (request.method == 'POST')

@app.route("/", methods=['GET', 'POST'])
@app.route("/index", methods=['GET', 'POST'])
@app.route("/translate", methods=['GET', 'POST'])
#@app.cache.memoize(timeout=5)
@app.cache.cached(timeout=5, key_prefix='page')
def translate():
	form = ReusableForm(request.form)
	print (form.errors)

	if request.method == 'POST':
		text=request.form['text']
		print (text)
	 
		if form.validate():
			# Save the comment here.
			# save database
			try:
				result = Translation(
					original=text,
					status='requested',
				)
				db.session.add(result)
				db.session.commit()
				
				#app.cache.delete_memoized(get_all_translations)
				app.cache.delete('get_all_translations')
				
				print(" [x] Saved Text to Translate " + str(result.id))
			except Exception as e:
				print (e)
				flash('Error: Saving database')
				return redirect(url_for('translate.html', form=form))

			#send request
			publisher = Publisher()
			publisher.publish(json.dumps(result.as_dict()))
			print(" [x] Sent Text to Translate " + json.dumps(result.as_dict()))

			flash(text)
		else:
			flash('Error: Text is required')
	 
	translations = get_all_translations() 

	return render_template('translate.html', title='Home', form=form,
	                       translations=translations)

#@app.cache.memoize()
@app.cache.cached(timeout=5, key_prefix='get_all_translations')
def get_all_translations():
    return Translation.query.order_by(Translation.translated_count.desc()).all()


if __name__ == "__main__":
	app.run()