#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2025, mikemorency
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: snitch_info
short_description: Lookup information about one or more snitches
description: Looks up information about one or more snitches

extends_documentation_fragment:
    - mikemorency.deadmanssnitch.module_base

options:
    name:
        description:
            - The exact name of the snitch to lookup
        required: false
        type: str

    id:
        description:
            - The exact ID of the snitch to lookup
        required: false
        type: str

    tags:
        description:
            - A list of tags by which to filter the snitches
        required: false
        type: list
        elements: str
"""

EXAMPLES = r"""
- name: Ensure tags are present
  mikemorency.deadmanssnitch.tags:
    id: 12345
    state: present
    tags:
      - one
      - two
      - three

- name: Ensure tags are absent
  mikemorency.deadmanssnitch.tags:
    id: 12345
    state: absent
    tags:
      - one
      - two
      - three

- name: Replace all tags on snitch with list
  mikemorency.deadmanssnitch.tags:
    id: 12345
    state: absolute
    tags:
      - one
      - two
      - three

- name: Remove all tags
  mikemorency.deadmanssnitch.tags:
    id: 12345
    state: absolute
    tags: []
"""

RETURN = r"""
snitches:
    description:
        - List of dictionaries that describe matching snitches
    type: list
    returned: always
    sample: [
        {
            'token': "123456",
            'name': "foo",
            'interval': "1_minute",
            'alert_type': "basic",
            'alert_email': ["foo@example.com"],
            'notes': "This is a note",
            'tags': ["foo", "bar"],
            'status': "pending",
            'created_at': "2021-01-01T00:00:00Z",
            'updated_at': "2021-01-01T00:00:00Z",
        }
    ]
"""
from ansible.module_utils.basic import AnsibleModule

import logging
from ansible_collections.mikemorency.deadmanssnitch.plugins.module_utils.module_base import (
    ModuleBase,
)

logger = logging.getLogger(__name__)


class SnitchInfoModule(ModuleBase):
    def __init__(self, module):
        super().__init__(module)

    def get_snitch_by_name(self):
        snitches = []
        for snitch in self.client.list_snitches():
            if snitch["name"] == self.params["name"]:
                snitches.append(snitch)
                break
        return snitches

    def get_snitches_by_tags(self):
        snitches = self.client.list_snitches(tags=self.params["tags"])
        return snitches if snitches else []

    def get_all_snitches(self):
        snitches = self.client.list_snitches()
        return snitches if snitches else []

    def get_snitch_by_id(self):
        snitch = self.client.get_snitch(snitch_id=self.params["id"])
        return [snitch] if snitch else []


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = {
        **ModuleBase.base_argument_spec(),
        **dict(
            name=dict(type="str", required=False),
            id=dict(type="str", required=False),
            tags=dict(type="list", elements="str", required=False),
        ),
    }

    # seed the result dict in the object
    result = dict(changed=False, snitches=[])

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[("name", "id", "tags")],
    )
    snitch_info = SnitchInfoModule(module)

    try:
        if module.params["name"]:
            result["snitches"] = snitch_info.get_snitch_by_name()
        elif module.params["id"]:
            result["snitches"] = snitch_info.get_snitch_by_id()
        elif module.params["tags"]:
            result["snitches"] = snitch_info.get_snitches_by_tags()
        else:
            result["snitches"] = snitch_info.get_all_snitches()
    except Exception as e:
        module.fail_json(
            msg=f"Failed to get snitches: {e}",
            error_type=type(e),
            error_message=str(e),
        )

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    logging.basicConfig(level=logging.NOTSET)
    main()
