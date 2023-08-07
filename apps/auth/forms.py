from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class SignUpForm(FlaskForm):
    username = StringField(
        "ユーザー名",
        validators=[
            DataRequired(message="ユーザー名は必須です。"),
            Length(1, 30, message="30文字以内で入力してください。"),
        ],
    )
    # email
    email = StringField(
        "メールアドレス",
        validators=[
            DataRequired(message="メールアドレスは必須です。"),
            Email(message="メールアドレスの形式で入力してください。"),
        ],
    )
    # password
    password = PasswordField("パスワード", validators=[DataRequired(message="パスワードは必須です。")])
    # ユーザーフォームsubmitの文言を設定する
    submit = SubmitField("新規登録")


# ログイン機能用のクラス
class LoginForm(FlaskForm):
    email = StringField(
        "メールアドレス",
        validators=[DataRequired("メールアドレスは必須です。"), Email("メールアドレスの形式で入力してください。")],
    )
    password = PasswordField("パスワード", validators=[DataRequired("パスワードは必須です。")])
    submit = SubmitField("ログイン")
