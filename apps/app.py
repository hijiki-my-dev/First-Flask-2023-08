from flask import Flask


# 処理を関数化することで環境の切り替えがしやすくなる
def create_app():
    app = Flask(__name__)

    from apps.crud import views as crud_views

    # blueprintを利用する
    app.register_blueprint(crud_views.crud, url_prefix="/crud")

    return app
