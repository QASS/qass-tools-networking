import socket
import json
import time
from enum import Enum, auto
from typing import Any


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

    def __init__(self, ip, port, flag=False):
        """ Constructor of the class connects the PC to an analyzer reachable over user-given Input of IP (self.ip) and Port (self.port). A created object of the class AnalyzerCmd(ip, port) automaticly 
        connects to given network adress. The message ID provides a method to assign commands to the analyzer and to this corresponding response from analyzer. Message ID increments in method send(self,command).
        Thrid argument "flag" is by default False. The user has to actively decide to change that variable and create an dictionary of commands wihtin (see method send). Most of the time only interesting in case
        of debugging. """
        self.ip = ip
        self.port = port
        self.flag = flag
        # message ID to assign command to analyzer and specific response
        self.msgid = 0
        # list to document last commands
        self._executed_commands = []
        # connect to socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(1)
        self.s.connect((self.ip, self.port))

    def start_measuring(self):
        """ This method creates a dictionary "command" which is filled with information to start a new measuring. Afterwards the dictionary will be send to the conencted analyzer by the send method 
        and the command gets executed. The key 'cmd' is signalling that this message is an App Command and over 'msgid' you can assign every send message to an ID. Key "p1" always include the actual command phrase
        for the analyzer. This commands are implied in the analyzer source code. """
        command = {'cmd': "AppCmd", "msgid": self.msgid, "p1": "startMeasuring"}
        self.send(command)

    def start_sineGenerator(self, f, amp):
        """ This method creates a dictionary "command" which is filled with information to start the sine genrator. It includes the amplitude and frequency settings of the future desired measurement. 
        Afterwards the dictionary will be send to the conencted analyzer by the send method and the command gets executed. The key 'cmd' is signalling that this message is an App Command and over 
        'msgid' you can assign every send message to an ID. The key "p1" always include the actual command for the analyzer. Over the last keyword (p2) the desired settings have to be entered as a float. 
        The variables will be entered as arguments of the function. The first arguments is the deisred frequency while the second one is the desired amplitude. As a delimiter a space letter should be used. Before the
        command gets sended, input values get checked. If entered amplitude value is saved in enum class, the command will be sended. If not, and ValueError is raisen. The user will be called to enter new settings for
        sine generator. The function is called again with new settings. Due to that syntax it is secured that even the new settings will be tested."""
        a = list(Amplitudes)
        try:
            if amp in Amplitudes:
                command = {'cmd': "AppCmd", "msgid": self.msgid, "p1": "StartSineGen", "p2": f"{f} {amp}"}
                self.send(command)
            else: 
                raise ValueError
        except ValueError: 
            (f"Desiered amplitude cannot be set. Please enter one of the following amplitudes to continue: {a}")
            NEWamp = input("Enter new sine amplitude:")
            NEWf = input("Enter new sine frequency:")
            self.start_sineGenerator(NEWf, NEWamp)
    

    def stop_sineGenerator(self):
        """ This method creates a dictionary "command" which is filled with information to stop the running sine generator. Afterwards the dictionary will be send to the conencted analyzer by the send method
        and the command gets executed. The key 'cmd' is signalling that this message is an App Command and over 'msgid' you can assign every send message. The key "p1" always include the actual command for 
        the analyzer. This commands are implied in the analyzer source code. """        
        command = {'cmd': "AppCmd", "msgid": self.msgid, "p1": "StopSineGen"}
        self.send(command)

    def stop_measuring(self):
        """ This method creates a dictionary "command" which is filled with information to stop the running measurement. Afterwards the dictionary will be send to the conencted analyzer by the send method
        and the command gets executed. The key 'cmd' is signalling that this message is an App Command and over 'msgid' you can assign every send message. The key "p1" always include the actual command for 
        the analyzer. This commands are implied in the analyzer source code. """ 
        command = {'cmd': "AppCmd", "msgid": self.msgid, "p1": "stopMeasuring"}
        self.send(command)

    def set_process_comment(self, pro_comm):
        """ This method creates a dictionary "command" which is filled with information to set a process comment in the current process. Afterwards the dictionary will be send to the conencted analyzer 
        by the send method and the command gets executed. The created dictionary differs because it has it own ComServer Command. The key 'cmd' now gives information about the analyzer actions and in "p1"
        are more detailed information saved. In this case this information should be a string. """
        command = {'cmd': "AppCmd", "msgid": self.msgid, "p1": "setprocesscomment", "p2": f"{pro_comm}"}
        self.send(command)

    def set_app_var(self, app_var_cmd:str, app_var_value:any):
        """ Method to set AppVars in operator network of analyzer. AppVar Operator reads out here set variables. AppVars have to be implemented in operator network first.
        Command is SetAppVar and due to p1 and p2 details will be set. First key contains kind of AppVar as a string. Name should match with created AppVar in operator network. Key p2 contains the 
        value of the created variable. As value can be choosed any datatyp supported by python (e.g. float, int, str, json, ...)."""
        command = {'cmd': "SetAppVar", "msgid": self.msgid, "p1": f"{app_var_cmd:}", "p2": f"{app_var_value}"}
        self.send(command)    
    
    def set_app_var_json(self, var_name:str, value:any):
        """ Method to send an AppVar. Placeholder var_name and name of AppVar Reader in operator network have to be equal. An extra method is provided because this method works with an general analyzer AppCommand.
        Process provided in Method " set_app_vars" uses his own app command. In this method by key "p1" is declared that a new AppVar has to bet set. In "p2" kind of appVar as the correspodning value is set. Name 
        value is delimited by a space letter. """
        comand = {'cmd': "AppCmd", "msgid": self.msgid, "p1": "SetAppVar", "p2": f"{var_name} {value}"}
        self.send(comand)

    def get_current_process_number(self):
        command = {'cmd': "getprocessnumber", "msgid": self.msgid}
        cmd_str = json.dumps(command).encode()
        cmd_str = (len(cmd_str)).to_bytes(2, 'big') + cmd_str
        self.msgid += 1
        self.s.sendall(cmd_str)
        response = self.s.recv(4096) # readed byte count
        response = response[2:].decode() #utf-8 decode type
        obj = json.loads(response)
        return int(obj["processnumber"])
    
    def get_info(self):
        command = {'cmd': "getinfo", "msgid": self.msgid}
        cmd_str = json.dumps(command).encode()
        cmd_str = (len(cmd_str)).to_bytes(2, 'big') + cmd_str
        self.msgid += 1
        self.s.sendall(cmd_str)
        response = self.s.recv(4096) # readed byte count
        response = response[2:].decode() #utf-8 decode type
        obj = json.loads(response)
        return obj
        
    def send(self, command):
        """ Method to transorm the creates dictioanries in JSON Format and send them to the analyzer. Every sended message got its own unique message ID. After sending the message, the analyzer responses. The
        response will be read out and decoded after utf-8. For every sended command, the analyzer provides a section in his response which says "true" (command got executed) or "false" (command got not executed)
        The try statement checks if command get executed and raises an exception if commands were not handled correctly. In case of this exception the analyzer get commands to stop sine generator and measurement.
        Flag value (set in __init__ method) makes it possible to decide wether commands and their results will be saved in a dictionary. """
        cmd_str = json.dumps(command).encode()
        cmd_str = (len(cmd_str)).to_bytes(2, 'big') + cmd_str
        self.msgid += 1
        self.s.sendall(cmd_str)
        response = self.s.recv(4096) # readed byte count
        response = response.decode("utf-8") #utf-8 decode type
        print(response)

        # raise exception if message is not send in the right way
        try:
            if -1 == response.find("true"):
                raise RuntimeError("Command was not send correctly")
        except RuntimeError: 
            self.stop_sineGenerator()
            self.stop_measuring()
            print("Command was not send correctly")

        if (self.flag == True):
            command_status = dict()
            command_status["command"] = command["p1"]
            a = response.rfind('"ok":')
            command_status["status"] = response[(a):(a+5)]
            self._executed_commands.append(command_status)

    def close(self):
        """ Method to close the socket connection between PC and analyzer. """
        self.s.close()


    @property
    def last_command(self):
        """ Class property for user. Reads out the last send command and corresponding response of the analyzer saved in method send. This functions ist only avaible by choosing flag=True as an class variable. Is set by
        initialization of analyzer object (see __init__ function).
        This sets if-statement located in method "send" to True, therefore a dictionary will be generated. Out of this generated dictionary the last saved entry is printed. """
        return self._executed_commands[-1]

    @property
    def all_commands(self):
        """ Class property for user. Reads out all sended commands since connection was enabled and the response of the analyzer saved in method send. This functions ist only avaible by choosing flag=True 
        as an class variable. This sets if condition in method send to True and a dictionary will be generated. Out of this generated dictionary the last saved entry is printed. """    
        return self._executed_commands
   
   


# Example
# analyzer = AnalyzerCmd(ip="192.168.1.246", port=17000)
# analyzer.start_measuring()
# analyzer.start_sineGenerator(500, 191)
# time.sleep(2)
# analyzer.set_process_comment("Hey ich bims, eins Kommentar")
# analyzer.stop_sineGenerator()
# analyzer.stop_measuring()
