from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base: type = declarative_base()


class PageSegment(Base):
    __tablename__ = "page_segments"
    page_name: Column[str] | str = Column(String, primary_key=True)
    segment_name: Column[str] | str = Column(String, primary_key=True)
    segment_hash: Column[str] | str = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f"<PageSegment({self.page_name})>"
