from flask import Blueprint, render_template

# Blueprintでcrudアプリを生成する
crud = Blueprint("crud", __name__, template_folder="templates", static_folder="static")


@crud.route("/")
def index():
    return render_template("crud/index.html")
