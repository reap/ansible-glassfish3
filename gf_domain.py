#!/usr/bin/python
# -*- coding: utf-8 -*-


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            domain=dict(required=True),
            admin_user=dict(required=False, default='admin'),
            password_file=dict(required=False),
            glassfish_path=dict(required=True),
            state=dict(choices=['absent', 'present'], default='present')
        ),
        supports_check_mode=True
    )

    glassfish_path = module.params['glassfish_path']

    domain_name = module.params['name']
    state = module.params['state']

    password_file = module.params['password_file']

    asadmin_command = module.get_bin_path('asadmin', True, [glassfish_path + '/bin/'])

    enviroment_changed = False

    domain_exists = is_existing_domain(module, asadmin_command, domain_name)

    if not domain_exists and state == 'present':
        execute_create_domain(module, asadmin_command, domain_name)
        enviroment_changed = True
    elif domain_exists and state == 'absent':
        execute_delete_domain(asadmin_command, domain_name, module)
        enviroment_changed = True

    module.exit_json(changed=enviroment_changed)


def execute_delete_domain(asadmin_command, domain_name, module):
    if module.check_mode is False:
        module.run_command([asadmin_command, 'delete-domain', domain_name], check_rc=True)


def execute_create_domain(module, asadmin_command, domain_name):
    if module.check_mode is False:
        module.run_command(
            [asadmin_command, '--user', (module.params['admin_user']), 'create-domain', '--nopassword', domain_name],
            check_rc=True)


def is_existing_domain(module, asadmin_command, domain_name):
    rc, out, err = module.run_command([asadmin_command, 'list-domains'], check_rc=True)
    output_lines = out.split("\n")
    domain_exists = False
    for line in output_lines:
        match = re.search('^' + domain_name + ' .*', line)
        if match is not None:
            domain_exists = True
            break
    return domain_exists


from ansible.module_utils.basic import *
main()
