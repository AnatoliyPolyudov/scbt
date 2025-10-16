from flask import Flask, request
from callback_handler import handle_callback

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    data = request.json
    callback_data = data['callback_query']['data']
    handle_callback(callback_data)
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
