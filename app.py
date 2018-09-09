import os
import sys
import csv
from flask import Flask, request, render_template, url_for, g, jsonify, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
app = Flask(__name__)

channel_secret = os.environ['LINE_CHANNEL_SECRET']
channel_access_token = os.environ['LINE_CHANNEL_ACCESS_TOKEN']

if channel_secret is None or channel_access_token is None:
    app.config.from_pyfile('config.py')
    channel_secret = app.config.get('LINE_CHANNEL_SECRET')
    channel_access_token = app.config.get('LINE_CHANNEL_ACCESS_TOKEN')


line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


def search(title: str):
    results = []
    csvfile = 'play1.csv'
    f = open(csvfile, "r")
    reader = csv.reader(f)

    for row in reader:
        if title == row[0]:
            results.append((row[1], row[2]))

    f.close()
    return results


@app.route('/')
def top():
    return render_template('top.html')


@app.route('/result', methods=['POST'])
def result():
    title = request.form.get('title')
    results = search(title)
    return render_template('result.html', results=results)


if __name__ == '__main__':
    app.run(debug=True)
