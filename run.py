import eventlet
eventlet.monkey_patch()

import os

from app import create_app
from app.extensions import socketio

config_name = os.environ.get('FLASK_ENV') or 'dev'
app = create_app(config_name)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    socketio.run(app, host='0.0.0.0', port=port, use_reloader=False)