"""Main module for Aggregator API"""
from datetime import datetime
import os

import requests

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bson.objectid import ObjectId
from sanic import Sanic
from sanic.response import text, json
from sanic_cors import CORS

from aggregator.db import save_to_db, retrieve_objects_from_db, connect_to_mongo, disconnect_mongo, update_fields
from aggregator.log import logger, LOGGING_CONFIG_DEFAULTS
from aggregator.gmail import get_facebook


app = Sanic(__name__, log_config=LOGGING_CONFIG_DEFAULTS)
CORS(app, automatic_options=True)
app.static('/test', 'docker-compose.yml')


@app.listener('before_server_start')
async def initialize_scheduler(_, loop):
    """Initialize scheduler for periodic sending of scheduled emails every minute.

    Args:
        loop (AbstractEventLoop): event loop
    """
    logger.info('Initializing Scheduler.')
    scheduler = AsyncIOScheduler({'event_loop': loop}, timezone='UTC')
    scheduler.add_job(get_facebook, 'interval', seconds=10)
    scheduler.start()
    logger.info('Scheduler started.')


@app.route('/slack', methods=['POST'])
async def inbound_slack(request):
    """inbound post messages from slack"""
    req = request.json
    logger.info(str(req))
    if req['type'] == 'url_verification':
        logger.info('Responding with: %s', req['challenge'])
        return text(req['challenge'])
    elif req['type'] == 'event_callback':
        if any(word in req['event']['text'] for word in ['Viasat', 'Viasat 3', 'meeting', 'wifi']):
            logger.info('Message recieved')
            get_user = requests.post('https://slack.com/api/users.profile.get', data={'token': str(os.environ['SLACK_AUTH_TOKEN']), 'user': req['event']['user']})
            noti_obj = {
                "msg": req['event']['text'],
                "from_program": "slack",
                "time_received": datetime.fromtimestamp(req['event_time']),
                "sender_name": get_user.json()['profile']['display_name'],
                "url": "https://aggregator-app.slack.com",
                "read": False
            }
            logger.info('Notification Object: %s', noti_obj)
            await save_to_db(noti_obj)
        return text('Success')

    return text('Not Found', 404)


@app.route('/notifications/<noti_id>', methods=['PUT'])
async def update_status(request, noti_id):
    """Update status to read or unread."""
    try:
        if request.args['read']:
            query = [
                {"field": "read", "field_value": bool(request.args['read']), "operation": "$set"}
            ]
            await update_fields(query, ObjectId(noti_id), database='email_db', collection='email_collection')
            return text('Success', 200)

        return text('Cannot update that field.', 400)
    except Exception:
        return text('Cannot update field', 400)


@app.route('/notifications/<noti_id>', methods=['DELETE'])
async def delete_notification(_, noti_id):
    """Delete notifications"""
    try:
        db = await connect_to_mongo()
        db['email_db']['email_collection'].delete_one({"_id": ObjectId(noti_id)})
        await disconnect_mongo(db)

        return text("Deleted")
    except Exception:
        return text('Failed to delete.', 400)


@app.route('/notifications', methods=['GET'])
async def get_notifications(_):
    """Get notifications."""
    db = await connect_to_mongo()
    notifications = db['email_db']['email_collection'].find().sort([('time_received', -1)])
    # notifications = await retrieve_objects_from_db(query, 'email_db', 'email_collection', find_one=False)
    await disconnect_mongo(db)

    noti_list = []
    for noti in notifications:
        noti['_id'] = str(noti['_id'])
        noti['time_received'] = noti['time_received'].isoformat()
        noti_list.append(noti)
    logger.info(noti_list)
    return json({"data": noti_list})
