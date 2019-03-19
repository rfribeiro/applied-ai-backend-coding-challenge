from flask import Flask, render_template, flash, request
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

class ReusableForm(Form):
	text = TextField('Text:', validators=[validators.required()])
 
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
				return render_template('translate.html', form=form)

			#send request
			publisher = Publisher()
			publisher.publish(json.dumps(result.as_dict()))
			print(" [x] Sent Text to Translate " + json.dumps(result.as_dict()))

			flash('Text to translate: ' + text)
		else:
			flash('Error: Text is required ')
	 
	return render_template('translate.html', form=form)
 
if __name__ == "__main__":
	app.run()