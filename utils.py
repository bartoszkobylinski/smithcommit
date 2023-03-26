from wtforms import Form, TextAreaField


class CommitForm(Form):
    diff_message = TextAreaField()
