import socket
import json
import time
from enum import Enum, auto
from typing import Any, Dict


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
        """ This method creates a dictionary "command" which is filled with information to start a new measuring. Afterwards the dictionary will be send to the conencted analyzer by the send method 
        and the command gets executed. The key 'cmd' is signalling that this message is an App Command and over 'msgid' you can assign every send message to an ID. Key "p1" always include the actual command phrase
        for the analyzer. This commands are implied in the analyzer source code. """
        command = {'cmd': "AppCmd", "msgid": self.msgid, "p1": "startMeasuring"}
        self._send(command)

    def start_sineGenerator(self, frequency: int, amplitude: int):
        """ This method creates a dictionary "command" which is filled with information to start the sine genrator. It includes the amplitude and frequency settings of the future desired measurement. 
        Afterwards the dictionary will be send to the conencted analyzer by the send method and the command gets executed. The key 'cmd' is signalling that this message is an App Command and over 
        'msgid' you can assign every send message to an ID. The key "p1" always include the actual command for the analyzer. Over the last keyword (p2) the desired settings have to be entered as a float. 
        The variables will be entered as arguments of the function. The first arguments is the deisred frequency while the second one is the desired amplitude. As a delimiter a space letter should be used. Before the
        command gets sended, input values get checked. If entered amplitude value is saved in enum class, the command will be sended. If not, and ValueError is raisen. The user will be called to enter new settings for
        sine generator. The function is called again with new settings. Due to that syntax it is secured that even the new settings will be tested."""
        a = list(Amplitudes)
        try:
            if amplitude in Amplitudes:
                command = {'cmd': "AppCmd", "msgid": self.msgid, "p1": "StartSineGen", "p2": f"{frequency} {amplitude}"}
                self._send(command)
            else: 
                raise ValueError
        except ValueError: 
            (f" Desiered amplitude cannot be set. Please enter one of the following amplitudes to continue: {a}")
            NEWamp = input("Enter new sine amplitude:")
            NEWf = input("Enter new sine frequency:")
            self.start_sineGenerator(NEWf, NEWamp)
    

    def stop_sineGenerator(self):
        """ This method creates a dictionary "command" which is filled with information to stop the running sine generator. Afterwards the dictionary will be send to the conencted analyzer by the send method
        and the command gets executed. The key 'cmd' is signalling that this message is an App Command and over 'msgid' you can assign every send message. The key "p1" always include the actual command for 
        the analyzer. This commands are implied in the analyzer source code. """        
        command = {'cmd': "AppCmd", "msgid": self.msgid, "p1": "StopSineGen"}
        self._send(command)

    def stop_measuring(self):
        """ This method creates a dictionary "command" which is filled with information to stop the running measurement. Afterwards the dictionary will be send to the conencted analyzer by the send method
        and the command gets executed. The key 'cmd' is signalling that this message is an App Command and over 'msgid' you can assign every send message. The key "p1" always include the actual command for 
        the analyzer. This commands are implied in the analyzer source code. """ 
        command = {'cmd': "AppCmd", "msgid": self.msgid, "p1": "stopMeasuring"}
        self._send(command)

    def set_process_comment(self, proc_comm: str):
        """ This method creates a dictionary "command" which is filled with information to set a process comment in the current process. Afterwards the dictionary will be send to the conencted analyzer 
        by the send method and the command gets executed. The created dictionary differs because it has it own ComServer Command. The key 'cmd' now gives information about the analyzer actions and in "p1"
        are more detailed information saved. In this case this information should be a string. The comment is stored in database under process.comment """
        command = {'cmd': "AppCmd", "msgid": self.msgid, "p1": "setprocesscomment", "p2": f"{proc_comm}"}
        self._send(command)

    def set_app_var(self, app_var_name:str, app_var_value:any):
        """ Method to set AppVars in operator network of analyzer. AppVar Operator reads out here set variables. AppVars have to be implemented in operator network first.
        Command is SetAppVar and due to p1 and p2 details will be set. First key contains kind of AppVar as a string. Name should match with created AppVar in operator network. Key p2 contains the 
        value of the created variable. As value can be choosed any datatyp supported by python (e.g. float, int, str, json, ...)."""
        command = {'cmd': "SetAppVar", "msgid": self.msgid, "p1": f"{app_var_name:}", "p2": f"{app_var_value}"}
        self._send(command)    
    
    def set_app_var_json(self, app_var_name:str, value:any):
        """ Method to send an AppVar. Placeholder var_name and name of AppVar Reader in operator network have to be equal. An extra method is provided because this method works with an general analyzer AppCommand.
        Process provided in Method " set_app_vars" uses his own app command. In this method by key "p1" is declared that a new AppVar has to bet set. In "p2" kind of appVar as the correspodning value is set. Name 
        value is delimited by a space letter. """
        command = {'cmd': "AppCmd", "msgid": self.msgid, "p1": "SetAppVar", "p2": f"{app_var_name} {value}"}
        self._send(command)

    def get_current_process_number(self) -> int:
        command = {'cmd': "getprocessnumber", "msgid": self.msgid}
        return self._send(command)
        
    #TODO: test function
    def create_project(self, project_name:str):
        """ Method from to create a new Porject with customize name. Parameter is a string with name of the new project. Avoid spaces in name or other typical forbidden characters"""
        command = {'cmd': "createloadproject", 'msgid': self.msgid, 'p1': project_name}
        self._send(command)
    
    #cmd="getpreampinfo" p1=portnumber
        #TODO: Test function
    def send_AppCmd(self, param_one:str, param_two=None):
        
        command = {'cmd': "AppCmd", 'msgid': self.msgid, 'p1': param_one}        
        
        if param_two and param_two == str:
            command = {'cmd': "AppCmd", 'msgid': self.msgid, 'p1': param_one, 'p2': param_two}    
        else:
            raise TypeError("Second parameter has to be a string.")
  
        self._send(command)

    def set_preamp(self, user_dict=None, **kwargs):
        """ Method to set new preamp settings for multiplexer. The default settings can be seen down below. By entering a new value as **kwargs,
            you are able to change specific values in the default dict, which will be sended. The use of whole new dict is possible to replace all settings with user-defined values.
            Have in mind that your new dictionary must have identical keys like the default one. Also check supported datatypes and range manually, as a automatic overproof is not provided yet.
        Args:
                    None
        **kwargs:
                    user_dict (optional, dict): complete new dict with user defined settings
                    every multiplexer keyword provided in default settings dict
        
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
        """ Method uses communication server command to return a dictionary with analyzer information. Part of the information is the analyzer version as current used project ID and name."""
        command = {'cmd': "getinfo", "msgid": self.msgid}
        return self._send(command)
    
    def import_project(self, path: str, project_name: str, overwrite: bool=False):
        """
        Imports a project from a settings export (tar.gz or sqlite export).
        :param path: The (local) path where to find the project settings export.
        This file has to be located on the target Optimizer4D.
        :type path: str
        :param project_name: The new project`s name.
        :type project_name: str
        :param overwrite: In case of an already existing project with the same name - should we overwrite the project`s settings? Defaults to False.
        :type overwrite: bool
        """
        params = f"{path} {project_name}"
        if overwrite:
            params += " overwrite"
        
        command = {'cmd': "AppCmd", "msgid": self.msgid, "p1": "ImportProjectArchive", "p2": params}
        return self._send(command)
        
    def _send(self, command: Dict):
        """ Private method to transform the creates dictioanries in JSON Format and send them to the analyzer. Every sended message got its own unique message ID. After sending the message, the analyzer responses. The
        response will be read out and decoded after utf-8. For every sended command, the analyzer provides a section in his response which says "true" (command got executed) or "false" (command got not executed)
        The try statement checks if command get executed and raises an exception if commands were not handled correctly. In case of this exception the analyzer get commands to stop sine generator and measurement.
        Flag value (set in __init__ method) makes it possible to decide wether commands and their results will be saved in a dictionary. """
        
        print(f"Sended command:\n{command}")
        cmd_str = json.dumps(command).encode()
        cmd_str = (len(cmd_str)).to_bytes(2, 'big') + cmd_str
        self.msgid += 1
        self.s.sendall(cmd_str)
        if not "setpreamp" in command['cmd']:
            response = self.s.recv(4096) # readed byte count
            
            if "AppCmd" in command['cmd']:
                response = response.decode("utf-8") #utf-8 decode type
                print(f"Optimizer response:\n{response}")
        # raise exception if message is not send in the right way
        #     try:
            #        response = response.decode("utf-8") #utf-8 decode type
            #        print(response)
            #        if -1 == response.find("true"):
            #            raise RuntimeError("Command was not send correctly")
            #     except RuntimeError: 
            #        self.stop_sineGenerator()
            #        self.stop_measuring()
            #        print("Command was not send correctly")
            
            elif "getprocessnumber" in command['cmd']:
                response = response[2:].decode()
                obj = json.loads(response)
                #print(f"Processnumber: {obj.gets("processnumber")}")
                return int(obj["processnumber"])
            
            else:
                response = response[2:].decode()
                obj = json.loads(response)
                return obj

        # if (self.flag == True):
        #     command_status = dict()
        #     command_status["command"] = command["p1"]
        #     a = response.rfind('"ok":')
        #     command_status["status"] = response[(a):(a+5)]
        #     self._executed_commands.append(command_status)

    def close(self):
        """ Method to close the socket connection between PC and analyzer. """
        self.s.close()


    # @property
    # def last_command(self):
    #     """ Class property for user. Reads out the last send command and corresponding response of the analyzer saved in method send. This functions ist only avaible by choosing flag=True as an class variable. Is set by
    #     initialization of analyzer object (see __init__ function).
    #     This sets if-statement located in method "send" to True, therefore a dictionary will be generated. Out of this generated dictionary the last saved entry is printed. """
    #     return self._executed_commands[-1]

    # @property
    # def all_commands(self):
    #     """ Class property for user. Reads out all sended commands since connection was enabled and the response of the analyzer saved in method send. This functions ist only avaible by choosing flag=True 
    #     as an class variable. This sets if condition in method send to True and a dictionary will be generated. Out of this generated dictionary the last saved entry is printed. """    
    #     return self._executed_commands
   
   


# Example
#analyzer = AnalyzerCmd(ip="192.168.2.67", port=17000)
#analyzer.set_process_comment("test-set-comment-remote2")
#analyzer.set_preamp(gain=800)
#proc_nr = analyzer.get_current_process_number()
#print(proc_nr)
#info =analyzer.get_info()
#print(info)
#analyzer.start_measuring()
# analyzer.start_sineGenerator(500, 191)
# time.sleep(2)
# analyzer.set_process_comment("Hey ich bims, eins Kommentar")
# analyzer.stop_sineGenerator()
# analyzer.stop_measuring()
