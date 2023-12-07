import json
from os import name
import sys
from types import NoneType
from typing import Dict
import socket
from datetime import datetime
from paramiko import SSHClient, AutoAddPolicy, ssh_exception, channel
import getpass
import logging
import re
import time
from typing import Union, List
from tqdm.auto import tqdm


class BadPswdException(Exception):
    def __init__(self, message="Password authenticification failed three times. Programm will be interupted."):
        self.message = message
        super().__init__(self.message)

class MissingPswdError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class SSHConnector():
    def __init__(self, ip: str, user: str = "opti", ssh_password:str=None, debug_mode: bool = False): # type: ignore
        """ Initalizing helper values. Creating two different Logger instances to inherit from logger used by Paramiko module and creating own logger. Both are addressing sys.stdout.

        :param ip: IP for executing SSH connection
        :type ip: str
        :param user: Username for executing SSH connection, defaults to "opti"
        :type user: str, optional
        :param ssh_password: Password for SSH connection with host, defaults to None
        :type ssh_password: str, optional
        :param debug_mode: Debug mode which will lower the level of logged entries to DEBUG and helps to find bugs by providing more informations, defaults to False
        :type debug_mode: bool, optional
        """
        self.ip = ip
        self.username = user
        self.ssh_pswd = ssh_password
        self.sudo_pswd = None
        self.paths = {}
   
        # set logger level after user
        msg_mode = logging.DEBUG if debug_mode else logging.INFO
        self._define_paramiko_logger(msg_mode)
        self._create_module_logger(msg_mode)

    def __enter__(self):
        """Contextmanager uses open method to open SSH connection and setting automatically host key policy."""
        self.open()
        return self
    
    def open(self):
        """ Method for initalizing connection to host without contextmanager. Opens connection and sets host key policy automatically."""
        # Open SSH connection
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        # set ssh_pswd
        if not self.ssh_pswd:
            self.ssh_pswd = getpass.getpass(prompt="Add ssh passwort for opti:\n")
        # connect
        self.client.connect(self.ip, username=self.username, password=self.ssh_pswd)

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit method for contextmanager."""
        self.close()
        if exc_type != None:
            self.logger.error(
                f"\nExecution type: {exc_type}\nTraceback: {traceback}")

    def close(self):
        """Closes all still open connections and delets set root password for this session."""
        self.sudo_pswd = None
        self.pswd = None
        self.client.close()
        self.logger.info("SSH connection closed")

    def set_sudo_password(self, sudo_password:str):
        """ Method to set sudo password before executing SSH commands which need root rights

        :param sudo_password: Sudo password for connected machine
        :type sudo_password: str
        """
        self.sudo_pswd = sudo_password

    def send_command(self, command:str, give_out_stderr:bool=False, timeout:int=None): # type: ignore
        """ Method for easy command handling with SSH terminal. Command will be checked for sudo term. If term is not containing '-S' option, it will be added. In this way, beforehand set sudo password will be flushed to channel.

        :param command: Command line for linux Terminal
        :type command: str
        :param give_out_stderr: Flag to give out additional , defaults to False
        :type give_out_stderr: bool, optional
        :return: Terminal response, if command executed wihtout error
        :rtype: List
        """
        try:
            if not timeout:
                timeout = 3 
            if "sudo" in command:
                if "-S" not in command:
                    command = command.replace("sudo","sudo -S")
            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
            if "sudo" in command:
                if not self.sudo_pswd:
                    raise MissingPswdError("Sudo password is needed but missing. Please set beforehand.")
                pswd_flush = "".join((str(self.sudo_pswd),"\n")) 
                stdin.write(pswd_flush)
            output = stdout.readlines()
            if give_out_stderr == True:
                err_output = stderr.readlines()
                return output, err_output
            else:
                return output  
        except TimeoutError:
            raise BadPswdException("Command could not be executed, most likely because of password failure. Pls check your sudo password for typos.") 
        
    def _define_paramiko_logger(self, level_mode, stream=sys.stdout):
        """Overwrite already exisitng paramiko logger and adapting it to print out to sys.stdout and log custom message and time, log level.

        :param level_mode: logging msg mode (e.g. logging.debug)
        :type level_mode: Message level that will be displayed
        :param stream: Stream to which message will be send, defaults to sys.stdout
        :type stream: stream, optional
        """
        #  use paramikos logger
        self.paramiko_logger = logging.getLogger("paramiko")
        # create and define handler to print to std.out
        stdout_channel = logging.StreamHandler(stream=stream)
        stdout_channel.set_name("stdout_channel")
        stdout_channel.setLevel(level_mode)
        logging_FORMAT = logging.Formatter(
            '[%(asctime)s]  %(levelname)s: %(message)s')
        stdout_channel.setFormatter(logging_FORMAT)
        # add handler to logger
        self.paramiko_logger.addHandler(stdout_channel)

    def _create_module_logger(self, level_mode, stream=sys.stdout) -> None:
        """Creates a logger which will print out to sys.stdout and log custom message and time, log level.

        :param level_mode: logging msg mode (e.g. logging.debug)
        :type level_mode: Message level that will be displayed
        """
        logging.basicConfig(stream=stream, level=level_mode,
                            format='[%(asctime)s]  %(levelname)s: %(message)s')
        self.logger = logging.getLogger("SSH_logger")

    def detect_harddrives(self, return_paths=False) -> None:
        """ Searches for path of systemplate(s) and dataplate(s). Paths are saved as class variable or returned by keyword argument.

        :raises ValueError: If no systempath can be estimated.
        :raises ValueError: If zero dataplatepaths can be estimated.
        """
        datapaths = []
        try:
            # find system path
            # search for device which is mounted as /home
            result = self.send_command("df /home -H --output=source")
            if len(result) == 0:
                raise ValueError
            systempath = str(result[1])
            if "\n" in systempath:
                systempath = systempath.strip()
            if systempath[-1].isdigit(): # check for last char: mountpint is /dev/sda3 but for later use we only need sda
                systempath = systempath[:-1]
            self.paths.update({"systempath":systempath}) # type: ignore
            if systempath == None or systempath == "":
                raise ValueError
        except Exception as e:
            self.logger.debug(e)
            self.logger.warning(
                "Automatic detection of systemplate(s) failed. Please check manually.")
        try:
            # find dataplate paths; arbitary amount
            devices = self.send_command("lsblk -o Name,Type,MOUNTPOINT")
            # iterate through all devices
            for dev in devices:
                dev = str(dev)
                if "/data" in dev:
                    name, type, mount = dev.split(" ")
                    # convert name to path
                    path = re.sub(r'\W+','',name) # replace all non alphanumeric characters ('_' is not replaced) 
                    if path[-1].isdigit(): # check for last char: example: mountpoint is sda3 but for later use we only need sda
                        path = path[:-1]
                    path = '/dev/' + path
                    
                    # convert mount
                    mount = mount.strip()
                    datapaths.append((path,mount))
                    
                #if "/home" in dev:
            self.paths.update({"datapaths":datapaths}) # type: ignore
            if len(datapaths) == 0:
                raise ValueError
        except Exception as e:
            self.logger.debug(e)
            self.logger.warning(
                "Automatic detection of dataplate(s) failed. Please check manually.")
        if return_paths:
            return self.paths # type: ignore
 
    def get_harddrive_information(self, device:str, attributes=None)    -> Dict:
        disk_info = {}
        output = self.send_command("sudo smartctl -a " + device + " --json") # use json format
        
        # output is always list with strings so convert
        output = "".join(output) # type: ignore
        smartctl = json.loads(output) # now json again

        if not attributes:
            attributes = ["SATA_version", "SATA_linkspeed", "manufacturer_serial", "model", "relocated_areas", "power_on_hours", "size", "health_state"]

        
        function_translator= {"SATA_version": self._get_disk_SATA_version, "SATA_linkspeed":self._get_disk_SATA_linkspeed, 
                              "manufacturer_serial":self._get_disk_manufacturer_serial, "model":self._get_disk_model, "relocated_areas":self._get_disk_relocated_areas,
                                "power_on_hours":self._get_disk_power_on_hours, "size":self._get_disk_size, "health_state":self._get_disk_health_state}
        for attr in attributes:
            disk_info.update({str(attr):function_translator[attr](smartctl)})

        return disk_info
    
    def _get_disk_SATA_version(self, smartctl_output) -> str:
        try:
            return smartctl_output["sata_version"]["string"]
        except KeyError:
            self.logger.warning("SATA Version could not be read out. Empty string will be returned.")
            return str()

    def _get_disk_SATA_linkspeed(self, smartctl_output) -> str:
        try:
            return smartctl_output["interface_speed"]["current"]["string"]
        except KeyError:
            self.logger.warning("SATA Linkspeed could not be read out. Empty string will be returned.")
            return str()

    def _get_disk_manufacturer_serial(self, smartctl_output) -> str:
        try:
            return smartctl_output["serial_number"]
        except KeyError:
            self.logger.warning("Manufacturer serial could not be read out. Empty string will be returned.")
            return str()

    def _get_disk_model(self, smartctl_output) -> str:
        try:
            return smartctl_output["model_name"]
        except KeyError:
            self.logger.warning("Manufacturer serial could not be read out. Empty string will be returned.")
            return str()
        
    def _get_disk_relocated_areas(self, smartctl_output) -> int:
        """_get_disk_relocated_areas _summary_

        _extended_summary_

        :param smartctl_output: _description_
        :type smartctl_output: _type_
        :return: _description_
        :rtype: int
        """
        try:
            for idx, table_obj in enumerate(smartctl_output["ata_smart_attributes"]["table"]):
                var = table_obj.get("name", None)
                if var == "Reallocated_Sector_Ct":
                    target_idx = idx
                    break
            
            return smartctl_output["ata_smart_attributes"]["table"][target_idx]["raw"]["value"]
        except KeyError:
            self.logger.warning("Relocated areas number could not be read. mpty string will be returned.")
            return str()
        
    def _get_disk_power_on_hours(self, smartctl_output) -> int:
        """ Get harddrive power on hours out smartctl command.

        :param smartctl_output: Terminal output from "smartctl" command in JSON format
        :type smartctl_output: json
        :raises KeyError: If key is not found and returns empty string and warning.
        :return: Power-on hours of disk
        :rtype: int
        """
        try:
            return smartctl_output["power_on_time"]["hours"]  # hours
        except KeyError:
            self.logger.warning("Power on time in hours could not be read out. Empty string will be returned.")
            return str()
        
    def _get_disk_size(self, smartctl_output) -> str:
        """ Get harddrive capacity which can be used from user in Gb.  

        :param smartctl_output: Terminal output from "smartctl" command in JSON format
        :type smartctl_output: json
        :raises KeyError: If key is not found and returns empty string and warning.
        :return: Real user usable capacity from disk in Gb
        :rtype: str
        """
        try:
            size = smartctl_output["user_capacity"]["bytes"] # bytes
            return round(size / 1e+9)
        except KeyError:
            self.logger.warning("Size could not be read out. Empty string will be returned.")
            return str()

    def _get_disk_health_state(self, smartctl_output) -> str:
        """ Get disk health state from smartctl output

        :param smartctl_output: Terminal output from "smartctl" command in JSON format
        :type smartctl_output: json
        :raises KeyError: If key is not found and returns empty string and warning.
        :return: Either "healthy" or "logged error state"
        :rtype: str
        """
        try:
            health = smartctl_output["smart_status"].get("passed", None)
            if isinstance(health, NoneType):
                raise KeyError
            if health == "true" or health == True:
                return "healthy"
            else:
                return "logged error state"
        except KeyError:
            self.logger.warning("Health state could not be read out. Empty string will be returned.")
            return str()

    def get_BIOS_information(self) -> Dict:
            """Reads out BIOS vendor name, version and fabrication date [keys=vendor,version,date]. Sudo rights required.

            Used module is dmidecode. If required information cannot be read out, a wild warning will appear. In this case return will be empty string.

            :return: BIOS Information
            :rtype: Dict
            """
            try:
                bios = self.send_command("sudo dmidecode | grep -A3 'BIOS Information'")
                # build dict from terminal response
                vendor = str(bios[1]).strip() # type: ignore
                version = str(bios[2]).strip() # type: ignore
                date = str(bios[3]).strip() # type: ignore
                # split every info by key value 
                ven_key, ven_val = vendor.split(": ")
                ver_key, ver_val = version.split(": ")
                date_key, date_val = date.split(": ")
                bios_infos = {ven_key: ven_val,
                            ver_key: ver_val, date_key: date_val}
                return bios_infos
            except Exception as e:
                self.logger.debug(e)
                self.logger.warning(
                    "BIOS information could not be read out. Return is empty string.")
                return "" # type: ignore
            
    def get_linux_version(self) -> str:
        """Method to read out Linux Version.

        Information is extracted out /etc/os-release file.If required information cannot be read out, a wild warning will appear. In this case return will be empty string.

        :return: Linux version
        :rtype: str
        """
        try:
            # terminal command
            info = self.send_command("cat /etc/os-release | grep 'PRETTY_NAME'") #e.g. ['PRETTY_NAME="openSUSE Leap 15.3"\n']
            _,name,_ = str(info).split(sep='"')
            return name
        except Exception as e:
            self.logger.debug(e)
            self.logger.warning(
                "Could not find Linux version. Return is empty string")
            return ""
    
    def get_CPU_name(self) -> str:
        """Method gets CPU model name. 

        Information is extracted out /proc/cpuinfo file. If required information cannot be read out, a wild warning will appear. In this case return will be empty string.

        :return: CPU model name
        :rtype: str
        """
        try:
            # terminal command line
            cmd_info = self.send_command("cat /proc/cpuinfo | grep 'model name' | uniq") 
            #e.g. ['model name\t: AMD Ryzen 7 5700G with Radeon Graphics\n']
            _, cpu = str(cmd_info[0]).split(": ")
            return cpu
        except Exception as e:
            self.logger.debug(e)
            self.logger.warning(
                "CPU Name could not be read out. Return is empty string.")
            return ""

    def get_IP_address(self) -> str:
        """Reads out IP address.

        Information is extracted by terminal command "hostname -I". If required information cannot be read out, a wild warning will appear. In this case return will be empty string.

        :return: IP address in local network
        :rtype: str
        """
        # find analyzer_ip
        try:
            ip = self.send_command("hostname -I") #e.g.['192.168.3.241 \n']
            ip = str(ip[0]).strip()
            return ip
        except Exception as e:
            self.logger.debug(e)
            self.logger.warning(
                "IP address could not be read out. Return is empty string.")
            return ""

    def get_RAM_size(self) -> str:
        """Reads out RAM size in Gb. 

        Information is extracted out /proc/meminfo file. If required information cannot be read out, a wild warning will appear. In this case return will be empty string.

        :return: RAM memory size
        :rtype: str
        """
        try:
            # terminal command
            cmd_info = self.send_command("cat /proc/meminfo | grep 'MemTotal'")
            # filter for size only
            total_ram_kB = int("".join(filter(str.isdigit, str(cmd_info))))
            # converting to GB
            return round(total_ram_kB / (1024*1024), 2) # type: ignore
        except Exception as e:
            self.logger.debug(e)
            self.logger.warning(
                "RAM memory could not be read out. Return is empty string")
            return ""

    def get_FPGA_version(self) -> str:
        """ Method gets FPGA version.

        Information is extracted out /sys/class/qass/info file. If required information cannot be read out, a wild warning will appear. In this case return will be empty string.

        :return: CPU model name
        :rtype: str
        """
        try:
            # terminal command line
            cmd_info = self.send_command("cat /sys/class/qass/info | grep 'FPGA Version'")
            _, fpga = str(cmd_info[0]).split(": ")
            return fpga
        except Exception as e:
            self.logger.debug(e)
            self.logger.warning(
                "FPGA version could not be read out. Return is empty string.")
            return ""

    def get_hardware_information(self, systempath:str=None, datapaths:List=None)  -> Dict: # type: ignore
        """ Function to get all ready-to-use hardware information from connected device per SSH. See Example file to see dictionary structure and keys.


        :param systempath: Optional way to set datapaths if auto detection failed. Parsed argument should be tuple (device_path, mountpoint), defaults to None
        :type systempath: str, optional
        :param datapaths: Optional way to set datapaths if auto detection failed. List should contain tuples with (device_path, mountpoint), defaults to None
        :type datapaths: List, optional
        :return: Dictionary with all ready-to-use hardware information
        :rtype: Dict
        """
        # datapaths List with tuple (path,mountpoint)
        self.detect_harddrives()
        # get path to system disk # choose auto path or set by hand
        if systempath:
            systemdisk_path = systempath
        else:
            systemdisk_path = self.paths.get("systempath", None)
        
        # get datadisk paths and infos
        datadisk_info = []
        # choose auto path or set by hand
        if datapaths:
            datadisk_paths = datapaths
        else:
            datadisk_paths = self.paths["datapaths"]
        
        # Create dict for all datadisks
        for path, mountpoint in datadisk_paths:
            disk = {"device_path": path,
                "mountpoint": mountpoint,
                "infos": self.get_harddrive_information(path)}
            datadisk_info.append(disk)

        # create dict with all remaining informationa nd append datadisk dict
        info = {
            "CPU_name": self.get_CPU_name(),
            "IP_address": self.get_IP_address(),
            "linux_version": self.get_linux_version(),
            "RAM_size_Gb": self.get_RAM_size(),
            "FPGA_version": self.get_FPGA_version(),
            "systemdisk": { "device_path": systemdisk_path,
                            "mountpoint": "/home",
                            "infos": self.get_harddrive_information(systemdisk_path)},
            "datadisk": datadisk_info}
        return info
    
    def export_to_json(self, export_dict: Dict, filename:str = None) -> None:
        """ Function exports parsed dictionary to a JSON file. If not set by hand, auto filename and path will be set to optimizer hostname and creation date,
        located in the same directory as python script.

        :param export_dict: Dictionary that should be exported to local file.
        :type export_dict: str
        :param filename: Possible filename (+ path if needed) for export JSON. Optional, default to None
        :type filename: str
        """
        if not filename:
            cmd_info = self.send_command("hostname")
            analyzer_hostname = str(cmd_info[0]).replace("\n", "")
            time_now = datetime.now()
            # reconstruct
            date_string = time_now.strftime("_%Y-%m-%d_%H-%M-%S")
            file_name = analyzer_hostname + date_string + ".json"
        else:
            if not filename.endswith(".json"):
                filename = filename + ".json"
            file_name = filename
        with open(file_name, 'w') as file:
            json.dump(export_dict, file)

class AnalyzerSSH(): 
    """ Class to open a SSH connection in python context extends possible remote control of analyzer functionalities. The here used commands are tested for OpenSuse [Linux version 5.16.8]. Functionallity for other operating systems cannot be guaranteed."""

    def __init__(self, ip: str, user: str = "opti", ssh_password=None, debug_mode: bool = False):
        """ Initalizing helper values. Creating two different Logger instances to inherit from logger used by Paramiko module and creating own logger. Both are addressing sys.stdout.

        :param ip: IP for executing SSH connection
        :type ip: str
        :param username: Username for executing SSH connection, defaults to "opti"
        :type username: str, optional
        :param debug_mode: Debug mode which will lower the level of logged entries to DEBUG and helps to find bugs by providing more informations, defaults to False
        :type debug_mode: bool, optional
        """
        self.ip = ip
        self.username = user
        self.ssh_pswd = ssh_password
        self.datapaths = []
        self.sudo_psw = None
        self.systempath = None
        self.smartctl_json_system = None
        self.smartctl_json_datas = []
        self.dataplate_sizes = []
        self.all_infos = {}
        # set logger level after user
        msg_mode = logging.DEBUG if debug_mode else logging.INFO
        self._define_paramiko_logger(msg_mode)
        self._create_module_logger(msg_mode)

    def __enter__(self):
        """Contextmanager opens SSH connection and setting automatically host key policy."""
        self.open()
        return self
    
    def open(self):
        # Open SSH connection
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        # set ssh_pswd
        if not self.ssh_pswd:
            self.ssh_pswd = getpass.getpass(prompt="Add ssh passwort for opti:\n")
        # connect
        self.client.connect(self.ip, username=self.username, password=self.ssh_pswd)

    def __exit__(self, exc_type, exc_value, traceback):
        """Closes all still open connections and delets set root password for this session."""
        self.close()
        if exc_type != None:
            self.logger.error(
                f"\nExecution type: {exc_type}\nTraceback: {traceback}")

    def close(self):
        time.sleep(2)
        self.sudo_psw = None
        self.pswd = None
        self.client.close()
        self.logger.info("SSH connection closed")

    def set_sudo_password(self, sudo_password:str):
        self.sudo_psw = sudo_password
    
    def _send_ssh_command(self, command: str) -> str:
        """ Method handles sending commands to interactive shell as receiving response. In case for needed sudo password function will send either a user setted password or automatically send password already used before. For every message will be opened an own channel, which automatically closes after receiving all data out of this channel. 


        :param command: Command that should be executed in linux terminal over SSH.
        :type command: str
        :return: Terminal response
        :rtype: str
        """
        # Helper
        buffer = bytearray()
        READ_SIZE = 4096
        DECODE_STYLE = "utf-8"
        self.receive = True
        current_length = 0
        # Creating a channel for every message (Channel closes autoamtically after receiving)
        channel = self.client.get_transport().open_session()
        channel.get_pty()
        channel.exec_command(command)
        # receiving
        while self.receive:
            try:
                # Is true as the first byte is readable until nothing is left
                while channel.recv_ready():
                    # Dumb solution to solve problem that receiving is too quick...
                    time.sleep(1)
                    # save received data in buffer
                    buffer.extend(channel.recv(READ_SIZE))
                    current_length = len(buffer)
            # if timeout is reached and channels shows still data to read, just continue
            except socket.timeout as e:
                continue
            # if you have received data
            if current_length > 0:
                # decode and slice message
                terminal_response = buffer.decode(DECODE_STYLE)
                buffer = buffer[current_length:]
                current_length = 0
                # check response for request to enter sudo pswd
                if re.search(".*\[sudo\].*", terminal_response) and re.search(".*sudo.*", command):
                    try:
                        # if sudo pswd had been used before, use this one
                        if not self.sudo_psw:
                            # else: ask user for new one
                            self.sudo_psw = getpass.getpass(
                                prompt="Add root passwort for opti:\n", mask="*")
                        # send pswd
                        channel.send(f'{self.sudo_psw}\n')
                    # Handle typo mistakes
                    except ssh_exception.AuthenticationException:
                        self.pswd_failure_count = 0
                        self._handle_pswd_failure(channel)
                # handle special case of smartctl command as json
                elif re.search(".*smartctl.*", command):
                    terminal_response = json.loads(terminal_response)
                    # end loop
                    self.receive = False
                else:
                    # end loop
                    self.receive = False
        return terminal_response

    def _handle_pswd_failure(self, channel: channel.Channel) -> None:
        """Recursiv function to enter sudo password until authentification is accept. Recursive loop will be ended after third fail.

        :param channel: Used channel in which authenfication problem occured.
        :type channel: channel.Channel
        :raises BadPswdException: Custom Exception if authenfication failed. Approximated as typo mistake.
        """
        try:
            self.pswd_failure_count += 1
            self.sudo_psw = getpass.getpass(
                prompt="Add root passwort for opti:\n", mask="*")
            channel.send(f'{self.sudo_psw}\n')
        except ssh_exception.AuthenticationException:
            if self.pswd_failure_count >= 4:
                raise BadPswdException()
            self._handle_pswd_failure(channel)

    def _detect_harddrives(self) -> None:
        """ Searches autoamtically for path of systemplate and dataplates. Paths are saved as class variable. Used to get plate informations later.

        :raises Exception: If no systempath can be estimated.
        :raises Exception: If zero dataplatepaths can be estimated.
        """
        try:
            # find system path
            # search for device which is mounted as /home
            sys_info = self._send_ssh_command("df /home -H --output=source")
            sys_idx = sys_info.find("\n")
            sys_info = sys_info[sys_idx+1:]
            sys_info = sys_info.strip()
            # check for last char: mountpint is /dev/sda3 but for later use we only need sda
            if sys_info[-1].isdigit():
                sys_info = sys_info[:-1]
            self.systempath = sys_info
            if not self.systempath:
                raise Exception
        except:
            self.logger.warning(
                "Automatic detection of systemplate failed. Please check manually.")
            self.set_harddrive_paths_manually(harddrivepath=False)
        try:
            # find dataplate paths; arbitary amount
            devices = self._send_ssh_command("lsblk -o Name,MOUNTPOINT")
            datadrive_amount = re.findall(r"/data\d", devices)
            # iterate over all detected dataplates
            for idx in range(1, len(datadrive_amount)+1):
                # define individual name
                name = "/data"+str(idx)
                # find idx to indetify path
                end_idx_plate = devices.find(name)
                sd_idx_plate = devices.rfind("sd", 0, end_idx_plate)
                # minus one because there is always a white space between two infos
                plate_info = devices[sd_idx_plate:(end_idx_plate-1)]
                # save paths in list
                path = "/dev/" + plate_info[:-1]
                self.datapaths.append(path)
                if len(self.datapaths) == 0:
                    raise Exception
        except:
            self.logger.warning(
                "Automatic detection of dataplates failed. Please check manually.")
            self.set_harddrive_paths_manually(systempath=False)

    def _define_paramiko_logger(self, level_mode, stream=sys.stdout):
        """Overwrite already exisitng paramiko logger and adapting it to print out to sys.stdout and log custom message and time, log level.

        :param level_mode: logging msg mode (e.g. logging.debug)
        :type level_mode: Message level that will be displayed
        :param stream: Stream to which message will be send, defaults to sys.stdout
        :type stream: stream, optional
        """
        #  use paramikos logger
        self.paramiko_logger = logging.getLogger("paramiko")
        # create and define handler to print to std.out
        stdout_channel = logging.StreamHandler(stream=stream)
        stdout_channel.set_name("stdout_channel")
        stdout_channel.setLevel(level_mode)
        logging_FORMAT = logging.Formatter(
            '[%(asctime)s]  %(levelname)s: %(message)s')
        stdout_channel.setFormatter(logging_FORMAT)
        # add handler to logger
        self.paramiko_logger.addHandler(stdout_channel)

    def _create_module_logger(self, level_mode, stream=sys.stdout) -> None:
        """Creates a logger which will print out to sys.stdout and log custom message and time, log level.

        :param level_mode: logging msg mode (e.g. logging.debug)
        :type level_mode: Message level that will be displayed
        """
        logging.basicConfig(stream=stream, level=level_mode,
                            format='[%(asctime)s]  %(levelname)s: %(message)s')
        self.logger = logging.getLogger("SSH_logger")

    def set_harddrive_paths_manually(self, systempath: bool = True, harddrivepath: bool = True):
        translator = {"Yes": True, "yes": True, "True": True, "Ja": True, "ja": True, "y": True,
                      "Y": True, "No": False, "no": False, "Nein": False, "nein": False, "n": False, "N": False, "False": False}
        manually = input(
            "Do you want to give in harddrive paths by hand?(yes/no)\n")
        try:
            if translator[manually] == True:
                if systempath:
                    self.systempath = input(
                        "Please insert systempath now, e.g.'/dev/sda'")
                if harddrivepath:
                    self.datapaths = input(
                        "Please insert dataplates now, e.g.'/dev/sdb'. Seperate different plates with commata.").split(",")
            else:
                self.logger.info(
                    "Harddrive information will not be read please fill in manually to JSON file.")
        except:
            self.logger.info("Given answer is not known to system.")
            self.set_harddrive_paths_manually()

    def check_smartctl(self):
        """ Check if class variables already created for smartctl (per saved path in AnalyzerSSH._detect_harddrives()). If not, create ones."""
        if self.smartctl_json_system and len(self.smartctl_json_datas) == len(self.datapaths):
            pass
        else:
            self.smartctl_json_system = self.get_smartctl_output(
                self.systempath)
            for path in self.datapaths:
                self.smartctl_json_datas.append(self.get_smartctl_output(path))

    def get_BIOS_information(self) -> Dict:
        """Reads out BIOS vendor name, version and fabrication date [Keys=vendor,version,date].

        Used module is dmidecode. If required information cannot be read out, a wild warning will appear. In this case return will be empty string.

        :return: BIOS Information
        :rtype: Dict
        """
        try:
            bios = self._send_ssh_command(
                "sudo dmidecode | grep -A3 'BIOS Information'")
            _, vendor, version, date = bios.split("\r\n\t")
            ven_key, ven_val = vendor.split(": ")
            ver_key, ver_val = version.split(": ")
            date_key, date_val = date.split(": ")
            bios_infos = {ven_key: ven_val,
                          ver_key: ver_val, date_key: date_val}
            return bios_infos
        except:
            self.logger.warning(
                "BIOS information could not be read out. Return is empty string.")
            return ""

    def get_linux_version(self) -> str:
        """Function to read out Linux Version.

        Information is extracted out /etc/os-release file.If required information cannot be read out, a wild warning will appear. In this case return will be empty string.

        :return: Linux version
        :rtype: str
        """
        try:
            # terminal command
            cmd_info = self._send_ssh_command(
                "cat /etc/os-release | grep 'PRETTY_NAME'")
            idx = cmd_info.find("=")
            version = cmd_info[idx+1:]

            return version
        except:
            self.logger.warning(
                "Could not find Linux version. Return is empty string")
            return ""

    def get_CPU_name(self) -> str:
        """Function gets CPU model name. 

        Information is extracted out /proc/cpuinfo file. If required information cannot be read out, a wild warning will appear. In this case return will be empty string.

        :return: CPU model name
        :rtype: str
        """
        try:
            # terminal command line
            cmd_info = self._send_ssh_command(
                "cat /proc/cpuinfo | grep 'model name' | uniq")
            _, cpu = cmd_info.split(": ")
            return cpu
        except:
            self.logger.warning(
                "CPU Name could not be read out. Return is empty string.")
            return ""

    def get_IP_address(self) -> str:
        """Reads out IP address.

        Information is extracted by terminal command "hostname -I". If required information cannot be read out, a wild warning will appear. In this case return will be empty string.

        :return: IP address in local network
        :rtype: str
        """
        # find analyzer_ip
        try:
            ip = self._send_ssh_command("hostname -I")
            ip = ip.strip()
            self.logger.info(f"Found IP address is: {ip}")
            return ip
        except:
            self.logger.warning(
                "IP address could not be read out. Return is empty string.")
            return ""

    def get_RAM_size(self) -> str:
        """Reads out RAM size in Gb. 

        Information is extracted out /proc/meminfo file. If required information cannot be read out, a wild warning will appear. In this case return will be empty string.

        :return: RAM memory size
        :rtype: str
        """
        try:

            # terminal command
            cmd_info = self._send_ssh_command(
                "cat /proc/meminfo | grep 'MemTotal'")
            # filter for size only
            total_ram_kB = int("".join(filter(str.isdigit, cmd_info)))
            # converting to GB
            return round(total_ram_kB / (1024*1024), 2)
        except:
            self.logger.warning(
                "RAM memory could not be read out. Return is empty string")
            return ""

    def get_FPGA_version(self) -> str:
        """ Function gets FPGA version. 

        Information is extracted out /sys/class/qass/info file. If required information cannot be read out, a wild warning will appear. In this case return will be empty string.

        :return: CPU model name
        :rtype: str
        """
        try:
            # terminal command line
            cmd_info = self._send_ssh_command(
                "cat /sys/class/qass/info | grep 'FPGA Version'")
            _, fpga = cmd_info.split(": ")
            return fpga
        except:
            self.logger.warning(
                "FPGA version could not be read out. Return is empty string.")
            return ""

    def get_harddrive_SATA_version(self, smartctl_json: json) -> str:
        """ Reads out harddrive SATA version out of smartctl information.

        See AnalyzerSSH.smartctl_json_system or AnalyzerSSH.smartctl_json_data If required information cannot be read out, a wild warning will appear. Return is empty string.

        :param smartctl_json: JSON file which contains information from executed smartctl command.
        :type smartctl_json: json
        :return: SATA version of parsed harddrive or empty string.
        :rtype: str
        """
        try:
            return smartctl_json["sata_version"]["string"]
        except:
            self.logger.warning(
                "SATA version could not be read. Return is empty string.")
            return ""

    def get_harddrive_SATA_linkspeed(self, smartctl_json: json) -> str:
        """ Reads out harddrive SATA current linkspeed out of smartctl information.

        See AnalyzerSSH.smartctl_json_system or AnalyzerSSH.smartctl_json_data If required information cannot be read out, a wild warning will appear. Return is empty string.

        :param smartctl_json: JSON file which contains information from executed smartctl command. 
        :type smartctl_json: json
        :return: SATA linkspeed of parsed harddrive.
        :rtype: str
        """
        try:
            return smartctl_json["interface_speed"]["current"]["string"]
        except:
            self.logger.warning(
                "SATA linkspeed could not be read. Return is empty string.")
            return ""

    def get_harddrive_manufacture_serial(self, smartctl_json: json) -> str:
        """ Reads out harddrive manufactuare serial number out of smartctl information.

        See AnalyzerSSH.smartctl_json_system or AnalyzerSSH.smartctl_json_data If required information cannot be read out, a wild warning will appear. Return is empty string.

        :param smartctl_json: JSON file which contains information from executed smartctl command.
        :type smartctl_json: json
        :return: Manufactuares serial number of parsed harddrive.
        :rtype: str
        """
        try:
            return smartctl_json["serial_number"]
        except:
            self.logger.warning(
                "Harddrive manufractur serial could not be read. Return is empty string.")
            return ""

    def get_harddrive_type(self, smartctl_json: json) -> str:
        """ Reads out harddrive model name out of smartctl information. Type can be seen as long name with different additional information.

        See AnalyzerSSH.smartctl_json_system or AnalyzerSSH.smartctl_json_data If required information cannot be read out, a wild warning will appear. Return is empty string.

        :param smartctl_json: JSON file which contains information from executed smartctl command.
        :type smartctl_json: json
        :return: Manufactuares model name of parsed harddrive.
        :rtype: str
        """
        try:
            return smartctl_json["model_name"]
        except:
            self.logger.warning(
                "Harddrive type could not be read. Return is empty string.")
            return ""

    def get_harddrive_relocated_areas(self, smartctl_json: json) -> int:
        """ Reads out how often a harddrive was forced to relocate areas out of smartctl information.

        See AnalyzerSSH.smartctl_json_system or AnalyzerSSH.smartctl_json_data If required information cannot be read out, a wild warning will appear. Return is empty string.

        :param smartctl_json: JSON file which contains information from executed smartctl command.
        :type smartctl_json: json
        :return: Times harddrive had to relocate areas.
        :rtype: int
        """
        try:
            for idx, table_obj in enumerate(smartctl_json["ata_smart_attributes"]["table"]):
                if table_obj["name"]:
                    if table_obj["name"] == "Reallocated_Sector_Ct":
                        target_idx = idx
                        break
                    else:
                        continue
                else:
                    continue
            if target_idx:
                return smartctl_json["ata_smart_attributes"]["table"][target_idx]["raw"]["value"]
            else:
                self.logger.warning(
                    "Harddrive relocated areas number could not be read. Return is empty string.")
                return ""
        except:
            self.logger.warning(
                "Harddrive relocated areas number could not be read. Return is empty string.")
            return ""

    def get_harddrive_power_on_time(self, smartctl_json: json) -> int:
        """ Reads out total power on time of harddrive in hours out of smartctl information.

        See AnalyzerSSH.smartctl_json_system or AnalyzerSSH.smartctl_json_data If required information cannot be read out, a wild warning will appear. Return is empty string.

        :param smartctl_json: JSON file which contains information from executed smartctl command.
        :type smartctl_json: json
        :return: Power on time in hours
        :rtype: int
        """
        try:
            return smartctl_json["power_on_time"]["hours"]  # hours
        except:
            self.logger.warning(
                "Harddrive power on time could not be read. Entry will be filled with empty string.")
            return ""

    def get_harddrive_size(self, smartctl_json: json) -> str:
        """ Read out total usable size, e.g. 2 Tb harddrive has a usable space size from approx. 1,9 Tb.

        See AnalyzerSSH.smartctl_json_system or AnalyzerSSH.smartctl_json_data If required information cannot be read out, a wild warning will appear. Return is empty string.

        :param smartctl_json: JSON file which contains information from executed smartctl command.
        :type smartctl_json: json
        :return: Harddrive total usable space.
        :rtype: int
        """
        try:
            disk_size = smartctl_json["user_capacity"]["bytes"]  # bytes
            return round(disk_size / 1e+9)
        except:
            self.logger.warning(
                "Harddrive size could not be read. Return empty string.")
            return ""

    def get_harddrive_health_state(self, smartctl_json: json) -> str:
        """ Checks smartctl for health state. If test is parsed function returns "healthy". if not return is string with ERRORS logged.

        :param smartctl_json: JSON file which contains information from executed smartctl command.
        :type smartctl_json: json
        :return: "healthy" | "ERRORS logged"
        :rtype: str
        """
        try:
            if smartctl_json["smart_status"]["passed"] == "true" or smartctl_json["smart_status"]["passed"] == True:
                return "healthy"
            else:
                return "ERRORS logged"
        except:
            self.logger.warning(
                "Harddrive health status could not be read. Return is empty string.")
            return ""

    def get_smartctl_output(self, device: str) -> json:
        """ Returns smartctl output as json formatted variable.  

        :param device: Path to device
        :type device: str
        :return: Smartctl ouput in json format 
        :rtype: json
        """
        cmd = "sudo smartctl -a " + device + " --json"
        cmd_info = self._send_ssh_command(cmd)
        return cmd_info

    def _get_machine_info(self):
        """ Method to save CPU name, IP address, Linux version and RAM size into class dictionary all_infos."""
        self.all_infos["CPU_name"] = self.get_CPU_name()
        self.all_infos["IP_address"] = self.get_IP_address()
        self.all_infos["linux_version"] = self.get_linux_version()
        self.all_infos["RAM_size"] = self.get_RAM_size()
        self.all_infos["FPGA_version"] = self.get_FPGA_version()

    def _get_systemdrive_info(self):
        """ Method to save all information regarding the systemplate into class dictionary all_infos. Additionally a progressbar is generated over the process."""
        with tqdm(total=100, desc="Computing systemplate informations") as bar:
            self.all_infos["systemplate_SATA_version"] = self.get_harddrive_SATA_version(
                self.smartctl_json_system)
            bar.update((100/8))
            self.all_infos["systemplate_SATA_linkspeed"] = self.get_harddrive_SATA_linkspeed(
                self.smartctl_json_system)
            bar.update((100/8))
            self.all_infos["systemplate_health_state"] = self.get_harddrive_health_state(
                self.smartctl_json_system)
            bar.update((100/8))
            self.all_infos["systemplate_size"] = self.get_harddrive_size(
                self.smartctl_json_system)
            bar.update((100/8))
            self.all_infos["systemplate_power_on_time"] = self.get_harddrive_power_on_time(
                self.smartctl_json_system)
            bar.update((100/8))
            self.all_infos["systemplate_relocated_areas"] = self.get_harddrive_relocated_areas(
                self.smartctl_json_system)
            bar.update((100/8))
            self.all_infos["systemplate_type"] = self.get_harddrive_type(
                self.smartctl_json_system)
            bar.update((100/8))
            self.all_infos["systemplate_manufractuar_serial"] = self.get_harddrive_manufacture_serial(
                self.smartctl_json_system)
            bar.update((100/8))

    def _get_datadrive_info(self):
        """ Method to save all information regarding the dataplates into class dictionary all_infos. Additionally a progressbar is generated over the process."""
        # get all dataplates
        self.dataplate_info_list = []
        for plate in self.smartctl_json_datas:
            with tqdm(total=100, desc="Computing dataplate informations") as bar:
                plate_dict = {}
                plate_dict["dataplate_SATA_version"] = self.get_harddrive_SATA_version(
                    plate)
                bar.update(100/8)
                plate_dict["dataplate_SATA_linkspeed"] = self.get_harddrive_SATA_linkspeed(
                    plate)
                bar.update(100/8)
                plate_dict["dataplate_health_state"] = self.get_harddrive_health_state(
                    plate)
                bar.update(100/8)
                plate_dict["dataplate_size"] = self.get_harddrive_size(plate)
                bar.update(100/8)
                plate_dict["dataplate_power_on_time"] = self.get_harddrive_power_on_time(
                    plate)
                bar.update(100/8)
                plate_dict["dataplate_relocated_areas"] = self.get_harddrive_relocated_areas(
                    plate)
                bar.update(100/8)
                plate_dict["dataplate_type"] = self.get_harddrive_type(plate)
                bar.update(100/8)
                plate_dict["dataplate_manufractuar_serial"] = self.get_harddrive_manufacture_serial(
                    plate)
                bar.update(100/8)
                self.dataplate_info_list.append(plate_dict)
        self.all_infos["dataplates"] = self.dataplate_info_list

    def get_all_infos(self) -> Dict:
        """ Function to get all information at once. Including all dataplates.

        :return: Dictionary will all avaible Information.
        :rtype: Dict
        """
        try:
            # get smartctl
            self.check_smartctl()
            print("eins")
            # get single infos
            all_infos = {"CPU_name": self.get_CPU_name(),
                         "IP_address": self.get_IP_address(),
                         "linux_version": self.get_linux_version(),
                         "RAM_size": self.get_RAM_size(),
                         "FPGA_version": self.get_FPGA_version(),
                         "systemplate_SATA_version": self.get_harddrive_SATA_version(self.smartctl_json_system),
                         "systemplate_SATA_linkspeed": self.get_harddrive_SATA_linkspeed(self.smartctl_json_system),
                         "systemplate_health_state": self.get_harddrive_health_state(self.smartctl_json_system),
                         "systemplate_size": self.get_harddrive_size(self.smartctl_json_system),
                         "systemplate_power_on_time": self.get_harddrive_power_on_time(self.smartctl_json_system),
                         "systemplate_relocated_areas": self.get_harddrive_relocated_areas(self.smartctl_json_system),
                         "systemplate_type": self.get_harddrive_type(self.smartctl_json_system),
                         "systemplate_manufractuar_serial": self.get_harddrive_manufacture_serial(self.smartctl_json_system)}
            print("zwo")
            # get all dataplates
            dataplate_info_list = []
            for plate in self.smartctl_json_datas:
                plate_dict = {}
                plate_dict["dataplate_SATA_version"] = self.get_harddrive_SATA_version(
                    plate)
                plate_dict["dataplate_SATA_linkspeed"] = self.get_harddrive_SATA_linkspeed(
                    plate)
                plate_dict["dataplate_health_state"] = self.get_harddrive_health_state(
                    plate)
                plate_dict["dataplate_size"] = self.get_harddrive_size(plate)
                plate_dict["dataplate_power_on_time"] = self.get_harddrive_power_on_time(
                    plate)
                plate_dict["dataplate_relocated_areas"] = self.get_harddrive_relocated_areas(
                    plate)
                plate_dict["dataplate_type"] = self.get_harddrive_type(plate)
                plate_dict["dataplate_manufractuar_serial"] = self.get_harddrive_manufacture_serial(
                    plate)
                dataplate_info_list.append(plate_dict)

            # combine all information
            all_infos["dataplates"] = dataplate_info_list
            self.logger.info("All desired information could be read")
            return all_infos
        except Exception as e:
            self.logger.warning(e)

    def export_to_json(self, export_dict: str) -> None:
        """ Function exports parsed dictionary to a JSON file. File will be located in the same directory as python script.
        Name will be match creater date and Yast-Name (hostname).

        :param export_dict: Dictionary that should be exported to local file.
        :type export_dict: str
        """
        cmd_info = self._send_ssh_command("hostname")
        analyzer_hostname = cmd_info.replace("\n", "")
        time_now = datetime.now()
        # reconstruct
        date_string = time_now.strftime("_%Y-%m-%d_%H-%M-%S")
        file_name = analyzer_hostname + date_string + ".json"
        with open(file_name, 'w') as file:
            json.dump(export_dict, file)
