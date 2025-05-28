from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PageSegment(Base):
    __tablename__ = 'page_segments'
    page_name = Column(String, primary_key=True)
    segment_name = Column(String, primary_key=True)
    segment_hash = Column(String, nullable=False)

    def __repr__(self):
        return f'<PageSegment({self.id})>'
