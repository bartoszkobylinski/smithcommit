import argparse
import os
import subprocess
import openai


class CommitSmith:
    def __init__(self):
        self.git_diff = ''

    def is_git_repository(self):
        try:
            subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], capture_output=True, check=True, text=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def get_git_diff(self):
        temp_filename = 'temporary_file.txt'
        os.system(f"git diff > {temp_filename}")
        with open(temp_filename, 'r') as temp_file:
            self.git_diff = temp_file.read()
        os.remove(temp_filename)

    def get_ai_prompt(self):
        ai_prompt = f"Generate a commit message based on the following git diff:\n\n{self.git_diff}\n"
        ai_prompt += "The commit message should consist of a header, body, and footer. The header should have a " \
                     "maximum length of 50 characters, while the body and footer should have a maximum length of 72 " \
                     "characters each."
        return ai_prompt

    def generate_ai_commit_message(self, api_key):
        print("I'm here")
        openai.api_key = api_key
        ai_prompt = self.get_ai_prompt()
        response = openai.Completion.create(
            engine='text-davinci-002',
            prompt=ai_prompt,
            max_tokens=200,
            n=1,
            stop=None,
            temperature=0.8,
        )
        ai_generated_message = response.choices[0].text.strip()
        return ai_generated_message

    def run(self, api_key):
        if not self.is_git_repository():
            print("Error: The current directory is not a Git repository")
            return
        self.get_git_diff()
        commit_message = self.generate_ai_commit_message(api_key)
        print(commit_message)

def main(): # this name has to be changed in the future
    parser = argparse.ArgumentParser(description="Generate beautiful commit messages using CommitSmith")
    parser.add_argument('--max_header_length', type=int, default=50,
                        help='Maximum length of the header (default: 50)')
    parser.add_argument('--max_body_length', type=int, default=72,
                        help='Maximum length of the body (default: 72)')
    parser.add_argument('--max_footer_length', type=int, default=72,
                        help='Maximum length of the footer (default: 72)')
    parser.add_argument('-K', '--api_key', type=str, required=True,
                        help='Your OpenAI API key for GPT-4')

    args = parser.parse_args()

    commit_smith = CommitSmith()
    commit_smith.run(args.api_key)


if __name__ == "__main__":
    main()
