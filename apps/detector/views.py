from apps.app import db
from apps.crud.models import User
from apps.detector.models import UserImage

from flask import Blueprint, render_template, current_app, send_from_directory

dt = Blueprint("detector", __name__, template_folder="templates")


# dtアプリケーションを使ってエンドポイント作成
@dt.route("/")
def index():
    # UserとUserImageを結合して画像一覧を取得する。
    user_images = (
        db.session.query(User, UserImage)
        .join(UserImage)
        .filter(User.id == UserImage.user_id)
        .all()
    )
    return render_template("detector/index.html")


@dt.route("/images/<path:filename>")
def image_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
