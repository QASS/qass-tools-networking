import socket
import json
import time
from enum import Enum, auto
from typing import Any, Dict

from sqlalchemy import false


class Amplitudes(Enum):
    AMP_1 = 64
    AMP_2 = 128
    AMP_3 = 191
    AMP_4 = 255
    AMP_5 = 318
    AMP_6 = 382
    AMP_7 = 446
    AMP_8 = 509
    AMP_9 = 573
    AMP_10 = 637
    AMP_11 = 700
    AMP_12 = 764
    AMP_13 = 828
    AMP_14 = 891
    AMP_15 = 955
    
    @property
    def get_list(self):
        return list(Amplitudes)
    
class AnalyzerCmd():
    """ Class to communicate with Analyzer over network socket. Implied Methods: start/ end measuring, set process comment, set appVars and start/stop sine generator with spefici parameters. Functions that communicate
    with an analyzer build a dictionary to store user-given settings. With the help of the "send" function each dictionary will be converted to a JSON File and send to the connected analyzer. Each response from analyzer 
    will be read out and can be saved in a dictionary."""
    pro_comm = ""
    #def __init__(self, ip, port, flag=False):
    def __init__(self, ip, port):
        """ Constructor of the class connects the PC to an analyzer reachable over user-given Input of IP (self.ip) and Port (self.port). A created object of the class AnalyzerCmd(ip, port) automaticly 
        connects to given network adress. The message ID provides a method to assign commands to the analyzer and to this corresponding response from analyzer. Message ID increments in method send(self,command).
        Thrid argument "flag" is by default False. The user has to actively decide to change that variable and create an dictionary of commands wihtin (see method send). Most of the time only interesting in case
        of debugging. """
        self.ip = ip
        self.port = port
        #self.flag = flag
        # message ID to assign command to analyzer and specific response
        self.msgid = 0
        # list to document last commands
        #self._executed_commands = []
        # connect to socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(1)
        self.s.connect((self.ip, self.port))

    def start_measuring(self):
        """Method sends a command to the connected analyzer to start a maesuring process.
        """
        command = {'cmd': "AppCmd", "msgid": self.msgid, "p1": "startMeasuring"}
        response = self._send(command)
        self._handle_appcmd_response(response)

    def start_sineGenerator(self, frequency: int, amplitude: int):
        """Method sends command that sine generator generates a sine wave with custom frequency and amplitude settings.

        :param frequency: Used frequency to generate sine wave.
        :type frequency: int
        :param amplitude: Used amplitude to generate sine wave.
        :type amplitude: int
        :raises ValueError: Set amplitude has to be equal to one class constances of class Amplitudes. If exception is raised the user is asked to enter new amplitude and frequency. 
        """
        a = list(Amplitudes)
        try:
            if amplitude in Amplitudes:
                command = {'cmd': "AppCmd", "msgid": self.msgid, "p1": "StartSineGen", "p2": f"{frequency} {amplitude}"}
                response = self._send(command)
                self._handle_appcmd_response(response)
            else: 
                raise ValueError
        except ValueError: 
            (f" Desiered amplitude cannot be set. Please enter one of the following amplitudes to continue: {a}")
            NEWamp = input("Enter new sine amplitude:")
            NEWf = input("Enter new sine frequency:")
            self.start_sineGenerator(NEWf, NEWamp)
    

    def stop_sineGenerator(self):
        """Command to stop generating sine waves.
        """
        command = {'cmd': "AppCmd", "msgid": self.msgid, "p1": "StopSineGen"}
        response = self._send(command)
        self._handle_appcmd_response(response)

    def stop_measuring(self):
        """Command to stop current measuring process.
        """
        command = {'cmd': "AppCmd", "msgid": self.msgid, "p1": "stopMeasuring"}
        response = self._send(command)
        self._handle_appcmd_response(response)

    def set_process_comment(self, proc_comm: str):
        """Set a process comment for current selected process.

        Parsed string will be saved in database under entry: process.comment

        :param proc_comm: Text which should be seen and saved as process comment
        :type proc_comm: str
        """
        command = {'cmd': "AppCmd", "msgid": self.msgid, "p1": "setprocesscomment", "p2": f"{proc_comm}"}
        response = self._send(command)
        self._handle_appcmd_response(response)

    def set_app_var(self, app_var_name:str, app_var_value:any):
        """Parse value to specific AppVar operator in operator network of analyzer.

        There has to be an already existing AppVar operator which can accessed by (matching) name.

        :param app_var_name: Name of existing AppVar operator.
        :type app_var_name: str
        :param app_var_value: Value which should be assigned to operator. As value can be choosed any datatyp supported by python (e.g. float, int, str, json, ...).
        :type app_var_value: any
        """
        command = {'cmd': "SetAppVar", "msgid": self.msgid, "p1": f"{app_var_name:}", "p2": f"{app_var_value}"}
        self._send(command)    
    
    def set_app_var_appcmd(self, app_var_name:str, value:any):
        """Parse value to specific AppVar operator in operator network of analyzer.

        An extra method is provided because this method works with an general analyzer AppCommand.

        .. seealso:: set_app_var()

        :param app_var_name: Name of existing AppVar operator.
        :type app_var_name: str
        :param app_var_value: Value which should be assigned to operator. As value can be choosed any datatyp supported by python (e.g. float, int, str, json, ...).
        :type app_var_value: any
        """
        command = {'cmd': "AppCmd", "msgid": self.msgid, "p1": "SetAppVar", "p2": f"{app_var_name} {value}"}
        response = self._send(command)
        self._handle_appcmd_response(response)

    def get_process_number(self) -> int:
        """Send command to give out process number as return.

        .. note:: Analyzer response contains more information than only the process number. Private method will extract claimed information.
        :return: Process number of current selected process
        :rtype: int
        """
        command = {'cmd': "getprocessnumber", "msgid": self.msgid}
        self._send(command)
        
    #TODO: test function
    def create_project(self, project_name:str):
        """Create new project after used template with custom name.

        .. note:: Avoid spaces in name or other typical forbidden characters.

        :param project_name: Name of new project
        :type project_name: str
        """
        command = {'cmd': "createloadproject", 'msgid': self.msgid, 'p1': project_name}
        self._send(command)
    
    #cmd="getpreampinfo" p1=portnumber
        #TODO: Test function
    def send_AppCmd(self, param_one:str, param_two=None):
        """General method to send arbitrary AppCmd to analyzer.

        :param param_one: Setting which AppCmd should be used.
        :type param_one: str
        :param param_two: If needed second parameter to specify params used in AppCmd, defaults to None
        :type param_two: str, optional
        :raises TypeError: Type Check for second parameter, exception is raised if value is not equal to type str.
        """
        command = {'cmd': "AppCmd", 'msgid': self.msgid, 'p1': param_one}        
        
        if param_two and param_two == str:
            command = {'cmd': "AppCmd", 'msgid': self.msgid, 'p1': param_one, 'p2': param_two}    
        else:
            raise TypeError("Second parameter has to be a string.")
  
        response = self._send(command)
        self._handle_appcmd_response(response)
        

    def set_preamp(self, user_dict=None, **kwargs):
        """Method to set preamp settings for multiplexer.

        By entering a new value as **kwargs, you are able to change specific values in the default dict, which will be sended. The use of whole new dict is possible to replace all settings with user-defined values. Have in mind that your new dictionary must have identical keys like the default one.
        
        Default settings:
        | Type | Multiplexer     | Value |
        | ---- | --------------- | ----- |
        | int  | channel         | 0     |
        | int  | chp             | 0     |
        | int  | preampport      | 0     |
        | bool | fft             | true  |
        | bool | signal          | false |
        | int  | samplerate      | 6     |
        | int  | fftoversampling | 3     |
        | int  | fftwindowing    | 0     |
        | int  | fftlogarithmic  | 14    |
        | bool | filter          | false |
        | int  | gain            | 800   |
        | int  | subport         | 0     |

        .. warning:: Check supported datatypes and range manually, as a automatic overproof is not provided yet.
        :param user_dict: Possibility to parse your own dictionary instead of editing the default one, defaults to None
        :type user_dict: Dict, optional
        """
        # helper dict with default values
        default_dict = {'channel': "0",
                        'chp': "0",
                        'preampport': "0", 
                        'fft': "true",
                        'signal': "false",
                        'samplerate': "6",
                        'fftoversampling': "3",
                        'fftwindowing': "0",
                        'fftlogarithmic': "14",
                        'filter': "false",
                        'gain': "800",
                        'subport': "0" 
                        }
        # command to build for analyzer
        command = {'cmd': "setpreamp", 'msgid': self.msgid}
        
        # handle kwarg cases and update the default dict
        if kwargs:
            for kwarg in kwargs:
                if kwarg in default_dict.keys():
                    default_dict.update({kwarg: kwargs[kwarg]})
                    print(f"Updated {kwarg} to {kwargs[kwarg]}")
        
        # handle case that user input complete new dict 
        if user_dict and user_dict.keys() == default_dict.keys():
            print("Use of user defined settings for preamp")
            # fill command with user defined settings values
            command.update(user_dict)
        else:
            # fill command with updated default dict values
            command.update(default_dict)
        
        self._send(command)

    
    #TODO: new function "CommunicationServer Command zum exportieren des Operatoren Netzes als JSON File"
    
    def get_info(self):
        """Method to read out anlyzer informations as current used project ID/name or analyer version.

        :return: Informations out of info window in analyzer.
        :rtype: Dict
        """
        command = {'cmd': "getinfo", "msgid": self.msgid}
        response = self._send(command)
        return self._handle_commserver_response(response)

    def _handle_appcmd_response(self, response):
        # change appearance
        response = response.decode("utf-8") #utf-8 decode type
        response = json.loads(response[2:])
        # rais exception if not performed right
        if response.get("ok") == False:
            print(f"Optimizer response:\n{response}")
            raise Exception("Analyzer could not perform action") 

    def _handle_commserver_response(self, response) -> Dict:
        response = response[2:].decode()
        obj = json.loads(response)
        return obj

    def _send(self, command: Dict)  -> Dict:
        """_summary_

        _extended_summary_

        :param command: Command which should be send to analyzer
        :type command: Dict
        :return response: Sended response from analyzer.
        :rtype: Dict
        """
        # print every sended command
        print(f"Sended command:\n{command}")
        # prepare command
        cmd_str = json.dumps(command).encode()
        cmd_str = (len(cmd_str)).to_bytes(2, 'big') + cmd_str
        # adding msgid 
        self.msgid += 1
        # actual sending command
        self.s.sendall(cmd_str)

        # setpreamp doesn't send a response at all
        if not "setpreamp" in command['cmd']:
            response = self.s.recv(4096) # readed byte count
            return response

    def close(self):
        """Method to close the socket connection between machine and analyzer.
        """
        self.s.close()



# Example
analyzer = AnalyzerCmd(ip="192.168.2.67", port=17000)
#analyzer.set_process_comment("test-set-comment-remote2")
#analyzer.set_preamp(gain=800)
#proc_nr = analyzer.get_current_process_number()
#print(proc_nr)
info =analyzer.get_info()
print(info)
#analyzer.start_measuring()
# analyzer.start_sineGenerator(500, 191)
# time.sleep(2)
# analyzer.set_process_comment("Hey ich bims, eins Kommentar")
# analyzer.stop_sineGenerator()
# analyzer.stop_measuring()
