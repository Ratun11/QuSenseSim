from flask import Flask, render_template
from backend.routes.api import api_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(api_bp)

    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/circuit-builder")
    def circuit_builder():
        return render_template("circuit_builder.html")

    @app.route("/analysis")
    def analysis():
        return render_template("analysis.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
