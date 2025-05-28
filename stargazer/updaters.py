import logging
import os.path

import pywikibot
from sqlalchemy.orm import Session

from stargazer.entity import EntityPrototype
from stargazer.segments import SegmentProcessor

log = logging.getLogger(__name__)


AUTO_GENERATED_SEGMENT_HEADER = '<!-- Begin auto-generated segment: {} -->'
AUTO_GENERATED_SEGMENT_FOOTER = '<!-- End auto-generated segment -->'


class Updater:
    def __init__(self, session: Session, site: pywikibot.Site):
        self.session = session
        self.site = site
        pass


class SpriteUpdater(Updater):
    sprites: list[str]

    def prepare(self, **kwargs) -> None:
        entities: dict[str, EntityPrototype] = kwargs['entities']

        # check for sprite for each entity
        self.sprites: list[tuple[str, str]] = []

        for entity in entities.values():
            sprite_path = entity.sprite_path()
            if sprite_path is None:
                continue
            self.sprites.append((sprite_path, SpriteUpdater.file_id_from_path(sprite_path)))

        # calculate hash for sprite png
        pass

    def run(self, **kwargs) -> None:
        # if hash does not match database for sprite,
        # ... upload/update sprite on wiki
        # ... update version hash in db
        # else, continue loop
        pass

    @staticmethod
    def file_id_from_path(path: str) -> str | None:
        # convert `Textures/Mobs/Animals/mothroach/mothroach.rsi/icon.png` into
        # `Mothroach.rsi (icon, Textures-Mobs-Animals-mothroach).png`

        if '.rsi' in path:
            state_name = os.path.splitext(os.path.basename(path))[0]
            rsi_path = os.path.dirname(path)
            rsi_name = os.path.basename(rsi_path)
            indicator = os.path.dirname(rsi_path).replace('\\', '/').replace('/', '-')

            file_id = f'{rsi_name} ({state_name}, {indicator}).png'
        else:
            log.warning(f'Unable to convert sprite file path: {path}')
            return None

        return file_id

    @staticmethod
    def generate_summary(path: str) -> str:
        summary = ''
        summary += '<!-- Begin auto-generated segment: File summary -->' + os.linesep
        summary += f'File path: {path}' + os.linesep

        # load rsi meta.json
        # ...

        summary += f'License: ' + os.linesep

        summary += f'Attribution: ' + os.linesep

        # link to github commit ...
        # summary += f'Source: ' + os.linesep

        summary += '<!-- End auto-generated segment -->' + os.linesep
        return summary


class EntityUpdater(Updater):
    def __init__(self, session: Session, site: pywikibot.Site, **kwargs):
        super().__init__(session, site)
        self.entities = kwargs.get('entities')
        self.base_path = kwargs.get('base_path', '.')


    def run(self) -> None:
        for entity_id, entity in self.entities.items():
            # capitalize the first letter or pywikibot will throw a fit (InconsistentTitleError)
            normalized_entity_id = entity_id[0].upper() + entity_id[1:]
            page_name = f'Entity:{normalized_entity_id}'
            infobox_segment = EntityUpdater.generate_infobox(entity)
            infobox_processor = SegmentProcessor(page_name, 'Infobox', infobox_segment, self.session)
            category_segment = EntityUpdater.generate_categories(entity)
            category_processor = SegmentProcessor(page_name, 'Categories', category_segment, self.session)

            try:
                should_update = infobox_processor.should_update() or category_processor.should_update()
                if should_update:
                    log.debug(f'Updating {page_name}...')
                    page = pywikibot.Page(self.site, page_name)
                    infobox_processor.process(page)
                    category_processor.process(page)
                    page.put(page.text, f'stargazer: a66e644b10')
                    self.session.commit()
            except Exception as e:
                log.error(
                    f'Failed to update page for entity: {entity_id} ({e}) skipping...')
                continue


    @staticmethod
    def replace_segment(haystack: str, name: str, new_segment: str) -> str:
        start_index = haystack.index(AUTO_GENERATED_SEGMENT_HEADER.format(name))
        end_index = haystack.index(AUTO_GENERATED_SEGMENT_FOOTER, start_index)
        end_index += len(AUTO_GENERATED_SEGMENT_FOOTER)
        old_segment = haystack[start_index:end_index]
        return haystack.replace(old_segment, new_segment)


    @staticmethod
    def generate_infobox(entity: EntityPrototype):
        output = AUTO_GENERATED_SEGMENT_HEADER.format('Infobox') + os.linesep
        output += '{{Infobox PrototypeEntity' + os.linesep
        output += f'|id = {entity.id}' + os.linesep
        # output += f'|image = {entity.id}' + os.linesep  # TODO: select sprites, upload or updating them (with licensing)
        output += f'|name = {entity.name}' + os.linesep
        output += f'|description = {entity.description}' + os.linesep

        parent_str = ''
        for parent in entity.parents:
            parent_str += f'[[Entity:{parent}]], '
        parent_str = parent_str[:-2]
        output += f'|parents = {parent_str}' + os.linesep

        if entity.abstract:
            output += f'|abstract = true' + os.linesep

        src_string = entity.meta.file_path
        if entity.meta.line_number != -1:
            src_string += f'#L{entity.meta.line_number}'
        output += f'|source = {{{{SourceLink|{src_string}}}}}' + os.linesep

        output += '}}' + os.linesep
        output += AUTO_GENERATED_SEGMENT_FOOTER

        return output


    @staticmethod
    def generate_categories(entity: EntityPrototype) -> str:
        output = AUTO_GENERATED_SEGMENT_HEADER.format('Categories') + os.linesep

        output += '[[Category:Entities]]' + os.linesep

        if entity.has_component('Item'):
            output += '[[Category:Items]]' + os.linesep

        if entity.has_component('Mail'):
            output += '[[Category:Mail]]' + os.linesep

        if entity.has_component('Food'):
            output += '[[Category:Food]]' + os.linesep

        if entity.has_component('Cartridge'):
            output += '[[Category:Cartridges]]' + os.linesep

        if entity.has_component('Clothing'):
            output += '[[Category:Clothing]]' + os.linesep

        if entity.has_tag('Figurine'):
            output += '[[Category:Figurines]]' + os.linesep

        if entity.has_tag('Trash'):
            output += '[[Category:Trash]]' + os.linesep

        output += AUTO_GENERATED_SEGMENT_FOOTER
        return output
