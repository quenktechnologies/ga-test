# merge_pr.py

import sys
import os
import argparse
import requests

def get_pull_request_status(owner, repo, pr_number):
    response = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}",
        headers={"Authorization": f"Bearer {GITHUB_TOKEN}"}
    )
    return response.json()

def get_user_permissions(username, owner, repo):
    response = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/collaborators/{username}/permission",
        headers={"Authorization": f"Bearer {GITHUB_TOKEN}"}
    )
    return response.json().get('permission')

def main():
    parser = argparse.ArgumentParser(description='Merge pull requests if conditions are met')
    parser.add_argument('--owner', required=True, help='GitHub repository owner')
    parser.add_argument('--repo', required=True, help='GitHub repository name')
    parser.add_argument('--pr-number', required=True, help='Pull request number')
    args = parser.parse_args()

    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
    if GITHUB_TOKEN is None:
        print("GITHUB_TOKEN environment variable is not set.")
        sys.exit(1)

    pr_status = get_pull_request_status(args.owner, args.repo, args.pr_number)
    pr_state = pr_status.get('state')
    pr_merged = pr_status.get('merged')
    pr_creator_login = pr_status.get('user', {}).get('login')

    if pr_state == 'open' and not pr_merged:
        user_permission = get_user_permissions(pr_creator_login, args.owner, args.repo)
        if user_permission == 'write':
            # Perform your custom validation checks here
            # If checks pass, attempt to merge the pull request
            response = requests.put(
                f"https://api.github.com/repos/{args.owner}/{args.repo}/pulls/{args.pr_number}/merge",
                headers={"Authorization": f"Bearer {GITHUB_TOKEN}"}
            )
            if response.status_code == 200 and response.json().get('merged'):
                print("Pull request merged successfully.")
            else:
                print("Pull request not merged.")
        else:
            print("User doesn't have write permissions.")
    else:
        print("Pull request not eligible for merging.")

if __name__ == "__main__":
    main()
