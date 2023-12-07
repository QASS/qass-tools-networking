import src.qass.tools.networking.analyzer_ssh as SSH

##### Example 1 ########
""" Simple example for examine all supported hardware information and store them as local JSON File."""

with SSH.SSHConnector("192.168.3.241", ssh_password="mizer") as terminal:
    terminal.set_sudo_password("sudo_host_password")
    #res = terminal.get_hardware_information()
    #terminal.export_to_json(res)
    out, outerr = terminal.send_command("lt", give_out_stderr=True)
    print("stdout:",out)
    print("stderr:",outerr)
    


    
    