def log_failure_details(command, stderr):
    # a little fox's way to log command failures
    print(f'error executing command: {command} \nstderr: {stderr}')
