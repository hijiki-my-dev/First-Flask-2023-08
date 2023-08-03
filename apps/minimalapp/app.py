from email_validator import validate_email, EmailNotValidError
from flask import (
    Flask,
    render_template,
    url_for,
    current_app,
    g,
    request,
    redirect,
    flash,
)
import logging
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.config["SECRET_KEY"] = "2AZSMss3p5QPbcY2hBsJ"

# debug tool barを表示するには以下の1行を追加する必要がある。
app.debug = True
# ログレベルを設定
app.logger.setLevel(logging.DEBUG)

app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
toolbar = DebugToolbarExtension(app)


# route1つが1つのWebページに対応するイメージ？
@app.route("/")
def index():
    return "Hello, Flaskbook!"


@app.route("/hello/<name>", methods=["GET", "POST"], endpoint="hello-endpoint")
def hello(name):
    return f"Hello, {name}"


@app.route("/name/<name>")
def show_name(name):
    # 変数をテンプレートエンジンに渡す
    return render_template("index.html", name=name)


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/contact/complete", methods=["GET", "POST"])
def contact_complete():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        description = request.form["description"]

        # 入力チェック
        is_valid = True

        if not username:
            flash("ユーザー名は必須です。")
            is_valid = False

        if not mail:
            flash("メールアドレスは必須です。")
            is_valid = False

        try:
            validate_email(email)
        except EmailNotValidError:
            flash("メールアドレスの形式で入力してください。")
            is_valid = False

        if not description:
            flash("問い合わせ内容は必須です。")
            is_valid = False

        if not is_valid:
            return redirect(url_for("contact"))

        flash("問い合わせ内容はメールにて送信しました。問い合わせありがとうございました。")

        return redirect(url_for("contact_complete"))
    return render_template("contact_complete.html")


with app.test_request_context("/users?updated=true"):
    print(request.args.get("updated"))
    # print(url_for("index"))
    # print(url_for("hello-endpoint", name="world"))
    # print(url_for("show_name", name="mito", page="1"))

ctx = app.app_context()
ctx.push()

print(current_app.name)

g.connection = "connection"
print(g.connection)
