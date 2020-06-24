from sqlalchemy import Column, Integer, String, Text, Float
from sqlalchemy.orm import relationship

from db import Base

class OfferModel(Base):
    __tablename__ = 'offers'
    id = Column(Integer, primary_key=True)
    location = Column(String(50), unique=False)
    email = Column(String(120), unique=False)
    area = Column(Integer, unique= False)
    price = Column(Float, unique= False)
    description = Column(Text, unique= False)
    images = relationship("ImagesModel", cascade="save-update, merge, delete", backref = "offers")

    def __init__(self, location=None, email=None, area=None, price=None, description = None):
        self.area = area
        self.email = email
        self.location = location
        self.price = price
        self.description = description

    def __repr__(self):
        return '<Offer %r>' % (self.location)