from flask import render_template

from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    db.create_all()

@app.route('/')
def hello_world():
    # 返回主页面
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
