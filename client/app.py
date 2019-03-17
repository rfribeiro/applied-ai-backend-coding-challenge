from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import pika

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
 

class Publisher():
	def publish(_self, text):
		connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
		channel = connection.channel()

		channel.queue_declare(queue='translator', durable=True)

		channel.basic_publish(exchange='',
		                      routing_key='translator',
		                      body=text)

		print(" [x] Sent Text to Translate")
		connection.close()

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
			flash('Text to translate: ' + text)
			publisher = Publisher()
			publisher.publish(text)
		else:
			flash('Error: Text is required ')
	 
	return render_template('translate.html', form=form)
 
if __name__ == "__main__":
	app.run()