import os
from flask import Flask, render_template, request
from utils import CommitForm, request_commit_from_open_ai
from prompt import prompt as pr

app = Flask(__name__)

openai_api_key = os.environ.get("OPENAI_APIKEY")


@app.route('/', methods=['GET', "POST"])
def index():
    form = CommitForm(request.form)
    commit_message = 'First add your result of diff'
    if request.method == "POST" and form.validate():
        diff = form.diff_message.data
        prompt = pr + diff
        commit_message = request_commit_from_open_ai(prompt=prompt, api_key=openai_api_key)
        print(f"This is your commit: {commit_message}")
        return render_template('index.html', form=form, commit_message=commit_message)
    return render_template("index.html", form=form, commit_message=commit_message)


if __name__ == '__main__':
    app.run()
