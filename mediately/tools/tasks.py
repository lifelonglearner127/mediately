import json

import lokalise
from django.conf import settings

from config import celery_app

from .exceptions import GitHubApiError
from .githubclient import GithubAPI
from .utils import populate_with_translating_value

client = lokalise.Client(settings.LOKALISE_API_TOKEN)


@celery_app.task()
def update_task(context):
    tool_name = context.get('tool_name')
    tool_language = context.get('tool_language')
    if not tool_name or not tool_language:
        return

    try:
        is_found, master_file_name = GithubAPI.repository_has_sepc_files(tool_name, tool_language)
        if not master_file_name:
            # Github does not include the {tool_language} tool master file
            return

        payload = GithubAPI.repository_read_spec(master_file_name)

        # fetch language id from lokalise
        page = 1
        language_id = None

        # handle pagination of fetching system-languages
        while True:
            languages = client.system_languages({"page": page})
            for language in languages.items:
                if language.lang_iso == tool_language:
                    language_id = language.lang_id
                    break

            if languages.is_last_page():
                break
            page += 1

        if not language_id:
            # Your supplied language code {tool_language} does not exists
            return

        # handle paginations of fetching keys
        localise_dict = {}
        page = 1
        while True:
            keys = client.keys(
                settings.LOKALISE_PROJECT_ID,
                {
                    'page': page,
                    'limit': 500,
                    'disable_references': '1',
                    'include_translations': '1',
                    'filter_translation_lang_ids': [str(language_id)],
                    'filter_tags': [tool_name]
                }
            )
            for key in keys.items:
                key_name = next(iter(key.key_name.values()))
                localise_dict[key_name] = key.translations[0]['translation']

            if keys.is_last_page():
                break
            page += 1

        # Replace values in JSON with translations
        populate_with_translating_value(payload, localise_dict, tool_name)
        with open(f'{tool_name}.{tool_language}.json', 'w') as f:
            json.dump(payload, f, indent=4)

        # create pull request
        GithubAPI.create_pull_request(tool_name, tool_language, payload)

    except GitHubApiError:
        pass
    except Exception as e:
        # TODO: logger
        print(e)
        pass
