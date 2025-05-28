from hashlib import sha256

import pywikibot
import sqlalchemy
from sqlalchemy.orm import Session

from stargazer.models import PageSegment

AUTO_GENERATED_SEGMENT_HEADER = '<!-- Begin auto-generated segment: {} -->'
AUTO_GENERATED_SEGMENT_FOOTER = '<!-- End auto-generated segment -->'


class SegmentProcessor:
    page_name: str
    segment_name: str
    new_segment: str
    new_hash: str
    session: Session
    page_segment: PageSegment = None

    def __init__(self, page_name: str, segment_name: str, new_segment: str, session: Session) -> None:
        self.page_name = page_name
        self.segment_name = segment_name
        self.new_segment = new_segment
        self.new_hash = sha256(self.new_segment.encode('utf-8')).hexdigest()
        self.session = session

        statement = sqlalchemy.select(PageSegment).where(sqlalchemy.and_(
            PageSegment.page_name == self.page_name, PageSegment.segment_name == self.segment_name))
        self.page_segment: PageSegment | None = self.session.scalar(statement)
        pass

    def should_update(self) -> bool:
        return self.page_segment is None or self.page_segment.segment_hash != self.new_hash

    '''
    Replace the segment on the page and track the new segment state in the database.
    '''
    def process(self, page: pywikibot.Page) -> None:
        if len(page.text) == 0:
            new_page_text = self.new_segment + '\n'
            new_page_text += '\n'
            new_page_text += '\n'
            new_page_text += '\n'
            page.text = new_page_text
        else:
            try:
                page.text = SegmentProcessor.replace_segment(page.text, self.segment_name, self.new_segment)
            except ValueError:
                page.text += self.new_segment

        if self.page_segment is None:
            self.page_segment = PageSegment()
            self.page_segment.page_name = self.page_name
            self.page_segment.segment_name = self.segment_name
            self.page_segment.segment_hash = self.new_hash
            self.session.add(self.page_segment)
        else:
            self.page_segment.segment_hash = self.new_hash

        return

    @staticmethod
    def replace_segment(haystack: str, name: str, new_segment: str) -> str:
        start_index = haystack.index(AUTO_GENERATED_SEGMENT_HEADER.format(name))
        end_index = haystack.index(AUTO_GENERATED_SEGMENT_FOOTER, start_index)
        end_index += len(AUTO_GENERATED_SEGMENT_FOOTER)
        old_segment = haystack[start_index:end_index]
        return haystack.replace(old_segment, new_segment)
