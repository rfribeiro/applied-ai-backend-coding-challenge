#from sqlalchemy import Column, Integer, String, DateTime
#from database import Base
#from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import JSON

class Translation(db.Model):
    __tablename__ = 'translation'
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(300))
    translated = db.Column(db.String(300))
    status = db.Column(db.String(50))
    translated_count = db.Column(db.Integer)

    def __init__(self, original=None, status=None):
        self.original = original
        self.translated = ""
        self.status = status
        self.translated_count = 0

    def __repr__(self):
        return '<Message %r>' % (self.original)