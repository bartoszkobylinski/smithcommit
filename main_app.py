import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, session, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash

from database import db
from prompt import system_prompt as sys_pr
from models import RequestCounter, User
from app_forms import CommitForm, LoginForm, RegistrationForm
from utils import request_commit_from_open_ai
from login_manager import init_login_manager

openai_api_key = os.environ.get("OPENAI_APIKEY")
secret_key = os.environ.get("MY_WEBSITE_FLASK_SESSION_SECRET_KEY")
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    csrf.init_app(app)
    app.secret_key = secret_key
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///request.db"

    db.init_app(app)
    migrate = Migrate(app, db)
    init_login_manager(app)

    @app.route("/", methods=["GET", "POST"])
    def index():
        session.pop('commit_message', None)
        commit_form = CommitForm(request.form)
        today = datetime.date(datetime.now())

        counter = RequestCounter.query.filter_by(date=today).first()
        if not counter:
            counter = RequestCounter(date=today)
            db.session.add(counter)
            db.session.commit()

        if request.method == "POST" and commit_form.validate():
            using_user_api = current_user.is_authenticated and hasattr(current_user, 'api_key') and current_user.api_key
            used_api_key = current_user.api_key if (current_user.is_authenticated and hasattr(current_user, 'api_key')) else openai_api_key

            if not using_user_api and counter.count >= 15:
                flash("The global request limit has been reached for today. Please try again tomorrow.", 'danger')
                return render_template('index.html', form=commit_form, counter=counter)

            diff = commit_form.diff_message.data
            commit_message = request_commit_from_open_ai(
                prompt=diff, api_key=used_api_key, sys_prompt=sys_pr
            )
            if not using_user_api:
                counter.count += 1
                db.session.commit()

            session["commit_message"] = commit_message
            return redirect(url_for("commit"))

        return render_template("index.html", form=commit_form, counter=counter)

    @app.route("/commit", methods=["GET"])
    def commit():
        commit_message = session.get(
            "commit_message", "There is no commit message. Try again"
        )
        return render_template("commit.html", commit_message=commit_message, login_form=LoginForm())

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        login_form = LoginForm()
        if login_form.validate_on_submit():
            user = User.query.filter_by(email=login_form.email.data).first()
            if user and user.check_password(login_form.password.data):
                login_user(user, remember=login_form.remember.data)
                flash("Logged in successfully.", 'success')
                return redirect(url_for('index'))
            flash("Invalid email or password. Please try again.", 'danger')
        return render_template('login.html', login_form=login_form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash("Logged out successfully.", 'success')
        session.clear()
        return redirect(url_for('index'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        register_form = RegistrationForm()
        if register_form.validate_on_submit():
            existing_user = User.query.filter_by(email=register_form.email.data).first()
            if existing_user:
                flash("This email is already registered. Try logging in.", 'danger')
                return redirect(url_for('login'))
            user = User(email=register_form.email.data)
            user.set_password(register_form.password.data)

            db.session.add(user)
            db.session.commit()
            flash("Registered successfully. You can now login.", 'success')
            return redirect(url_for('login'))

        for field, errors in register_form.errors.items():
            for error in errors:
                flash(error, 'danger')

        return render_template('register.html', register_form=register_form)

    @app.route('/profile', methods=['GET'])
    @login_required
    def profile():
        return render_template('profile.html', user=current_user)
    
    @app.route("/why-pretty-commit", methods=["GET"])
    def why_pretty_commit():
        return render_template("why-pretty-commit.html", user=current_user)

    @app.route('/update_api_key', methods=['POST'])
    @login_required
    def update_api_key():
        new_api_key = request.form.get('new_api_key')
        hashed_api_key = generate_password_hash(new_api_key, method='sha256')
        current_user.api_key = hashed_api_key
        db.session.commit()
        flash("API key updated successfully!", 'success')
        return redirect(url_for('profile'))

    @app.route('/delete_api_key', methods=['POST'])
    @login_required
    def delete_api_key():
        current_user.api_key = None
        db.session.commit()
        flash("API key deleted successfully!", 'success')
        return redirect(url_for('profile'))

    @app.route('/change_password', methods=['POST'])
    @login_required
    def change_password():
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

        if not current_user.check_password(current_password):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('profile'))
        current_user.set_password(new_password)
        db.session.commit()
        flash("Password updated successfully!", 'success')
        return redirect(url_for('profile'))

    @app.template_filter('mask_password')
    def mask_password_filter(password):
        return '*' * 10

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=5002)
