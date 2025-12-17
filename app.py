from flask import render_template

from app import create_app, socketio
from app.extensions import db

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
