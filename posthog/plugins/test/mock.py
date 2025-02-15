import base64
import json

from .plugin_archives import (
    HELLO_WORLD_PLUGIN_GITHUB_ATTACHMENT_ZIP,
    HELLO_WORLD_PLUGIN_GITHUB_ZIP,
    HELLO_WORLD_PLUGIN_GITLAB_ZIP,
    HELLO_WORLD_PLUGIN_NPM_TGZ,
)


# This method will be used by the mock to replace requests.get
def mocked_plugin_requests_get(*args, **kwargs):
    class MockJSONResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        def ok(self):
            return self.status_code < 300

    class MockTextResponse:
        def __init__(self, text, status_code):
            self.text = text
            self.status_code = status_code

        def ok(self):
            return self.status_code < 300

    class MockBase64Response:
        def __init__(self, base64_data, status_code):
            self.content = base64.b64decode(base64_data)
            self.status_code = status_code

        def ok(self):
            return self.status_code < 300

    if args[0] == "https://api.github.com/repos/PostHog/posthog/commits":
        return MockJSONResponse([{"html_url": "https://www.github.com/PostHog/posthog/commit/MOCKLATESTCOMMIT"}], 200)

    if args[0] == "https://api.github.com/repos/PostHog/helloworldplugin/commits":
        return MockJSONResponse(
            [
                {
                    "html_url": "https://www.github.com/PostHog/helloworldplugin/commit/{}".format(
                        HELLO_WORLD_PLUGIN_GITHUB_ZIP[0]
                    )
                }
            ],
            200,
        )

    if args[0] == "https://registry.npmjs.org/posthog-helloworld-plugin/latest":
        return MockJSONResponse({"pkg": "posthog-helloworld-plugin", "version": "MOCK"}, 200)

    if args[0] == "https://github.com/PostHog/helloworldplugin/archive/{}.zip".format(HELLO_WORLD_PLUGIN_GITHUB_ZIP[0]):
        return MockBase64Response(HELLO_WORLD_PLUGIN_GITHUB_ZIP[1], 200)

    if args[0] == "https://github.com/PostHog/helloworldplugin/archive/{}.zip".format(
        HELLO_WORLD_PLUGIN_GITHUB_ATTACHMENT_ZIP[0]
    ):
        return MockBase64Response(HELLO_WORLD_PLUGIN_GITHUB_ATTACHMENT_ZIP[1], 200)

    if args[0] == "https://gitlab.com/mariusandra/helloworldplugin/-/archive/{}/helloworldplugin-{}.zip".format(
        HELLO_WORLD_PLUGIN_GITLAB_ZIP[0], HELLO_WORLD_PLUGIN_GITLAB_ZIP[0]
    ) or args[
        0
    ] == "https://gitlab.com/api/v4/projects/mariusandra%2Fhelloworldplugin/repository/archive.zip?sha={}&private_token={}".format(
        HELLO_WORLD_PLUGIN_GITLAB_ZIP[0], "PRIVATE_TOKEN"
    ):
        return MockBase64Response(HELLO_WORLD_PLUGIN_GITLAB_ZIP[1], 200)

    if args[0] == "https://registry.npmjs.org/posthog-helloworld-plugin/-/posthog-helloworld-plugin-0.0.0.tgz":
        return MockBase64Response(HELLO_WORLD_PLUGIN_NPM_TGZ[1], 200)

    if args[0] == "https://raw.githubusercontent.com/PostHog/plugin-repository/main/repository.json":
        return MockTextResponse(
            json.dumps(
                [
                    {
                        "name": "posthog-currency-normalization-plugin",
                        "url": "https://github.com/posthog/posthog-currency-normalization-plugin",
                        "description": "Normalise monerary values into a base currency",
                        "verified": False,
                        "maintainer": "official",
                    },
                    {
                        "name": "helloworldplugin",
                        "url": "https://github.com/posthog/helloworldplugin",
                        "description": "Greet the World and Foo a Bar",
                        "verified": True,
                        "maintainer": "community",
                    },
                ]
            ),
            200,
        )

    return MockJSONResponse(None, 404)
