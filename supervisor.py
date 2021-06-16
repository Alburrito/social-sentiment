import logging
import requests

from resources.utils import SUPERVISOR_CONFIG, SUPERVISOR_LOGGER

def update_twitter_db():
    """
    Returns:
        twitter_ids: list of ids to update
        updated_ids: list of updated ids

    """
    __LOGGER.info('Updating Twitter Profiles...')
    baseUrl = __API_URI
    endpoint = '/twitter/twitter_ids'
    uri = baseUrl + endpoint

    r = requests.get(uri)
    twitter_ids = r.json()["twitter_ids"]
    
    updated_ids = []
    endpoint = '/twitter/update'
    for id in twitter_ids:
        query = f'?twitter_id={id}'
        uri = baseUrl + endpoint + query
        __LOGGER.info(f'Updating profile: {id}')
        try:
            r = requests.get(uri)
            updated_ids.append(id)
            __LOGGER.info('Done')
        except:
            __LOGGER.error('Error updating {id} profile')
            continue

    __LOGGER.info('Twitter DB profiles updated.')
    return twitter_ids, updated_ids


if __name__ == '__main__':
    __API_URI = SUPERVISOR_CONFIG["API_URI"]

    __LOGGER = logging.getLogger(SUPERVISOR_LOGGER)
    __LOGGER.propagate = False

    __LOGGER.debug('=============================')
    __LOGGER.debug(' [*] Supervisor Routine')
    __LOGGER.debug('=============================')
    
    og, up = update_twitter_db()



