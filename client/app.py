from flask import Flask, render_template, flash, request, url_for
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from flask_sqlalchemy import SQLAlchemy
import os
import json

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#from database import db_session
from models import Translation
from communication import Publisher
from forms import ReusableForm

@app.route("/", methods=['GET', 'POST'])
@app.route("/index", methods=['GET', 'POST'])
@app.route("/translate", methods=['GET', 'POST'])
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
			flash('Error: Text is required ')
	 
	page = request.args.get('page', 1, type=int)
	translations_table = Translation.query.order_by(Translation.translated_count.desc()).paginate(
	    page, app.config['TRANSLATIONS_PER_PAGE'], False)

	next_url = url_for('translate', page=translations_table.next_num) \
	    if translations_table.has_next else None
	prev_url = url_for('translate', page=translations_table.prev_num) \
	    if translations_table.has_prev else None

	return render_template('translate.html', title='Home', form=form,
	                       translations_table=translations_table.items, next_url=next_url,
	                       prev_url=prev_url)

 
if __name__ == "__main__":
	app.run()