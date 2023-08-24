import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, session, url_for

from database import db
from prompt import system_prompt as sys_pr
from models import RequestCounter
from utils import CommitForm, request_commit_from_open_ai
from login_manager import init_login_manager

openai_api_key = os.environ.get("OPENAI_APIKEY")
secret_key = os.environ.get("MY_WEBSITE_FLASK_SESSION_SECRET_KEY")


def create_app():
    app = Flask(__name__)
    app.secret_key = secret_key
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///request.db"

    db.init_app(app)
    init_login_manager(app)

    @app.route("/", methods=["GET", "POST"])
    def index():
        form = CommitForm(request.form)
        today = datetime.date(datetime.now())
        counter = RequestCounter.query.filter_by(date=today).first()
        if not counter:
            counter = RequestCounter(date=today)
            db.session.add(counter)
            db.session.commit()

        if request.method == "POST" and form.validate():
            if counter.count > 15:
                return render_template("index.html", form=form)
            diff = form.diff_message.data
            commit_message = request_commit_from_open_ai(
                prompt=diff, api_key=openai_api_key, sys_prompt=sys_pr
            )
            counter.count += 1
            db.session.commit()
            session["commit_message"] = commit_message
            print(f"counter: {counter.count}")
            return redirect(url_for("commit"))
        return render_template("index.html", form=form)

    @app.route("/commit", methods=["GET"])
    def commit():
        commit_message = session.get(
            "commit_message", "There is no commit message. Try again"
        )
        return render_template("commit.html", commit_message=commit_message)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=5002)
