# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy.types import LargeBinary
from db import Base

class ImagesModel(Base):
    __tablename__ = 'Imagesdata'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('offers.id'))
    cla = Column(String(120), unique = False, nullable = True)
    imagePath = Column(String(120), unique = False )
    #posting = relationship("Posting",backref=backref("postings", cascade="all, delete-orphan"))
    
    def __init__(self, cla=None, parent_id = None, imagePath = None):
        self.cla = cla
        self.parent_id = parent_id
        self.imagePath = imagePath
        
    def __repr__(self):
        return '<Image %r>' % (self.imagePath)
