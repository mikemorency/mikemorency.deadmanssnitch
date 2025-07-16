#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2025, mikemorency
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: tags
short_description: Add, update, or delete tags on a snitch
description: Add, update, or delete tags on a snitch

extends_documentation_fragment:
    - mikemorency.deadmanssnitch.module_base

options:
    name:
        description:
            - The name of the snitch to create, or the new name of the snitch if updating.
            - Either O(name) or O(id) must be specified.
            - This is required when creating a new snitch.
        required: false
        type: str
    id:
        description:
            - The ID of the snitch to update.
            - Either O(name) or O(id) must be specified.
        required: false
        type: str
    tags:
        description:
            - A list of tags to modify on the snitch
            - This list is absolute. Any existing tags on the snitch will be replaced.
        type: list
        required: true
        elements: str
    state:
        description:
            - Controls if the tags should be 'present', 'absent', or 'absolute'
            - If present, O(tags) will be added if they are missing.
            - If absent, O(tags) will be removed from the snitch.
            - If absolute, O(tags) will replace any tags currently on the snitch.
        required: false
        default: present
        type: str
        choices: ['present', 'absent', 'absolute']
"""

EXAMPLES = r"""
- name: Create a new alert policy
  alert_policy:
    name: foo
    api_key: "{{ nr_api_key }}"
    account_id: 1234567
    incident_preference: PER_CONDITION

- name: Delete an alert policy
  alert_policy:
    name: foo
    api_key: "{{ nr_api_key }}"
    account_id: 1234567
    state: absent
"""

RETURN = r"""
snitch:
    description:
        - Identification for the affected snitch.
    type: dict
    returned: always
    sample: {
        'id': "123456",
        'name': "my-snitch",
    }

old_tags:
    description:
        - The tags on the snitch before the module was run.
    type: list
    returned: always
    sample: [
        "1",
        "2",
        "3"
    ]

new_tags:
    description:
        - The tags on the snitch after the module was run.
    type: list
    returned: always
    sample: [
        "1",
        "2",
        "3"
    ]
"""

from ansible.module_utils.basic import AnsibleModule
import logging
from ansible_collections.mikemorency.deadmanssnitch.plugins.module_utils.module_base import (
    ModuleBase,
)

logger = logging.getLogger(__name__)


class TagsModule(ModuleBase):
    def __init__(self, module):
        super().__init__(module)
        self._lookup_live_snitch()
        self._live_tags = set(self.live_snitch['tags'])
        self._param_tags = set(self.params['tags'])

    def _lookup_live_snitch(self):
        if self.params["id"]:
            self.live_snitch = self.client.get_snitch(snitch_id=self.params["id"])
        elif self.params["name"]:
            for snitch in self.client.list_snitches():
                if snitch["name"] == self.params["name"]:
                    self.live_snitch = snitch
                    break

        if not self.live_snitch:
            self.fail_unable_to_find_snitch()

    def state_absolute(self):
        if self._param_tags != self._live_tags:
            tags_to_change = list(self._param_tags)
            self.client.replace_snitch_tags(snitch_id=self.live_snitch["token"], tags=tags_to_change)
            return True, tags_to_change

        return False, list(self._live_tags)

    def state_present(self):
        tags_to_add = list(self._param_tags.difference(self._live_tags))
        if tags_to_add:
            new_tags = list(self._param_tags.union(self._live_tags))
            self.client.append_snitch_tags(snitch_id=self.live_snitch["token"], tags=tags_to_add)
            return True, new_tags

        return False, list(self._live_tags)

    def state_absent(self):
        tags_to_remove = list(self._param_tags.intersection(self._live_tags))
        if tags_to_remove:
            new_tags = list(self._live_tags.difference(self._param_tags))
            for tag in tags_to_remove:
                self.client.remove_snitch_tag(snitch_id=self.live_snitch["token"], tag=tag)
            return True, new_tags

        return False, list(self._live_tags)


def main():
    # define available arguments/parameters a user can pass to the module
    module_args = {
        **ModuleBase.base_argument_spec(),
        **dict(
            name=dict(type="str", required=False),
            id=dict(type="str", required=False),
            tags=dict(type="list", elements="str", required=True),
            state=dict(
                type="str",
                choices=["present", "absent", "absolute"],
                default="present",
                required=False,
            ),
        ),
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_one_of=[
            ["name", "id"],
        ]
    )
    tag_module = TagsModule(module)
    result = dict(changed=False, snitch=dict(
        name=tag_module.live_snitch['name'],
        id=tag_module.live_snitch['token']
    ))
    try:
        old_tags = tag_module.live_snitch['tags']
        if module.params['state'] == "present":
            changed, new_tags = tag_module.state_present()
        elif module.params['state'] == "absent":
            changed, new_tags = tag_module.state_absent()
        else:
            changed, new_tags = tag_module.state_absolute()

        result["changed"] = changed
        if changed:
            result["old"] = old_tags
            result["new"] = new_tags

    except Exception as e:
        tag_module.handle_exception(e)

    module.exit_json(**result)


if __name__ == "__main__":
    logging.basicConfig(level=logging.NOTSET)
    main()
