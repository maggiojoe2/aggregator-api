"""Main module for Aggregator API"""
from datetime import datetime
import os

import requests
from sanic import Sanic
from sanic.response import text, json
from sanic_cors import CORS

from aggregator.db import save_to_db, retrieve_objects_from_db
from aggregator.log import logger, LOGGING_CONFIG_DEFAULTS


app = Sanic(__name__, log_config=LOGGING_CONFIG_DEFAULTS)
CORS(app, automatic_options=True)
app.static('/test', 'docker-compose.yml')


@app.route('/slack', methods=['POST'])
async def inbound_slack(request):
    """inbound post messages from slack"""
    req = request.json
    logger.info(str(req))
    if req['type'] == 'url_verification':
        logger.info('Responding with: %s', req['challenge'])
        return text(req['challenge'])
    elif req['type'] == 'event_callback':
        logger.info('Message recieved')
        get_user = requests.post('https://slack.com/api/users.profile.get', data={'token': str(os.environ['SLACK_AUTH_TOKEN']), 'user': req['event']['user']})
        noti_obj = {
            "msg": req['event']['text'],
            "from_program": "slack",
            "time_recieved": datetime.fromtimestamp(req['event_time']),
            "sender_name": get_user.json()['profile']['display_name'],
            "url": "https://aggregator-app.slack.com",
            "read": False
        }
        logger.info('Notification Object: %s', noti_obj)
        await save_to_db(noti_obj)
        return text('Success')

    return text('Not Found', 404)


@app.route('/notifications', methods=['GET'])
async def get_notifications(_):
    """Get notifications."""
    query = {'read': False}
    notifications = await retrieve_objects_from_db(query, 'email_db', 'email_collection', find_one=False)

    noti_list = []
    for noti in notifications:
        noti['_id'] = str(noti['_id'])
        noti['time_received'] = noti['time_received'].isoformat()
        noti_list.append(noti)
    logger.info(noti_list)
    return json({"data": noti_list})
