#!/usr/bin/python
# -*- coding: utf-8 -*-


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            admin_user=dict(required=False, default='admin'),
            password_file=dict(required=False),
            glassfish_path=dict(required=False, default='/opt/glassfish3'),
            state=dict(choices=['absent', 'present'], default='present')
        ),
        supports_check_mode=True
    )

    glassfish_path = module.params['glassfish_path']

    cluster_name = module.params['name']
    state = module.params['state']

    asadmin_command = module.get_bin_path('asadmin', True, [glassfish_path + '/bin/'])

    enviroment_changed = False

    cluster_exists = is_existing_cluster(module, asadmin_command, cluster_name)

    if not cluster_exists and state == 'present':
        execute_create_cluster(module, asadmin_command, cluster_name)
        enviroment_changed = True
    elif cluster_exists and state == 'absent':
        execute_delete_cluster(asadmin_command, cluster_name, module)
        enviroment_changed = True

    module.exit_json(changed=enviroment_changed)


def execute_delete_cluster(asadmin_command, cluster_name, module):
    if module.check_mode is False:
        execution_args = create_execution_args(module, asadmin_command, ['delete-cluster', cluster_name])

        module.run_command(execution_args, check_rc=True)


def execute_create_cluster(module, asadmin_command, cluster_name):
    if module.check_mode is False:
        execution_args = create_execution_args(module, asadmin_command, ['create-cluster', cluster_name])

        module.run_command(execution_args, check_rc=True)


def is_existing_cluster(module, asadmin_command, cluster_name):
    execution_args = create_execution_args(module, asadmin_command, ['list-clusters'])

    rc, out, err = module.run_command(execution_args, check_rc=True)
    output_lines = out.split("\n")
    domain_exists = False
    for line in output_lines:
        match = re.search('^' + cluster_name + ' .*', line)
        if match is not None:
            domain_exists = True
            break
    return domain_exists


def create_execution_args(module, asadmin_command, commands_arr):
    execution_args = [asadmin_command]
    # add admin user to command
    execution_args.extend(['--user', module.params['admin_user']])
    # add password file (if one was provided)
    if module.params['password_file'] is not None:
        execution_args.extend(['--passwordfile', module.params['password_file']])

    # add actual command and parameters
    execution_args.extend(commands_arr)
    return execution_args


from ansible.module_utils.basic import *
main()
