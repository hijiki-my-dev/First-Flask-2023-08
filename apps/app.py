from pathlib import Path
from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from apps.config import config
from flask_login import LoginManager

# SQLAlchemyのインスタンス化
db = SQLAlchemy()

csrf = CSRFProtect()

# login managerをインスタンス化（ユーザーの認証機能）
login_manager = LoginManager()
login_manager.login_view = "auth.signup"
login_manager.login_massege = ""


# 処理を関数化することで環境の切り替えがしやすくなる
def create_app(config_key):
    app = Flask(__name__)
    # アプリのコンフィグ設定
    # config_keyにマッチする環境のコンフィグクラスを読み込む
    app.config.from_object(config[config_key])

    ## デバッグ用のロギング
    # import logging

    # app.logger.setLevel(logging.DEBUG)
    # app.logger.debug("debug")

    ## デバックツールバー
    # from flask_debugtoolbar import DebugToolbarExtension

    # app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
    # toolbar = DebugToolbarExtension(app)

    csrf.init_app(app)

    # SQLAlchemyとアプリを連携
    db.init_app(app)
    # Migrateとアプリを連携
    Migrate(app, db)

    from apps.crud import views as crud_views
    from apps.auth import views as auth_views

    # blueprintを利用する
    app.register_blueprint(crud_views.crud, url_prefix="/crud")

    app.register_blueprint(auth_views.auth, url_prefix="/auth")

    # login_managerをアプリケーションと連携する
    login_manager.init_app(app)

    # 物体検知アプリを追加
    from apps.detector import views as dt_views

    app.register_blueprint(dt_views.dt)

    # カスタムエラー画面を登録
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)

    return app


# カスタムエラー画面のエンドポイント
def page_not_found(e):
    """404 Not Found"""
    return render_template("404.html"), 404


def internal_server_error(e):
    """500 Internal Server Error"""
    return render_template("500.html"), 500
