# Copyright (c) 2019 Alexander Todorov <atodorov@MrSenko.com>

# Licensed under the GPL 3.0: https://www.gnu.org/licenses/gpl-3.0.txt
# pylint: disable=too-many-ancestors

import json
from http import HTTPStatus

from django import test
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponseForbidden

from tcms.utils import github


class WebHookTestCase(test.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse('github_app_webhook')

    def test_hook_ping(self):
        payload = """
{
  "zen": "Mind your words, they are important.",
  "sender": {
    "login": "atodorov",
    "id": 1002300
  }
}
""".strip()
        signature = github.calculate_signature(
            settings.KIWI_GITHUB_APP_SECRET,
            json.dumps(json.loads(payload)).encode())
        response = self.client.post(self.url,
                                    json.loads(payload),
                                    content_type='application/json',
                                    HTTP_X_HUB_SIGNATURE=signature,
                                    HTTP_X_GITHUB_EVENT='ping')

        # initial ping responds with a pong
        self.assertContains(response, 'pong')

    def test_without_signature_header(self):
        payload = json.loads("""
{
  "zen": "Mind your words, they are important.",
  "sender": {
    "login": "atodorov",
    "id": 1002300
  }
}
""".strip())

        response = self.client.post(
            self.url, payload, content_type='application/json')

        # missing signature should cause failure
        self.assertIsInstance(response, HttpResponseForbidden)
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)
