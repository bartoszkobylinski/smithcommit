import os
from flask import Flask, render_template, request, redirect, url_for, session
from utils import CommitForm, request_commit_from_open_ai
from prompt import system_prompt as sys_pr

openai_api_key = os.environ.get("OPENAI_APIKEY")
secret_key = os.environ.get("MY_WEBSITE_FLASK_SESSION_SECRET_KEY")

app = Flask(__name__)
app.secret_key = secret_key


@app.route('/', methods=['GET', "POST"])
def index():
    form = CommitForm(request.form)
    if request.method == "POST" and form.validate():
        diff = form.diff_message.data
        commit_message = request_commit_from_open_ai(prompt=diff, api_key=openai_api_key, sys_prompt=sys_pr)
        print(f"This is your commit: {commit_message}")
        session['commit_message'] = commit_message
        return redirect(url_for('commit'))
    return render_template("index.html", form=form)


@app.route('/commit', methods=["GET"])
def commit():
    commit_message = session.get('commit_message', 'There is no commit message. Try again')
    return render_template('commit.html', commit_message=commit_message)


if __name__ == '__main__':
    app.run(port=5002)
