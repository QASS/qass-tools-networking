import src.qass.tools.networking.analyzer_ssh as SSH

##### Example 1 ########
""" Simple example for examine all supported hardware information and store them as local JSON File."""
with SSH.SSHConnector("machine_IP", ssh_password="ssh_password") as terminal:
    terminal.set_sudo_password("sudo_host_password")
    res = terminal.get_hardware_information()
    terminal.export_to_json(res)
    # please see attached JSON file

##### Example 2 ########
""" Simple example for analyzing an empty result without exception."""   
with SSH.SSHConnector("machine_IP", ssh_password="ssh_password") as terminal:
    terminal.set_sudo_password("sudo_host_password")
    #res = terminal.get_hardware_information()
    #terminal.export_to_json(res)
    out, outerr = terminal.send_command("lt", give_out_stderr=True)
    print("stdout:",out) # terminal output--> 'stdout: []'
    print("stderr:",outerr) # terminal output --> 'stderr: ['zsh:1: command not found: lt\n']'

##### Example 3 ########
""" Simple example for partially examined data."""
with SSH.SSHConnector("machine_IP", ssh_password="ssh_password") as terminal:
    terminal.set_sudo_password("sudo_host_password")
    terminal.get_BIOS_information()
    device_paths = terminal.detect_harddrives()
    for device in device_paths:
        desired_inforamtion = terminal.get_harddrive_information(device, attributes=['SATA_version', 'size'])

