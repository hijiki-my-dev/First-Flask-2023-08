from flask_wtf import FileAllowed, FileField, FileRequired
from flask_wtf import FlaskForm
from wtforms.fields.simple import SubmitField


# 画像アップロード画面のクラス
class UploadImageForm(FlaskForm):
    image = FileField(
        validators=[
            FileRequired("画像ファイルを指定してください。"),
            FileAllowed(["png", "jpg", "jpeg"], "サポートされていない画像形式です。"),
        ]
    )
    submit = SubmitField("アップロード")
