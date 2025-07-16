#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2025, mikemorency
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: snitch
short_description: Create, update, or delete a Dead Man's Snitch
description: Create, update, or delete a Dead Man's Snitch

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
    state:
        description:
            - Controls if the snitch should be 'present' or 'absent'
        required: false
        default: present
        type: str
        choices: ['present', 'absent']
    interval:
        description:
            - The interval at which the snitch will be expected to check in.
            - This is required when creating a new snitch.
        required: false
        type: str
        choices: [
            '1_minute', '2_minute', '3_minute', '5_minute', '10_minute', '15_minute', '30_minute',
            'hourly', '2_hour', '3_hour', '4_hour', '6_hour', '8_hour', '12_hour',
            'daily', 'weekly', 'monthly'
        ]
    alert_type:
        description:
            - The type of alerts the snitch will use.
            - Smart alerts require a valid license, configured in the Dead Man's Snitch dashboard.
        required: false
        type: str
        choices: ['basic', 'smart']
    alert_email:
        description:
            - One or more email addresses to which alerts should be sent.
            - This list is absolute. Any existing email addresses on the snitch will be replaced.
            - To remove all email addresses, set this to an empty list.
        required: false
        type: list
        elements: str
    notes:
        description:
            - A note to associate with the snitch.
        required: false
        type: str
    tags:
        description:
            - A list of tags to associate with the snitch.
            - Tags provided here are appended to any existing tags on the snitch, if needed.
            - For more complex tag operations, use the M(mikemorency.deadmanssnitch.snitch_tags) module.
        required: false
        type: list
        elements: str
"""

EXAMPLES = r"""
- name: Create minimal snitch
  mikemorency.deadmanssnitch.snitch:
    name: my-snitch
    interval: hourly

- name: Create more complex snitch
  mikemorency.deadmanssnitch.snitch:
    name: my-snitch
    interval: daily
    alert_type: smart
    notes: This is a test snitch
    alert_email:
      - my@example.com
    tags:
      - production
      - daily
      - some-team

- name: Update snitch
  mikemorency.deadmanssnitch.snitch:
    id: 12345
    notes: Updating description

- name: Delete snitch
  mikemorency.deadmanssnitch.snitch:
    name: my-snitch
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
"""

from ansible.module_utils.basic import AnsibleModule
import logging
from ansible_collections.mikemorency.deadmanssnitch.plugins.module_utils.module_base import (
    ModuleBase,
)

logger = logging.getLogger(__name__)


class SnitchModule(ModuleBase):
    def __init__(self, module):
        super().__init__(module)
        self.live_snitch = None

    def validate_params_for_present(self):
        if not self.live_snitch:
            for param in ["name", "interval"]:
                if not self.params[param]:
                    self.module.fail_json(
                        msg=f"{param} is required when creating a new snitch"
                    )

    def are_changes_needed(self):
        if not self.live_snitch:
            return True

        if any(
            [
                self.params["name"] is not None
                and self.params["name"] != self.live_snitch["name"],
                self.params["interval"] is not None
                and self.params["interval"] != self.live_snitch["interval"],
                self.params["alert_type"] is not None
                and self.params["alert_type"] != self.live_snitch["alert_type"],
                self.params["alert_email"] is not None
                and self.params["alert_email"] != self.live_snitch["alert_email"],
                self.params["notes"] is not None
                and self.params["notes"] != self.live_snitch["notes"],
                self.params["tags"] is not None
                and self.params["tags"] != self.live_snitch["tags"],
            ]
        ):
            return True

        return False

    def lookup_live_snitch(self):
        if self.params["id"]:
            self.live_snitch = self.client.get_snitch(snitch_id=self.params["id"])
        elif self.params["name"]:
            for snitch in self.client.list_snitches():
                if snitch["name"] == self.params["name"]:
                    self.live_snitch = snitch
                    break

        return self.live_snitch

    def state_present(self):
        if self.live_snitch:
            logger.info("Snitch already exists, it will be updated.")
            snitch = self.client.update_snitch(
                snitch_id=self.live_snitch["token"],
                name=self.params["name"],
                interval=self.params["interval"],
                alert_type=self.params["alert_type"],
                alert_email=self.params["alert_email"],
                notes=self.params["notes"],
                tags=self.params["tags"],
            )
            self.live_snitch = snitch
        else:
            snitch = self.client.create_snitch(
                name=self.params["name"],
                interval=self.params["interval"],
                alert_type=self.params["alert_type"],
                alert_email=self.params["alert_email"],
                notes=self.params["notes"],
                tags=self.params["tags"],
            )
            self.live_snitch = snitch
        return

    def state_absent(self):
        if not self.live_snitch:
            return

        self.client.delete_snitch(snitch_id=self.live_snitch["token"])
        return


def main():
    # define available arguments/parameters a user can pass to the module
    module_args = {
        **ModuleBase.base_argument_spec(),
        **dict(
            name=dict(type="str", required=False),
            id=dict(type="str", required=False),
            interval=dict(
                type="str",
                required=False,
                choices=[
                    "1_minute",
                    "2_minute",
                    "3_minute",
                    "5_minute",
                    "10_minute",
                    "15_minute",
                    "30_minute",
                    "hourly",
                    "2_hour",
                    "3_hour",
                    "4_hour",
                    "6_hour",
                    "8_hour",
                    "12_hour",
                    "daily",
                    "weekly",
                    "monthly",
                ],
            ),
            alert_type=dict(type="str", required=False, choices=["basic", "smart"]),
            alert_email=dict(type="list", elements="str", required=False),
            notes=dict(type="str", required=False),
            tags=dict(type="list", elements="str", required=False),
            state=dict(
                type="str",
                choices=["present", "absent"],
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
        ],
    )
    result = dict(changed=False, snitch=dict(name=module.params["name"]))

    snitch_module = SnitchModule(module)
    try:
        snitch_module.lookup_live_snitch()
        if module.params["state"] == "present":
            snitch_module.validate_params_for_present()
            changes_needed = snitch_module.are_changes_needed()
            result["changed"] = changes_needed
            if changes_needed:
                snitch_module.state_present()
            result['snitch']['id'] = snitch_module.live_snitch['token']
        elif module.params["state"] == "absent":
            if snitch_module.live_snitch:
                result["changed"] = True
                snitch_module.state_absent()

    except Exception as e:
        snitch_module.handle_exception(e)

    module.exit_json(**result)


if __name__ == "__main__":
    logging.basicConfig(level=logging.NOTSET)
    main()
