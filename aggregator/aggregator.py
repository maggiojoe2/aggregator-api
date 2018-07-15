"""Main module for Aggregator API"""
from datetime import datetime

import requests
from sanic import Sanic
from sanic.response import text

from aggregator.db import save_to_db
from aggregator.log import logger, LOGGING_CONFIG_DEFAULTS


app = Sanic(__name__, log_config=LOGGING_CONFIG_DEFAULTS)
app.static('/test', 'docker-compose.yml')


@app.route('/slack', methods=['POST'])
def inbound_slack(request):
    """inbound post messages from slack"""
    req = request.json
    logger.info(str(req))
    if req['type'] == 'url_verification':
        logger.info('Responding with: %s', req['challenge'])
        return text(req['challenge'])
    elif req['type'] == 'event_callback':
        logger.info('Message recieved')
        get_user = requests.post('https://slack.com/api/users.profile.get', data={'token': SLACK_AUTH_TOKEN, 'user': req['event']['user']})
        noti_obj = {
            "msg": req['event']['text'],
            "from_program": "slack",
            "time_recieved": datetime.fromtimestamp(req['event_time']),
            "sender_name": get_user.json()['profile']['display_name']
        }
        logger.info('Notification Object: %s', noti_obj)
        save_to_db(noti_obj)
        return text('Success')

    return text('Not Found', 404)
