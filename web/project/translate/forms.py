#from flask_wtf import FlaskForm
from project import app
from wtforms import Form, TextField, StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length

from project.models import Translation


#class TranslateForm(FlaskForm):
#    post = TextAreaField('Text:', validators=[DataRequired(),Length(min=1, max=config.TRANSLATE_TEXT_SIZE)])
#    submit = SubmitField('Translate')

class ReusableForm(Form):
  text = TextField('Text:', validators=[DataRequired(), Length(max=app.config['TRANSLATE_TEXT_SIZE'])])