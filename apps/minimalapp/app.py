from flask import Flask, render_template, url_for, current_app, g, request, redirect

app = Flask(__name__)


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
        # ここにメール送信処理

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
