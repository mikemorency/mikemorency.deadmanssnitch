# Copyright: (c) 2025, mikemorency
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from ansible.module_utils.basic import env_fallback
from ansible.module_utils.basic import missing_required_lib
from ansible_collections.mikemorency.deadmanssnitch.plugins.module_utils.client import (
    Client,
    RequestError
)
import traceback

try:
    import requests  # pylint: disable=unused-import
    HAS_REQUESTS = True
    REQUESTS_IMPORT_ERROR = None
except ImportError:
    HAS_REQUESTS = False
    REQUESTS_IMPORT_ERROR = traceback.format_exc()


class ModuleBase:
    def __init__(self, module):
        self.module = module
        self.params = module.params
        self.client = Client(module.params["api_key"])
        if not HAS_REQUESTS:
            self.handle_missing_lib("requests", REQUESTS_IMPORT_ERROR)

    @staticmethod
    def base_argument_spec():
        return {
            "api_key": dict(
                type="str", required=True, fallback=(env_fallback, ["DMS_API_KEY"]), no_log=True
            ),
        }

    def handle_missing_lib(self, library, exception=None):
        self.module.fail_json(
            msg=missing_required_lib(library),
            exception=exception
        )

    def handle_exception(self, error):
        if isinstance(error, RequestError):
            self.handle_http_error(error.exception)
        else:
            self.module.fail_json(
                msg=f"Error: {error}"
            )

    def handle_http_error(self, error):
        self.module.fail_json(
            msg=f"HTTP error: {error.response.status_code} {error.response.reason}",
            request_url=error.request.url,
            request_method=error.request.method,
            request_headers=dict(error.request.headers),
            request_body=error.request.body,
            code=error.response.status_code,
            response=error.response.json(),
        )

    def fail_unable_to_find_snitch(self):
        output_data = {"searched": dict()}

        param_name = 'id'
        param_value = self.params.get(param_name)
        if not param_value:
            param_name = 'name'
            param_value = self.params.get(param_name)

        self.module.fail_json(
            msg="Unable to find snitch with ID %s or name %s",
            searched=dict(
                param=param_name,
                value=param_value
            )
        )
