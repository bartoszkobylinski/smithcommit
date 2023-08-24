import openai
from wtforms import Form, TextAreaField
import ast


class CommitForm(Form):
    diff_message = TextAreaField(render_kw={"placeholder": "set your diff message here"})


def request_commit_from_open_ai(prompt, api_key, sys_prompt):
    openai.api_key = api_key
    completion = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1280,
        n=1,
        temperature=0.0,
    )
    commit_message = completion.choices[0].message['content']
    print(commit_message)
    commit_message = ast.literal_eval(commit_message)
    # print(commit_message)
    return commit_message
