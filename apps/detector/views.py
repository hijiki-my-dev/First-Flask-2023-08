from flask import Blueprint, render_template

dt = Blueprint("detector", __name__, template_folder="templates")


# dtアプリケーションを使ってエンドポイント作成
@dt.route("/")
def index():
    return render_template("detector/index.html")
