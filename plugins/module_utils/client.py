#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2025, mikemorency
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

try:
    import requests
    from requests.auth import HTTPBasicAuth
except ImportError:
    # handled in module base
    pass


class RequestError(Exception):
    """
    Error wrapper to make testing easier
    """
    def __init__(self, exception):
        self.exception = exception


class Client:
    def __init__(self, api_key):
        self.api_key = api_key
        self._url_base = "https://api.deadmanssnitch.com/v1"
        self._auth = HTTPBasicAuth(self.api_key, "")

    def _create_headers(self, include_content_type: bool = False):
        headers = dict()
        if include_content_type:
            headers["Content-Type"] = "application/json"
        return headers

    def _format_url(self, uri: str, params: dict = None):
        url = f"{self._url_base}/{uri}"
        if params:
            url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    def _make_request(self, method: str, uri: str, data: dict = None, params: dict = None, include_content_type: bool = False):
        url = self._format_url(uri=uri, params=params)
        headers = self._create_headers(include_content_type=include_content_type)

        request_kwargs = {
            "url": url,
            "method": method,
            "headers": headers,
            "auth": self._auth,
        }

        if data:
            if isinstance(data, dict):
                _d = data.copy()
                for k, v in _d.items():
                    if v is None:
                        del data[k]
            request_kwargs["json"] = data

        response = requests.request(**request_kwargs)
        try:
            response.raise_for_status()
        except Exception as e:
            raise RequestError(e)
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            return

    def list_snitches(self, tags: list = None):
        """List all snitches"""
        params = {}
        if tags:
            params["tags"] = ",".join(tags)
        return self._make_request("GET", "snitches", params=params)

    def get_snitch(self, snitch_id: str):
        """Get a snitch by ID"""
        return self._make_request("GET", f"snitches/{snitch_id}")

    def create_snitch(self, name: str, interval: str, alert_type: str = None,
                      alert_email: list = None, notes: str = None, tags: list = None):
        """Create a snitch"""
        data = {
            "name": name,
            "interval": interval,
            "alert_type": alert_type,
            "alert_email": alert_email,
            "notes": notes,
            "tags": tags,
        }
        return self._make_request("POST", "snitches", data=data, include_content_type=True)

    def update_snitch(self, snitch_id: str, name: str = None, interval: str = None,
                      alert_type: str = None, alert_email: list = None, notes: str = None, tags: list = None):
        """Update a snitch"""
        data = {}
        for attr in ["name", "interval", "alert_type", "alert_email", "notes", "tags"]:
            if locals()[attr]:
                data[attr] = locals()[attr]
        return self._make_request("PATCH", f"snitches/{snitch_id}", data=data, include_content_type=True)

    def remove_snitch_tag(self, snitch_id: str, tag: str):
        """Remove tag from a snitch"""
        return self._make_request("DELETE", f"snitches/{snitch_id}/tags/{tag}", include_content_type=True)

    def append_snitch_tags(self, snitch_id: str, tags: list):
        """Append tags to a snitch"""
        data = tags
        return self._make_request("POST", f"snitches/{snitch_id}/tags", data=data, include_content_type=True)

    def replace_snitch_tags(self, snitch_id: str, tags: list):
        """Replace tags on a snitch"""
        data = {"tags": tags}
        return self._make_request("PATCH", f"snitches/{snitch_id}", data=data, include_content_type=True)

    def delete_snitch(self, snitch_id: str):
        """Delete a snitch"""
        return self._make_request("DELETE", f"snitches/{snitch_id}")

    def pause_snitch(self, snitch_id: str):
        """Pause a snitch"""
        return self._make_request("POST", f"snitches/{snitch_id}/pause")

    def unpause_snitch(self, snitch_id: str):
        """Unpause a snitch"""
        return self._make_request("POST", f"snitches/{snitch_id}/unpause")
