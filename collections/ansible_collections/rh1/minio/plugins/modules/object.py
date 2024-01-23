#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from ansible.module_utils.basic import AnsibleModule
from minio import Minio
from minio.commonconfig import CopySource
from minio.error import (InvalidResponseError, S3Error)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: object

short_description: A module for creating and removing buckets in Minio

version_added: "1.0.0"

description: Ansible custom module for interacting with MinIO to put, get, remove, list, and copy objects.

options:
    endpoint: 
        description: The MinIO server endpoint.
        required: true
        type: str
    
    access_key: 
        description: The access key for authentication.
        required: true
        type: str 
    
    secret_key: 
        description: The secret key for authentication.
        required: true
        type: str 
    
    mode:
        description: The desired state of the MinIO object (put, get, remove, list, copy).
        required: true
        type: str 

    bucket: 
        description: The MinIO bucket name
        required: true
        type: str 

    object: 
        description: The MinIO object name
        required: true
        type: str 

    src: 
        description: The content to be uploaded (for put operation).
        required: false
        type: str 

    src_bucket: 
        description: The source bucket for copy operation.
        required: false
        type: str 

    src_object: description: The source object for copy operation.
        required: false
        type: str 
    

author:
    - Karenna Rodriguez (@ykarennarod)
'''

EXAMPLES = r'''
# Upload an object to a bucket
- name: Upload an object
  rh1.minio.object:
    endpoint: {{ endpoint }}
    access_key: {{ access_key }}
    secret_ket: {{ secret_key }}
    bucket: rh1_bucket
    object: rh1_object
    mode: put

# List objects in a specified bucket
- name: List objects in rh1_bucket
  rh1.minio.object:
    endpoint: {{ endpoint }}
    access_key: {{ access_key }}
    secret_ket: {{ secret_key }}
    bucket: rh1_bucket
    mode: list
  register: object_list 

- name: Debug object list 
  ansible.builtin.debug:
    var: object_list

# Copy existing object to new object in the same bucket
- name: Copy rh1_object
  rh1.minio.object:
    endpoint: {{ endpoint }}
    access_key: {{ access_key }}
    secret_ket: {{ secret_key }}
    src_bucket: rh1_bucket
    src_object: rh1_object
    bucket: rh1_bucket
    object: new_rh1_object
    mode: copy

'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
msg:
    description: The output msg that the module generates.
    type: str
    returned: always
    sample: "MinIO object {object} uploaded to {bucket} successfully."
'''

def fput_object(module, client, bucket, object, src):
    """
    Put MinIO object of unknown size in specified bucket.

    Args:
      - module: Ansible module instance.
      - client: MinIO client instance.
      - bucket: Name of the MinIO bucket.
      - objec: Name of the MinIO object.
      - src: Content to be uploaded. 

    Returns:
      - Tuple: (success: bool, msg: str)
    """
    try:
        client.fput_object(bucket, object, src)
        return True, f'MinIO object {object} uploaded to {bucket} successfully.'
    except InvalidResponseError as e: 
        return False, str(e)

def fget_object(module, client, bucket, object, dest):
    # Get MinIO object from specified bucket.
    try:
        client.fget_object(bucket, object, dest)
        return True, f'MinIO object {object} retrieved successfully.'
    except InvalidResponseError as e:
        return False, None, str(e)

def remove_object(module, client, bucket, object):
    try: 
        client.remove_object(bucket, object)
        return True, f'MinIO object {object} removed successfully.'
    except InvalidResponseError as e:
        return False, str(e)

def list_object(module, client, bucket):
    try: 
        objects = [obj.object_name for obj in client.list_objects(bucket)]
        return True, f'Existing MinIO objects in {bucket}: {objects}'
    except InvalidResponseError as e: 
        return False, str(e)

def copy_object(module, client, bucket, object, src_bucket, src_object):
    try: 
        client.copy_object(bucket, object, CopySource(src_bucket, src_object))
        return True, f'MinIO object {src_object} copied to {object} successfully.'
    except (InvalidResponseError, S3Error) as e: 
        return False, str(e)

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        bucket=dict(type='str', required=True),
        object=dict(type='str', required=False),
        src=dict(type='str', required=False), 
        src_bucket=dict(type='str', required=False), 
        src_object=dict(type='str', required=False), 
        dest=dict(type='str', required=False), 
        mode=dict(type='str', choices=['get','put', 'copy', 'list', 'remove', 'stat', 'fget', 'fput'], required=True),
        access_key=dict(type='str', required=True),
        secret_key=dict(type='str', required=True),
        endpoint=dict(type='str', required=True),
    )

    result = dict(
        changed=False,
        msg=""
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )
    
    client = Minio(
        module.params['endpoint'],
        access_key=module.params['access_key'],
        secret_key=module.params['secret_key'],
    )

    if module.check_mode:
        result['changed'] = True
        module.exit_json(**result)

    if module.params['mode'] == "remove": 
        success, msg = remove_object(
            module=module,
            client=client,
            bucket=module.params['bucket'], 
            object=module.params['object']
        )
        result['msg'] = msg

    elif module.params['mode'] == "fput": 
        success, msg = fput_object(
            module=module,
            client=client,
            bucket=module.params['bucket'], 
            object=module.params['object'], 
            src=module.params['src']
        )
        result['msg'] = msg
    
    elif module.params['mode'] == "fget": 
        success, msg = fget_object(
            module=module,
            client=client,
            bucket=module.params['bucket'], 
            object=module.params['object'], 
            dest=module.params['dest']
        )
        result['msg'] = msg

    elif module.params['mode'] == "list": 
        success, msg = list_object(
            module=module,
            client=client,
            bucket=module.params['bucket'], 
        )
        result['msg'] = msg
    
    elif module.params['mode'] == "copy": 
        success, msg = copy_object(
            module=module,
            client=client,
            bucket=module.params['bucket'], 
            object=module.params['object'], 
            src_bucket=module.params['src_bucket'], 
            src_object=module.params['src_object'], 
        )
        result['msg'] = msg

    elif module.params['mode'] == "stat": 
        success, msg = stat_object(
            module=module,
            client=client,
            bucket=module.params['bucket'], 
            object=module.params['object'], 
        )
        result['msg'] = msg

    # Register success or failure 
    if success:
        result['changed'] = True
    else:
        result['msg'] = f"Failed to perform MinIO operation: {msg}"
        module.fail_json(**result)
        
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()