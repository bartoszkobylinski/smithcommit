import argparse
import os
import subprocess


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



def main(): # this name has to be changed in the future
    parser = argparse.ArgumentParser(description="Generate beautiful commit messages using CommitSmith")
    parser.add_argument("-H", '--header', type=str, required=True, max_length=50,
                        help="A brief summary of the changes made")
    parser.add_argument("-B", '--body', type=str, default='',
                        help="A more detailed description of teh changes made (optional)")
    parser.add_argument("-F", "--footer", type=str, default="", max_length=72,
                        help="Information about related issues, links to documentation, or other metadata (optional)")


    args = parser.parse_args()