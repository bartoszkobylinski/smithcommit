from flask import Flask, render_template, request
from utils import CommitForm

app = Flask(__name__)


@app.route('/', methods=['GET', "POST"])
def index():  # put application's code here
    form = CommitForm(request.form)
    if request.method == "POST" and form.validate():
        diff = form.diff_message.data
        print("Hey, your form is great")
        print(diff)
        #  print(form.data[:30])
        return render_template('index.html', form=form)
    return render_template("index.html", form=form)


if __name__ == '__main__':
    app.run()
