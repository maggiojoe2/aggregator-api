"""Main module for Aggregator API"""
from sanic import Sanic
from sanic.response import text

from aggregator.log import logger, LOGGING_CONFIG_DEFAULTS


app = Sanic(__name__, log_config=LOGGING_CONFIG_DEFAULTS)
app.static('/test', 'docker-compose.yml')


@app.route('/slack', methods=['POST'])
def inbound_slack(request):
    """inbound post messages from slack"""
#     if request.form.get('token') == SLACK_WEBHOOK_SECRET:
#         channel = request.form.get('channel_name')
#         username = request.form.get('user_name')
#         text = request.form.get('text')
#         inbound_message = username + " in " + channel + " says: " + text
#         print(inbound_message)
#     return Response(), 200
    req = request.json
    logger.info(str(req))
    if "challenge" in req.keys():
        return text(req['challenge'])

    return
