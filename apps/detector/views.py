import random
import cv2
import numpy as np
import torch
import torchvision

import uuid
from pathlib import Path

from apps.app import db
from apps.crud.models import User
from apps.detector.models import UserImage, UserImageTag
from apps.detector.forms import UploadImageForm, DetectorForm, DeleteForm

from flask import (
    Blueprint,
    render_template,
    current_app,
    send_from_directory,
    redirect,
    url_for,
    flash,
)

from PIL import Image
from sqlalchemy.exc import SQLAlchemyError

from flask_login import current_user, login_required

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

    # タグ一覧を取得
    user_image_tag_dict = {}
    for user_image in user_images:
        user_image_tags = (
            db.session.query(UserImageTag)
            .filter(UserImageTag.user_image_id == user_image.UserImage.id)
            .all()
        )
        user_image_tag_dict[user_image.UserImage.id] = user_image_tags

    # 物体検知フォームをインスタンス化
    detector_form = DetectorForm()
    # DeleteFormをインスタンス化する
    delete_form = DeleteForm()

    return render_template(
        "detector/index.html",
        user_images=user_images,
        user_image_tag_dict=user_image_tag_dict,
        detector_form=detector_form,
        delete_form=delete_form,
    )


@dt.route("/images/<path:filename>")
def image_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


@dt.route("/upload", methods=["GET", "POST"])
@login_required
def upload_image():
    form = UploadImageForm()
    if form.validate_on_submit():
        # アップされた画像データを取得
        file = form.image.data
        # ファイル名と拡張子を取得、UUIDに変換する（セキュリティー）
        ext = Path(file.filename).suffix
        image_uuid_file_name = str(uuid.uuid4()) + ext

        # 画像を保存
        image_path = Path(current_app.config["UPLOAD_FOLDER"], image_uuid_file_name)
        file.save(image_path)

        # DBに保存
        user_image = UserImage(user_id=current_user.id, image_path=image_uuid_file_name)
        db.session.add(user_image)
        db.session.commit()

        return redirect(url_for("detector.index"))
    return render_template("detector/upload.html", form=form)


# 画像処理系関数
# 枠線の色をランダムに決定
def make_color(labels):
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in labels]
    color = random.choice(colors)
    return color


# 枠線を作成
def make_line(result_image):
    line = round(0.002 * max(result_image.shape[0:2])) * 1
    return line


# 四角形の枠線を画像に追記
def draw_lines(c1, c2, result_image, line, color):
    cv2.rectangle(result_image, c1, c2, color, thickness=line)
    return cv2


# 検知したテキストラベルを画像に追記
def draw_texts(result_image, line, c1, cv2, color, labels, label):
    display_txt = f"{labels[label]}"
    font = max(line - 1, 1)
    t_size = cv2.getTextSize(display_txt, 0, fontScale=line / 3, thickness=font)[0]
    c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
    cv2.rectangle(result_image, c1, c2, color, -1)
    cv2.putText(
        result_image,
        display_txt,
        (c1[0], c1[1] - 2),
        0,
        line / 3,
        [255, 255, 255],
        thickness=font,
        lineType=cv2.LINE_AA,
    )
    return cv2


# 画像検知を実行する本体
def exec_detect(target_image_path):
    # ラベルの読み込み
    labels = current_app.config["LABELS"]
    # 画像の読み込み
    image = Image.open(target_image_path)
    # 画像データをテンソル型の数値データへ
    image_tensor = torchvision.transforms.functional.to_tensor(image)

    # 学習済みモデルの読み込み
    model = torch.load(Path(current_app.root_path, "detector", "model.pt"))
    # モデルの推論モードに切り替え
    model = model.eval()
    # 推論実行
    output = model([image_tensor])[0]

    tags = []
    result_image = np.array(image.copy())

    # モデルが検知した各物体の分だけ画像に追記
    for box, label, score in zip(output["boxes"], output["labels"], output["scores"]):
        if score > 0.5 and labels[label] not in tags:
            # 上で作成した関数により、枠線を描画
            color = make_color(labels)
            line = make_line(result_image)
            c1 = int(box[0]), int(box[1])
            c2 = int(box[2]), int(box[3])
            cv2 = draw_lines(c1, c2, result_image, line, color)
            cv2 = draw_texts(result_image, line, c1, cv2, color, labels, label)
            tags.append(labels[label])

    # 検知後の画像ファイル名を生成
    detected_image_file_name = str(uuid.uuid4()) + ".jpg"
    # 画像コピー先のパスを取得
    detected_image_file_path = str(
        Path(current_app.config["UPLOAD_FOLDER"], detected_image_file_name)
    )
    # 変換後の画像ファイルを保存先へコピー
    cv2.imwrite(detected_image_file_path, cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR))

    return tags, detected_image_file_name


def save_detected_image_tags(user_image, tags, detected_image_file_name):
    # 検知後画像の保存先パスをDBに保存する
    user_image.image_path = detected_image_file_name
    # 検知フラグをTに
    user_image.is_detected = True
    db.session.add(user_image)

    # user_images_tagsレコードを作成
    for tag in tags:
        user_image_tag = UserImageTag(user_image_id=user_image.id, tag_name=tag)
        db.session.add(user_image_tag)
    db.session.commit()


@dt.route("/detect/<string:image_id>", methods=["POST"])
@login_required
def detect(image_id):
    # user_imageテーブルからレコードを取得する
    user_image = db.session.query(UserImage).filter(UserImage.id == image_id).first()
    if user_image is None:
        flash("物体検知対象の画像が存在しません")
        return redirect(url_for("detector.index"))

    # 物体検知対象の画像パスを取得
    target_image_path = Path(current_app.config["UPLOAD_FOLDER"], user_image.image_path)

    tags, detected_image_file_name = exec_detect(target_image_path)

    try:
        save_detected_image_tags(user_image, tags, detected_image_file_name)
    except SQLAlchemyError as e:
        flash("物体検知処理でエラーが発生しました。")
        db.session.rollback()
        current_app.logger.error(e)
        return redirect(url_for("detector.index"))

    return redirect(url_for("detector.index"))


# 画像削除機能
@dt.route("/image/delete/<string:image_id>", methods=["POST"])
@login_required
def delete_image(image_id):
    try:
        # user_image_tagsテーブルからレコードを削除
        db.session.query(UserImageTag).filter(
            UserImageTag.user_image_id == image_id
        ).delete()
        # user_imageテーブルからレコードを削除
        db.session.query(UserImage).filter(UserImage.id == image_id).delete()

        db.session.commit()
    except SQLAlchemyError as e:
        flash("画像削除処理でエラーが発生しました。")
        current_app.logger.error(e)
        db.session.rollback()

    return redirect(url_for("detector.index"))
