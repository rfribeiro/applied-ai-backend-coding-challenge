from flask import render_template, Blueprint, request, redirect, url_for, abort, jsonify, g, flash
from project import db, app
from project.models import Translation
from project.communication import Publisher
from .forms import ReusableForm
import json

translate_blueprint = Blueprint('translate', __name__)

def is_post():
    return (request.method == 'POST')

#@app.route("/", methods=['GET', 'POST'])
#@app.route("/index", methods=['GET', 'POST'])
#@app.route("/translate", methods=['GET', 'POST'])
@translate_blueprint.route('/', methods=['GET','POST'])
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