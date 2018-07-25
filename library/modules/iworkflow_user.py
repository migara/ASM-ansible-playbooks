#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 F5 Networks Inc.
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
module: iworkflow_user
short_description: Manage users in iWorkflow
description:
  - Manage users in iWorkflow.
version_added: 2.4
options:
  name:
    description:
      - Name of the user that you want to manage.
    required: True
  description:
    description:
      - An optional description for the user.
    required: False
    default: None
  state:
    description:
      - When C(state) is C(present), ensures that the user exists. When
        C(state) is C(absent), ensures that the user is removed.
    required: False
    default: present
    choices:
      - present
      - absent
extends_documentation_fragment: f5
requirements:
    - iWorkflow >= 2.1.0
author:
    - Tim Rupp (@caphrim007)
'''

EXAMPLES = r'''
- name: Create a ...
  iworkflow_user:
    name: foo
    password: secret
    server: lb.mydomain.com
    state: present
    user: admin
  delegate_to: localhost
'''

RETURN = r'''
# only common fields returned
'''


from ansible.module_utils.f5_utils import (
    AnsibleF5Client,
    AnsibleF5Parameters,
    F5ModuleError,
    HAS_F5SDK,
    iControlUnexpectedHTTPError
)


class Parameters(AnsibleF5Parameters):
    api_map = {
        'displayName': 'description'
    }
    returnables = []

    api_attributes = [
        'description',
    ]

    updatables = []

    def to_return(self):
        result = {}
        try:
            for returnable in self.returnables:
                result[returnable] = getattr(self, returnable)
            result = self._filter_params(result)
        except Exception:
            pass
        return result

    def api_params(self):
        result = {}
        for api_attribute in self.api_attributes:
            if self.api_map is not None and api_attribute in self.api_map:
                result[api_attribute] = getattr(self, self.api_map[api_attribute])
            else:
                result[api_attribute] = getattr(self, api_attribute)
        result = self._filter_params(result)
        return result


class ModuleManager(object):
    def __init__(self, client):
        self.client = client
        self.have = None
        self.want = Parameters(self.client.module.params)
        self.changes = Parameters()

    def _set_changed_options(self):
        changed = {}
        for key in Parameters.returnables:
            if getattr(self.want, key) is not None:
                changed[key] = getattr(self.want, key)
        if changed:
            self.changes = Parameters(params=changed)

    def _update_changed_options(self):
        changed = {}
        for key in Parameters.updatables:
            if getattr(self.want, key) is not None:
                attr1 = getattr(self.want, key)
                attr2 = getattr(self.have, key)
                if attr1 != attr2:
                    changed[key] = attr1
        if changed:
            self.changes = Parameters(params=changed)
            return True
        return False

    def exec_module(self):
        changed = False
        result = dict()
        state = self.want.state

        try:
            if state == "present":
                changed = self.present()
            elif state == "absent":
                changed = self.absent()
        except iControlUnexpectedHTTPError as e:
            raise F5ModuleError(str(e))

        changes = self.changes.to_return()
        result.update(**changes)
        result.update(dict(changed=changed))
        return result

    def exists(self):
        return self.client.api.shared.authz.users.user.exists(
            name=self.want.name
        )

    def present(self):
        if self.exists():
            return self.update()
        else:
            return self.create()

    def create(self):
        if self.module.check_mode:
            return True
        self.create_on_device()
        return True

    def update(self):
        pass

    def read_current_from_device(self):
        collection = self.client.api.cm.cloud.tenants_s.get_collection(
            requests_params=dict(
                params="$filter=name+eq+'{0}'".format(self.want.name)
            )
        )
        resource = collection.pop()
        result = resource.attrs
        return Parameters(params=result)

    def create_on_device(self):
        params = self.want.api_params()
        self.client.api.cm.cloud.tenants_s.tenant.create(
            name=self.want.name,
            **params
        )
        return True

    def absent(self):
        if self.exists():
            return self.remove()
        return False

    def remove(self):
        if self.module.check_mode:
            return True
        self.remove_from_device()
        if self.exists():
            raise F5ModuleError("Failed to delete the tenant")
        return True

    def remove_from_device(self):
        collection = self.client.api.cm.cloud.tenants_s.get_collection(
            requests_params=dict(
                params="$filter=name+eq+'{0}'".format(self.want.name)
            )
        )
        resource = collection.pop()
        resource.delete()


class ArgumentSpec(object):
    def __init__(self):
        self.supports_check_mode = True
        self.argument_spec = dict(
            name=dict(required=True),
            description=dict(type='str'),
            contact_address=dict(type='str'),
            contact_phone=dict(type='str'),
            contact_email=dict(type='str'),
            state=dict(
                required=False,
                default='present',
                choices=['absent', 'present']
            )
        )
        self.f5_product_name = 'iworkflow'


def main():
    if not HAS_F5SDK:
        raise F5ModuleError("The python f5-sdk module is required")

    spec = ArgumentSpec()

    client = AnsibleF5Client(
        argument_spec=spec.argument_spec,
        supports_check_mode=spec.supports_check_mode,
        f5_product_name=spec.f5_product_name
    )

    try:
        mm = ModuleManager(client)
        results = mm.exec_module()
        client.module.exit_json(**results)
    except F5ModuleError as e:
        client.module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
