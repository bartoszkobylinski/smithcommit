import openai
from wtforms import Form, TextAreaField


class CommitForm(Form):
    diff_message = TextAreaField()


def request_commit_from_open_ai(prompt, api_key):
    response = openai.Completion.create(
        model='text-davinci-003',
        api_key=api_key,
        prompt=prompt,
        max_tokens=1280,
        n=1,
        stop='.',
        temperature=0.5,
    )
    commit_message = response.choices[0].text.strip()
    return commit_message
