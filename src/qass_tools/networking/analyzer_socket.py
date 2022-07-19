import socket
import json
import time
from enum import Enum, auto
from typing import Any, Dict
import logging
import sys


class Amplitudes(Enum):
    """ Enum class to list and check avaible amplitudes in mV to generate sine wave. 
    """
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
        """Property lists all allowed amplitudes to generate sine wave from:

        :rtype: List
        """
        return list(Amplitudes)
    
class AnalyzerCmd():
    """ Class to communicate with Analyzer over network socket. Implied Methods: start/ end measuring, set process comment, set appVars and start/stop sine generator with spefici parameters. Functions that communicate
    with an analyzer build a dictionary to store user-given settings. With the help of the "send" function each dictionary will be converted to a JSON File and send to the connected analyzer. Each response from analyzer 
    will be read out and can be saved in a dictionary.
    
    ::Example::
        import time
        opti = AnalyzerCmd(ip="192.168.2.67", port=17000)

        info = opti.get_info()
        print(info)

        opti.set_preamp(gain=800)

        proc = opti.get_process_number()

        opti.set_process_comment("Hey ich bims, eins Kommentar")

        opti.start_measuring()
        opti.start_sineGenerator(500, 191)
        time.sleep(2)
        opti.stop_sineGenerator()
        opti.stop_measuring()
    """
    def __init__(self, ip: str, port=17000):
        """Constructor of the class defines details for logger object.
        
        .. note:: The message ID provides a possibility to assign commands and there corresponding response from analyzer. And can be used for debugging.
        :param ip: Analyzer IP in network.
        :type ip: str
        :param port: Required Analyzer port, by the default always 17000.
        :type port: int

        ::Example::
            analyzer = AnalyzerCmd(ip="192.168.2.67", port=17000)
            analyzer = AnalyzerCmd(ip="192.168.2.67")
            analyzer = AnalyzerCmd("192.168.2.67")
        """
        self.ip = ip
        self.port = port
        # message ID to assign command to analyzer and specific response
        self.msgid = 0
        
        #short solution logger to sys.stdout
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
        format ='[%(asctime)s] - %(levelname)s - %(message)s')
        self.logger = logging.getLogger()
    
    def __enter__(self):
        """ Connects the machine to an analyzer reachable over user-given Input of IP (self.ip) and Port (self.port) 
        via TCP and returns an isntance of the class
        """
        # connect to socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(1)
        self.s.connect((self.ip, self.port))
        return self
    
    def __exit__(self,exc_type, exc_value, traceback):
        self.s.close()
        self.logger.info("Socket connection closed")
        if exc_type != None:
            self.logger.error(f"\nExecution type: {exc_type}\nTraceback: {traceback}")

    @property
    def get_ip(self):
        """Property that gives out connected IP.

        :rtype: str
        """
        return self.ip
    
    @property
    def get_port(self):
        """Property that gives out connected Port.

        :rtype: int
        """
        return self.port
    
    def start_measuring(self):
        """Method sends a command to the connected analyzer to start a maesuring process.
        """
        command = {'cmd': "AppCmd", "msgid": self.msgid, "p1": "startMeasuring"}
        response = self._send(command)
        self._handle_appcmd_response(response)

    def start_sineGenerator(self, frequency: int, amplitude: int):
        """Method sends command that sine generator generates a sine wave with custom frequency and amplitude settings.

        Note that you should consider that the sine generator needs a couple µs to start.

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
        response = self._send(command)
        self._handle_commserver_response(response)    
    
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
        :raise: Check for status of response. If status (key: "ok") is False, exception is risen.
        :return: Process number of current selected process
        :rtype: int
        """
        command = {'cmd': "getprocessnumber", "msgid": self.msgid}
        
        response = self._send(command)
        obj = self._handle_commserver_response(response) 
        
        if obj.get("ok") == False:
            self.logger.info(f"Optimizer response:\n{obj}")
            raise Exception("Analyzer could not perform action")
        
        return int(obj["processnumber"])
        
    #TODO: test function
    def create_project(self, project_name:str):
        """Create new project after used template with custom name.

        .. note:: Avoid spaces or other typical forbidden characters in choosen name.

        :param project_name: Name of new project
        :type project_name: str
        """
        command = {'cmd': "createloadproject", 'msgid': self.msgid, 'p1': project_name}
        
        response = self._send(command)
        self._handle_commserver_response(response) 
    
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
                    self.logger.info(f"Updated {kwarg} to {kwargs[kwarg]}")
        
        # handle case that user input complete new dict 
        if user_dict and user_dict.keys() == default_dict.keys():
            self.logger.info("Use of user defined settings for preamp.")
            # fill command with user defined settings values
            command.update(user_dict)
        else:
            # fill command with updated default dict values
            command.update(default_dict)
        
        self._send(command)
    
    #TODO: new function "CommunicationServer Command zum exportieren des Operatoren Netzes als JSON File" 
    def get_info(self)  -> Dict:
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
        self.logger.debug(response)
        # rais exception if not performed right
        if response.get("ok") == False:
            self.logger.info(f"Optimizer response:{response}")
            raise Exception("Analyzer could not perform action. Check your command details.") 

    def _handle_commserver_response(self, response) -> Dict:
        response = response[2:].decode()
        obj = json.loads(response)
        #self.logger.info(obj)
        return obj

    def _send(self, command: Dict)  -> Dict:
        # print every sended command
        self.logger.info(f"Sended command:{command}")
        # prepare command
        cmd_str = json.dumps(command).encode()
        cmd_str = (len(cmd_str)).to_bytes(2, 'big') + cmd_str
        # adding msgid 
        self.msgid += 1
        # actual sending command
   
        self.s.sendall(cmd_str)

        # handle special cases
        # setpreamp doesn't send a response at all
        if not "setpreamp" in command['cmd']:
            response = self.s.recv(4096) # readed byte count
            return response