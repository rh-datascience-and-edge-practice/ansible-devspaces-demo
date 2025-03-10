#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
from minio import Minio
from minio.error import S3Error
__metaclass__ = type

DOCUMENTATION = r'''
---
module: bucket

short_description: A module for creating and removing buckets in Minio

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: Create buckets! Remove buckets! All the bucket things!

options:
    name:
        description: This is the message to send to the test module.
        required: true
        type: str
    new:
        description:
            - Control to demo if the result of this module is changed or not.
            - Parameter description can be a list as well.
        required: false
        type: bool
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
# extends_documentation_fragment:
#     - my_namespace.my_collection.my_doc_fragment_name

author:
    - Brady Spiva (@brady-spiva)
'''

EXAMPLES = r'''
# Create a bucket
- name: Create a bucket
    rh1.minio.bucket:
        minio_url: "{{ minio_url }}"
        name: "{{ bucket_name }}"
        state: present
        access_key: "{{ access_key }}"
        secret_key: "{{ secret_key }}"

# Delete a bucket
- name: Delete a bucket
    rh1.minio.bucket:
        minio_url: "{{ minio_url }}"
        name: "{{ bucket_name }}"
        state: absent
        access_key: "{{ access_key }}"
        secret_key: "{{ secret_key }}"
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
changed:
    description: Whether or not the module has made changes
    type: bool
    returned: always
    sample: 'goodbye'
'''

from ansible.module_utils.basic import AnsibleModule

def make_bucket(client, name):
    # Create bucket.
    buckets = client.list_buckets()
    if name not in buckets: 
        client.make_bucket(name)
        return "Bucket" + name + "was created." 
    else: 
        return "Bucket" + name + "already exists"

def remove_bucket(client, name):
    # TODO: remove bucket with the provided name
    raise NotImplementedError("remove_bucket not implemented")

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        minio_url=dict(type='str', required=True),
        name=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present','absent']),
        access_key=dict(type='str', required=True),
        secret_key=dict(type='str', required=True),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    client = Minio(
        module.params['minio_url'],
        access_key=module.params['access_key'],
        secret_key=module.params['secret_key'],
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)
    
    # if the "state" param is "present", then call "make_bucket" function
    if module.params['state'] == 'present':
        make_bucket(client=client, name=module.params['name'])
        # indicate that the module has made a change
        result['changed'] = True

    # TODO: if the "state" param is "absent", then call "remove_bucket" function

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()