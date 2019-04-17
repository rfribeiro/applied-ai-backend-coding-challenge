from project import db, app #db, bcrypt, app, images
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from datetime import datetime
#from markdown import markdown
#from flask import url_for
#import bleach
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer



class ValidationError(ValueError):
    """Class for handling validation errors during
       import of recipe data via API
    """
    pass

class Translation(db.Model):
    __tablename__ = 'translation'
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(app.config['TRANSLATE_TEXT_SIZE']))
    translated = db.Column(db.String(app.config['TRANSLATE_TEXT_SIZE']))
    status = db.Column(db.String(50))
    translated_count = db.Column(db.Integer)
    original_count = db.Column(db.Integer)
    teste = db.Column(db.Integer)

    def __init__(self, original=None, status=None):
        self.original = original
        self.translated = ""
        self.status = status
        self.original_count = len(self.original)
        self.translated_count = 0

    def __repr__(self):
        return '<Message %r>' % (self.original)

    def as_dict(self):
        return {"id": self.id, 
            "original": self.original, 
            "translated": self.translated, 
            "status": self.status, 
            "original_count":self.original_count, 
            "translated_count": self.translated_count}