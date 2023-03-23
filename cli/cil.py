import argparse
import os

def request_commit_message_from_ai():
    pass

def get_git_diff():
    temporary_file = "temp_file.txt"
    os.system(f"git diff")


def main(): # this name has to be changed in the future
    parser = argparse.ArgumentParser(description="Generate beautiful commit messages using CommitSmith")
    parser.add_argument("-H", '--header', type=str, required=True, max_length=50,
                        help="A brief summary of the changes made")
    parser.add_argument("-B", '--body', type=str, default='',
                        help="A more detailed description of teh changes made (optional)")
    parser.add_argument("-F", "--footer", type=str, default="", max_length=72,
                        help="Information about related issues, links to documentation, or other metadata (optional)")


    args = parser.parse_args()