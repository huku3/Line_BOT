import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, StickerSendMessage
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(override=True)

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ["ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["CHANNEL_SECRET"])


@app.route("/")
def index():
    return "You call index()"


@app.route("/callback", methods=["POST"])
def callback():
    """Messaging APIからの呼び出し関数"""
    # LINEがリクエストの改ざんを防ぐために付与する署名を取得
    signature = request.headers["X-Line-Signature"]
    # リクエストの内容をテキストで取得
    body = request.get_data(as_text=True)
    # ログに出力
    app.logger.info("Request body: " + body)

    try:
        # signature と body を比較することで、リクエストがLINEから送信されたものであることを検証
        handler.handle(body, signature)
    except InvalidSignatureError:
        # クライアントからのリクエストに誤りがあったことを示すエラーを返す
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # ユーザーのメッセージを取得
    user_message = event.message.text

    # 特定のキーワードでスタンプを送信
    if "スタンプ" in user_message or "stamp" in user_message.lower():
        # スタンプを送信（パッケージID: 11537, スタンプID: 52002734 は例）
        sticker_message = StickerSendMessage(package_id="11537", sticker_id="52002734")
        line_bot_api.reply_message(event.reply_token, sticker_message)
    else:
        # 通常の日時メッセージを送信
        send_message = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=send_message))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 1000))
    app.run(host="0.0.0.0", port=port)
