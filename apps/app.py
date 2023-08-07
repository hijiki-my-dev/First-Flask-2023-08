from pathlib import Path
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from apps.config import config

# SQLAlchemyのインスタンス化
db = SQLAlchemy()

csrf = CSRFProtect()


# 処理を関数化することで環境の切り替えがしやすくなる
def create_app(config_key):
    app = Flask(__name__)
    # アプリのコンフィグ設定
    # config_keyにマッチする環境のコンフィグクラスを読み込む
    app.config.from_object(config[config_key])

    # app.config.from_mapping(
    #    SECRET_KEY="2AZSMss3p5QPbcY2hBsJ",
    #    SQLALCHEMY_DATABASE_URI=f"sqlite:///{Path(__file__).parent.parent / 'local.sqlite'}",
    #    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    #    SQLALCHEMY_ECHO=True,
    #    WTF_CSRF_SECRET_KEY="AuwzyszU5sugKN7KZs6f",
    # )

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

    return app
