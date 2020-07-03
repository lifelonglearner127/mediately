import json

import requests
import six
from django.conf import settings
from github import Github

from .constants import GITHUB_API_DOMAN, GITHUB_REPOSITORY, GITHUB_USER
from .exceptions import GitHubApiError

g = Github(settings.GITHUB_TOKEN)
repo = g.get_repo(f"{GITHUB_USER}/{GITHUB_REPOSITORY}")


class GitHubClient:
    """
    Not Used
    This is my first version of github client. But later I chose PyGithub
    """
    @staticmethod
    def repository_contents(path):
        """
        Github Content API
        """
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        try:
            req = requests.get(
                f'https://{GITHUB_API_DOMAN}/repos/{GITHUB_USER}/'
                f'{GITHUB_REPOSITORY}/contents/{path.lstrip("/")}',
                headers=headers,
            )
        except requests.exceptions.RequestException as e:
            raise GitHubApiError(six.text_type(e), status=getattr(e, "status_code", 0))
        if req.status_code < 200 or req.status_code >= 300:
            raise GitHubApiError(req.content, status=req.status_code)
        return json.loads(req.content)


class GithubAPI:
    @staticmethod
    def repository_has_sepc_files(tool_name, tool_language):
        """
        check if github repository contains such master file and return file name
        """
        master_file_candidate_names = [
            f'{tool_name}.{tool_language}.json',
            f'{tool_name}.{tool_language}.master.json'
        ]
        master_file_name = None

        # get repository file names
        # payload = GitHubClient.repository_contents('/')
        # repository_file_names = [item.get('name') for item in payload]

        try:
            payload = repo.get_contents("/")
            repository_file_names = [item.name for item in payload]

            for repository_file_name in repository_file_names:
                if repository_file_name in master_file_candidate_names:
                    return True, repository_file_name

                if repository_file_name.split('.')[0] == tool_name and \
                   repository_file_name.endswith('.master.json'):
                    master_file_name = repository_file_name

            return False, master_file_name
        except Exception:
            raise GitHubApiError

    @staticmethod
    def repository_read_spec(file_name):
        """
        Read json master spec file from the github repository
        """
        # payload = GitHubClient.repository_contents(file_name)
        # download_url = payload.get('download_url', None)
        # r = requests.get(download_url)
        # return json.loads(r.content)
        try:
            content = repo.get_contents(file_name)
        except Exception:
            raise GitHubApiError
        else:
            return json.loads(content.decoded_content)

    @staticmethod
    def create_pull_request(tool_name, tool_language, json_payload):
        # check if the file exist in the repository.
        # if not exists, create file, if exists, update file
        file_name = f'{tool_name}.{tool_language}.json'
        payload = repo.get_contents("/")
        is_exists = file_name in [item.name for item in payload]

        # create branch
        branch_name = f"updates/{tool_name}/{tool_language}"
        master_ref = repo.get_git_ref('heads/master')
        repo.create_git_ref(f'refs/heads/{branch_name}', master_ref.object.sha)

        # commit the changes
        if is_exists:
            repo.update_file(
                file_name,
                f"updated {file_name}",
                json.dumps(json_payload, indent=4),
                branch=branch_name,
                sha=repo.get_contents(file_name).sha
            )
        else:
            repo.create_file(
                file_name,
                f"added {file_name}",
                json.dumps(json_payload, indent=4),
                branch=branch_name,
            )

        # pull requests
        repo.create_pull(
            title=f"{tool_name}.{tool_language}",
            body=f"{tool_name}.{tool_language}",
            head=branch_name,
            base="master"
        )
