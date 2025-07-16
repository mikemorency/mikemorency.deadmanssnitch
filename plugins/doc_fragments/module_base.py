from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
author:
    - Mike Morency (@mikemorency)

options:
    api_key:
      description:
          - The API key to use for authenticating with Dead Man's Snitch.
          - If this is unset, the DMS_API_KEY environment variable will be used instead.
      type: str
      required: true
"""
