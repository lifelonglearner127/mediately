import json

import lokalise
from django.conf import settings
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, ListModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from .exceptions import GitHubApiError
from .githubclient import GithubAPI
from .models import Tool
from .serializers import ToolSerializer
# from .tasks import update_task
from .utils import get_all_translating_keys, populate_with_translating_value

client = lokalise.Client(settings.LOKALISE_API_TOKEN)


class ToolViewSet(ListModelMixin, CreateModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = Tool.objects.all()
        return Response(
            {
                'code': 0,
                'data': self.serializer_class(queryset, many=True).data
            }
        )

    def create(self, request, *args, **kwargs):
        serializer = ToolSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tool_name = serializer.validated_data['name']
        tool_language = serializer.validated_data['language']
        tool = Tool(
            name=tool_name,
            language=tool_language,
        )

        try:
            # check if the github repository contains the langauge spec file
            is_found, master_file_name, repository_file_names = \
                GithubAPI.repository_has_sepc_files(tool_name, tool_language)
            if not master_file_name:
                return Response(
                    {
                        'code': 1,
                        'msg': f'Github does not include the any seed files related to your requested spec file.'
                               f' It includes {", ".join(repository_file_names)} for now'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            payload = GithubAPI.repository_read_spec(master_file_name)
            if is_found:
                tool.json_spec = payload
            tool.save()

            # update key to lokalize
            keys = [
                {
                    'key_name': json.dumps({
                        "ios": key,
                        "android": key,
                        "web": key,
                        "other": key,
                    }),
                    'platforms': ["ios", "android", "web", "other"],
                    'tags': [tool_name]     # created tags for filtering
                }
                for key in get_all_translating_keys(payload, prefix=tool_name)
            ]
            client.create_keys(settings.LOKALISE_PROJECT_ID, keys)
            return Response(serializer.data)

        except GitHubApiError:
            return Response(
                {
                    'code': 1,
                    'msg': 'Error occured while calling Github API'
                }
            )
        except Exception as e:
            return Response(
                {
                    'code': 1,
                    'msg': f'Error {e}'
                }
            )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ToolSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        tool_name = serializer.validated_data['name']
        tool_language = serializer.validated_data['language']
        if tool_name == instance.name and tool_language == instance.language:
            return Response(
                {
                    'code': 0,
                    'msg': 'No updates'
                }
            )

        # TODO: run request in background service
        # I implemented it asynchronously in celery task
        # update_task.apply_async(
        #     args=[{
        #         'tool_id': instance.id,
        #         'tool_name': tool_name,
        #         'tool_language': tool_language
        #     }]
        # )

        try:
            _, master_file_name, _ = GithubAPI.repository_has_sepc_files(tool_name, tool_language)
            if not master_file_name:
                # Github does not include the {tool_language} tool master file
                return Response(
                    {
                        'code': 0,
                        'msg': f"Github does not include the any seed files related to "
                               f"your requested {tool_name} spec file."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

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
                return Response(
                    {
                        'code': 0,
                        'msg': f"Your Lokalise Project does not contains the {tool_language} translation"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

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
                    key_name = list(json.loads(key_name).values())[0]
                    localise_dict[key_name] = key.translations[0]['translation']

                if keys.is_last_page():
                    break
                page += 1

            # Replace values in JSON with translations
            populate_with_translating_value(payload, localise_dict, tool_name)
            with open(f'{instance.id}.{tool_name}.{tool_language}.json', 'w') as f:
                json.dump(payload, f, indent=4)

            # create pull request
            GithubAPI.create_pull_request(instance.id, tool_name, tool_language, payload)

            return Response(
                {
                    'code': 0,
                    'msg': 'Your request is accepted, Pending'
                }
            )

        except GitHubApiError:
            return Response(
                {
                    'code': 0,
                    'msg': "Github api error"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                {
                    'code': 0,
                    'msg': f"{e}"
                }
            )


class GitHookAPIView(APIView):
    """
    Github webhook url endpoint; Subscribe to pull requests event only

    Web hook is configured on tool spec repository.
    Any events related to pull requests will send a HTTP payload to
    this endpoint.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        payload = request.data.get('payload')
        if not payload:
            return Response(
                {
                    'code': 1,
                    'msg': 'Webhook does not contain the payload'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        payload = json.loads(payload)
        action = payload.get('action')
        pull_request_payload = payload.get('pull_request', {})
        merged = pull_request_payload.get('merged')

        # handle only if the pull request is merged
        if action == 'closed' and merged:
            # check which spec file is merged.
            # We can know by looking the branch name.
            # I follow the such name conventions.
            # branch_name: updates/{name}/{language}
            changes = pull_request_payload.get('head', {}).get('ref')
            tool_id = changes.split('/')[1]
            tool_name = changes.split('/')[2]
            tool_language = changes.split('/')[3]
            try:
                tool = Tool.objects.get(pk=tool_id)
                with open(f'{tool_id}.{tool_name}.{tool_language}.json', 'r') as f:
                    tool.json_spec = json.load(f)
                tool.name = tool_name
                tool.language = tool_language
                tool.save()
            except Tool.DoesNotExist:
                pass

            return Response(
                {
                    'code': 0,
                    'msg': 'Succeeded'
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                'code': 1,
                'msg': 'Not Succeeded or other pull request events'
            },
            status=status.HTTP_200_OK
        )
