from logging import basicConfig, getLogger

import markdown
from flask import Flask, render_template

from api.config import bp as config_bp
from api.debug import bp as debug_bp
from api.results import bp as results_bp
from api.tests import bp as tests_bp
from config.settings import settings
from utils.app import create_exception_handlers, set_config

logger = getLogger(__name__)
basicConfig(
    level=settings.log_level,
    format=settings.logger_format[0],
    datefmt=settings.logger_format[1],
)


def create_app() -> Flask:
    app = Flask(__name__)
    app.logger.setLevel(settings.log_level)

    app = set_config(app)
    app = create_exception_handlers(app)

    app.register_blueprint(config_bp)
    app.register_blueprint(tests_bp)
    app.register_blueprint(debug_bp)
    app.register_blueprint(results_bp)

    logger.info(
        "Run with debug=%s, allow_parallel=%s on host=%s",
        settings.debug,
        settings.allow_parallel,
        f"{settings.host}:{settings.port}",
    )

    @app.route("/")
    def index():
        return render_template(
            "index.html",
            allow_parallel="Yes" if settings.allow_parallel else "No",
        )

    @app.route("/docs")
    def docs():
        with open("DOCS.md", "r", encoding="utf-8") as f:
            content = f.read()

        html_content = markdown.markdown(
            content, extensions=["fenced_code", "tables", "codehilite", "toc", "smarty", "nl2br"]
        )
        return render_template("docs.html", content=html_content)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
