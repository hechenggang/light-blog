# coding=utf-8
from flask import Flask
from tools import kv_cache

app = Flask(__name__)
app.config["admin_username"] = "your username"
app.config["admin_password"] = "your password"
app.secret_key = "5e5705ae-a497-4054-859b-a9af02c2c8b5"
app.config["kv_cache"] = kv_cache()


from view.public import view_of_public
app.register_blueprint(view_of_public,url_prefix='/')

from view.admin import view_of_admin
app.register_blueprint(view_of_admin,url_prefix='/admin')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, debug=True)

