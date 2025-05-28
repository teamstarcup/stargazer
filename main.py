import logging
import os
import sys

import pywikibot
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from stargazer.entity import load_entities, EntityPrototype
from stargazer.updaters import EntityUpdater

BASE_PATH = 'E:/Development/SS14/Starcup/starcup'

SOURCE_PATH = 'https://github.com/teamstarcup/starcup/blob/'
COMMIT_HASH_SHORT = 'a66e644b10'

log = logging.getLogger(__name__)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                        level=logging.DEBUG,
                        stream=sys.stdout)

    load_dotenv()

    db_host = os.environ.get('STARGAZER_DB_HOST')
    db_port = os.environ.get('STARGAZER_DB_PORT')
    db_user = os.environ.get('STARGAZER_DB_USER')
    db_pass = os.environ.get('STARGAZER_DB_PASS')
    db_name = os.environ.get('STARGAZER_DB_NAME')

    engine = create_engine(f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}')
    session = Session(engine)

    site = pywikibot.Site('en', 'starcup')
    site.throttle.setDelays(2, 2)

    # load entity prototypes
    log.info('Loading entity prototypes...')
    entities: dict[str, EntityPrototype] = load_entities(BASE_PATH)
    log.info(f'Loaded {len(entities)} entity prototypes!')

    # resolve entity inheritance
    log.info(f'Resolving entity inheritance trees...')
    for entity_id, entity in entities.items():
        entity.resolve(entities)
    log.info(f'Resolved entity inheritances!')

    log.info(f'Updating entities...')
    entity_updater = EntityUpdater(session, site, entities=entities, base_path=BASE_PATH)
    entity_updater.run()
