import socket
import json
from turtle import clear
import numpy as np
import time
from enum import Enum, auto, IntEnum
from typing import Any, Dict, Union
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


class SysAmplitudesType(IntEnum):
    """System amplitud types avaible in analyzer software. Helps to represent calced
    maximum amplitudes in different styles.
    """
    AMPLITUDE_DEFAULT = 0
    # Amplitude is original ADC output value from hardware
    AMPLITUDE_ADC_OUT = 1
    # Amplitude is normalized energy value. (timedif x frqdif x normalized amplitude)
    AMPLITUDE_NORM_ENERGY = 2
    # Amplitude normalized to 1 as full ADC value:
    AMPLITUDE_NORM_ONE = 3
    AMPLITUDE_MILLI_VOLT = 4
    AMPLITUDE_MICRO_VOLT = 5


class AnalyzerCmd():
    """ Class to communicate with Analyzer over network socket. Implied Methods: start/ end measuring, set process comment, set appVars and start/stop sine generator with spefici parameters. Functions that communicate
    with an analyzer build a dictionary to store user-given settings. With the help of the "send" function each dictionary will be converted to a JSON File and send to the connected analyzer. Each response from analyzer 
    will be read out and can be saved in a dictionary.
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
        self.translator = {True: "true", "start": "true",
                           "beginn": "true", "enabled": "true", "on": "true",
                           False: "false", "stop": "false", "end": "false", "disabled": "false",
                           "monitor": "monitor"}
        # short solution logger to sys.stdout
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                            format='[%(asctime)s] - %(levelname)s - %(message)s')
        self.logger = logging.getLogger()

    def __enter__(self):
        """ Connects the machine to an analyzer reachable over user-given Input of IP (self.ip) and Port (self.port) 
        via TCP and returns an isntance of the class

        :return: Instance of AnalyzerCmd class
        :rtype: AnalyzerCmd object
        """
        # connect to socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(1)
        self.s.connect((self.ip, self.port))
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        time.sleep(2.0)
        self.s.close()
        self.logger.info("Socket connection closed")
        if exc_type != None:
            self.logger.error(
                f"\nExecution type: {exc_type}\nTraceback: {traceback}")

    @property
    def socket_ip(self):
        """Property that gives out connected IP.

        :rtype: str
        """
        return self.ip

    @property
    def socket_port(self):
        """Property that gives out connected Port.

        :rtype: int
        """
        return self.port

    def start_measuring(self) -> None:
        """Method sends a command to the connected analyzer to start a maesuring process.
        """
        command = {'cmd': "AppCmd",
                   "msgid": self.msgid, "p1": "startMeasuring"}
        response = self._send(command)
        self._handle_appcmd_response(response)

    def start_sineGenerator(self, frequency: int, amplitude: int) -> None:
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
                command = {'cmd': "AppCmd", "msgid": self.msgid,
                           "p1": "StartSineGen", "p2": f"{frequency} {amplitude}"}
                response = self._send(command)
                self._handle_appcmd_response(response)
            else:
                raise ValueError
        except ValueError:
            (f" Desiered amplitude cannot be set. Please enter one of the following amplitudes to continue: {a}")
            NEWamp = input("Enter new sine amplitude:")
            NEWf = input("Enter new sine frequency:")
            self.start_sineGenerator(NEWf, NEWamp)

    def stop_sineGenerator(self) -> None:
        """Command to stop generating sine waves.
        """
        command = {'cmd': "AppCmd", "msgid": self.msgid, "p1": "StopSineGen"}
        response = self._send(command)
        self._handle_appcmd_response(response)

    def stop_measuring(self) -> None:
        """Command to stop current measuring process.
        """
        command = {'cmd': "AppCmd", "msgid": self.msgid, "p1": "stopMeasuring"}
        response = self._send(command)
        self._handle_appcmd_response(response)

    def set_process_comment(self, proc_comm: str) -> None:
        """Set a process comment for current selected process.

        Parsed string will be saved in database under entry: process.comment

        :param proc_comm: Text which should be seen and saved as process comment
        :type proc_comm: str
        """
        command = {'cmd': "AppCmd", "msgid": self.msgid,
                   "p1": "setprocesscomment", "p2": f"{proc_comm}"}
        response = self._send(command)
        self._handle_appcmd_response(response)

    def set_app_var(self, app_var_name: str, app_var_value: any) -> None:
        """Parse value to specific AppVar operator in operator network of analyzer.

        There has to be an already existing AppVar operator which can accessed by (matching) name.

        :param app_var_name: Name of existing AppVar operator.
        :type app_var_name: str
        :param app_var_value: Value which should be assigned to operator. As value can be choosed any datatyp supported by python (e.g. float, int, str, json, ...).
        :type app_var_value: any
        """
        command = {'cmd': "SetAppVar", "msgid": self.msgid,
                   "p1": f"{app_var_name:}", "p2": f"{app_var_value}"}
        response = self._send(command)
        self._handle_commserver_response(response)

    def set_app_var_appcmd(self, app_var_name: str, value: any) -> None:
        """Parse value to specific AppVar operator in operator network of analyzer.

        An extra method is provided because this method works with an general analyzer AppCommand.

        .. seealso:: set_app_var()

        :param app_var_name: Name of existing AppVar operator.
        :type app_var_name: str
        :param app_var_value: Value which should be assigned to operator. As value can be choosed any datatyp supported by python (e.g. float, int, str, json, ...).
        :type app_var_value: any
        """
        command = {'cmd': "AppCmd", "msgid": self.msgid,
                   "p1": "SetAppVar", "p2": f"{app_var_name} {value}"}
        response = self._send(command)
        self._handle_appcmd_response(response)

    def get_app_var(self, app_var_name: str) -> None:
        """Get value of AppVar by name.

        :param app_var_name: Name of AppVar to adress.
        :type app_var_name: str
        :return: AppVar value
        :rtype: any
        """
        command = {'cmd': "getappvar", "msgid": self.msgid, "p1": app_var_name}

        response = self._send(command)
        val = self._handle_commserver_response(response)
        return val.get('result')

    def remove_app_var(self, app_var_name: str) -> None:
        """ Clear and remove AppVar by name.

        :param app_var_name: Naem of AppVar to remove.
        :type app_var_name: str
        """
        command = {'cmd': "clearappvar",
                   "msgid": self.msgid, "p1": app_var_name}

        response = self._send(command)
        self._handle_commserver_response(response)

    def get_app_vars_report(self, enable=True) -> Dict:
        """ Get report about existing AppVars and their changes.

        Return dict contains list of AppVars with name and value, as access time and unixtime.

        :param enable: Can be set to, defaults to True
        :type enable: bool, optional
        :return: AppVar report
        :rtype: Dict
        """
        command = {'cmd': "reportappvars",
                   "msgid": self.msgid, "p1": f"{enable}"}

        response = self._send(command)
        val = self._handle_commserver_response(response)
        val_dict = {"appvar_list": val.get("appvar_list"), "access_time": val.get(
            "appvar_readdate"), "unix_time": val.get("unixtime")}

        return val_dict

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

        return obj.get("processnumber")

    def create_project(self, project_name: str) -> None:
        """Create new project after used template with custom name.

        .. note:: Name size has to be at least 4. Avoid spaces or other typical forbidden characters in choosen name.

        :param project_name: Name of new project
        :type project_name: str
        """
        command = {'cmd': "createloadproject",
                   'msgid': self.msgid, 'p1': project_name}

        response = self._send(command)
        self._handle_commserver_response(response)

    def send_AppCmd(self, param_one: str, param_two=None) -> None:
        """General method to send arbitrary AppCmd to analyzer.

        :param param_one: Setting which AppCmd should be used.
        :type param_one: str
        :param param_two: If needed second parameter to specify params used in AppCmd, defaults to None
        :type param_two: str, optional
        :raises TypeError: Type Check for second parameter, exception is raised if value is not equal to type str.
        """
        command = {'cmd': "AppCmd", 'msgid': self.msgid, 'p1': param_one}

        if param_two and param_two == str:
            command = {'cmd': "AppCmd", 'msgid': self.msgid,
                       'p1': param_one, 'p2': param_two}
        else:
            raise TypeError("Second parameter has to be a string.")

        response = self._send(command)
        self._handle_appcmd_response(response)

    def set_preamp(self, user_dict=None, **kwargs) -> None:
        """Method to set preamplifier and multiplexer settings.

        By entering a new value as **kwargs, you are able to change specific values in the default dict, which will be sended. The use of whole new dict is possible to replace all settings with user-defined values. Have in mind that your new dictionary must have identical keys like the default one.

        Default settings:
        | Type | Multiplexer                     | Value |
        | ---- | ------------------------------- | ----- |
        | int  | channel (dropdown item)         | 0     |
        | int  | chp (dropdown item)             | 0     |
        | int  | preampport (dropdown item)      | 0     |
        | bool | fft                             | true  |
        | bool | signal                          | false |
        | int  | samplerate (dropdown item)      | 6     |
        | int  | fftoversampling (dropdown item) | 3     |
        | int  | fftwindowing (dropdown item)    | 0     |
        | int  | fftlogarithmic (dropdown item)  | 14    |
        | bool | filter                          | false |
        | int  | gain                            | 800   |
        | int  | subport                         | 0     |

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

    def get_analyzer_versions(self) -> str:
        """Method to read out anlyzer version informations.

        :return: Informations out of info window in analyzer.
        :rtype: str
        """
        command = {'cmd': "getversions", "msgid": self.msgid}
        response = self._send(command)
        val = self._handle_commserver_response(response)
        infos = val.get("v")
        while "\\n" in infos:
            analyzer_info = analyzer_info.replace("\\n", "\n")

        return analyzer_info

    def get_project_info(self) -> Dict:
        """Method to read out anlyzer informations as current used project ID/name or analyer version.

        :return: Informations about current project.
        :rtype: Dict
        """
        command = {'cmd': "getinfo", "msgid": self.msgid}
        response = self._send(command)
        project_info = self._handle_commserver_response(response)
        project_info.pop("v")
        project_info.pop("cmd")

        return project_info

    def get_heartbeat(self) -> bool:
        """ Check if the little guy is still there.

        :return: True if message comes back.
        :rtype: bool
        """
        command = {'cmd': "heartbeat", "msgid": self.msgid}
        response = self._send(command)
        val = self._handle_commserver_response(response)
        if val:
            self.logger.info("No worries. I'm still alive.")
            return True

    def run_measuring_mode(self, mode: str = "true") -> None:
        """Start or stop a measurement

        | Measuring mode    | Key       |
        | ----------------- | --------- |
        | start monitoring  | "monitor" |
        | start measurement | "true"    |
        | stop measurement  | "false"   |

        :param mode: Choosen measuring mode, defaults to "true"
        :type mode: str, optional
        :raises ValueError: Raises if keyword argument "mode" is parsed with invalid values.
        """

        command = {'cmd': "startmeasuring",
                   "msgid": self.msgid, "p1": self.translator[mode]}
        response = self._send(command)
        self._handle_commserver_response(response)

    def run_monitoring_mode(self, mode: Union[bool, str]) -> None:
        """Start or stop monitoring modus.

        Short settings:
        | Measuring mode    | Key       |
        | ----------------- | --------- |
        | start monitoring  | "true"    |
        | stop monitoring   | "false"   |

        :param mode: Switch between start monitoring ("true") or stop monitoring  ("false"). For supported keys see translator.
        :type mode: str, bool
        """
        command = {'cmd': "startmonitoring",
                   "msgid": self.msgid, "p1": self.translator[mode]}
        response = self._send(command)
        self._handle_commserver_response(response)

    def calc_max_amp_per_band(self, **kwargs):
        """Method to calculate maximum amplitude per band. 

        By entering a new value as **kwargs, you are able to change default values, which will be sended.

        Default settings:
        | Type | Key | kwargs    | Default value | Action                   |
        | ---- | --------------- | ------------- | ------------------------ |
        | int  | channel         | 0             | Choose channel buffer    |
        | bool | plot            | true          | Creates plot buffer      |
        | bool | save            | false         | Creates buffer with data |
        | int  | amplitudetype   | 0             | Type calced of amplitude |

        .. warning:: Check supported datatypes and range manually, as a automatic overproof is not provided yet.
        :param user_dict: Possibility to parse your own dictionary instead of editing the default one, defaults to None
        :type user_dict: Dict, optional
        :raises ValueError: Parsed key or related value is not supported.
        """
        # helper dict with default values
        default_dict = {'channel': 0,
                        'plot': True,
                        'save': False,
                        'amplitudetype': SysAmplitudesType.AMPLITUDE_DEFAULT
                        }
        # Check for right kwargs keys
        for kwarg in kwargs.keys():
            if kwarg not in default_dict.keys():
                self.logger.error(
                    "Choosen settings key is not supported in this method.")
                raise ValueError(
                    "Choosen settings key is not supported in this method.")
            if kwarg == "amplitudetype" and kwargs[kwarg] not in SysAmplitudesType:
                self.logger.error(
                    "Choosen amplitudetype is not a analyzer system aplitude type.")
                raise ValueError(
                    "Choosen amplitudetype is not a analyzer system aplitude type.")

        # command to build for analyzer
        command = {'cmd': "calcmaxamplitude", 'msgid': self.msgid, 'channel': 0,
                   'plot': True,
                   'save': False,
                   'amplitudetype': SysAmplitudesType.AMPLITUDE_DEFAULT
                   }

        self.logger.info(
            f"Updated settings to {kwargs.items()}")

        command.update(kwargs)
        response = self._send(command)

        # extract important information
        response_dict = self._handle_commserver_response(response)
        max_amp = response_dict.get("p1")

        return np.fromstring(max_amp, sep=',')

    # TODO:Test
    def load_test_project(self):
        command = {'cmd': "loadtestproject", "msgid": self.msgid}
        response = self._send(command)
        return self._handle_commserver_response(response)

    # TODO:Test
    def load_last_user_project(self):
        command = {'cmd': "loaduserproject", "msgid": self.msgid}
        response = self._send(command)
        return self._handle_commserver_response(response)

    def get_max_measure_positions(self) -> Dict:
        """_summary_

        :return: Measurepositions and calculated energy value.
        :rtype: Dict
        """
        command = {'cmd': "getmaxmeasurepositions", "msgid": self.msgid}
        response = self._send(command)
        return self._handle_commserver_response(response)

    # TODO:Test
    def get_preamp_settings(self, port: int):
        command = {'cmd': "getpreampinfo",
                   "msgid": self.msgid, "p1": f"{port}"}
        response = self._send(command)
        return self._handle_commserver_response(response)

    # TODO:Test
    def start_operator_function_values(self, start=True):
        command = {'cmd': "startoperatorfunctionvalues",
                   "msgid": self.msgid, "p1": f"{start}"}
        response = self._send(command)
        return self._handle_commserver_response(response)

    # TODO:Test
    def stopp_operator_function_values(self):
        command = {'cmd': "stoppoperatorfunctionvalues", "msgid": self.msgid}
        response = self._send(command)
        return self._handle_commserver_response(response)

    # TODO:Test
    def set_serial_number_pending_process(self, serial_number: int):
        command = {'cmd': "setpendingserial",
                   "msgid": self.msgid, "p1": f"{serial_number}"}
        response = self._send(command)
        return self._handle_commserver_response(response)

    # TODO:Test
    def set_comment_pending_process(self, comment: str):
        command = {'cmd': "setpendingcomment",
                   "msgid": self.msgid, "p1": comment}
        response = self._send(command)
        return self._handle_commserver_response(response)

    # TODO:Test
    def set_comment_current_process(self, comment: str):
        """ Sets comment for current activatet process.

        Similair to set_proces_comment but as JSON communication Server command.

        :param comment: Process comment to set
        :type comment: str
        """
        command = {'cmd': "setcomment", "msgid": self.msgid,
                   "p1": comment, "quiet": f"{False}"}
        response = self._send(command)
        val_dict = self._handle_commserver_response(response)
        self._check_response(val_dict)

    # TODO:Test
    def start_operator(self, operator_name: str, operator_command: str):
        command = {'cmd': "startoperator", "msgid": self.msgid,
                   "p1": operator_name, "p2": operator_command}
        response = self._send(command)
        return self._handle_commserver_response(response)

    # TODO:Test
    def import_operators(self, operator_fielpath: str, force_load: str):
        command = {'cmd': "importoperators", "msgid": self.msgid,
                   "p1": operator_fielpath, "p2": force_load}
        response = self._send(command)
        return self._handle_commserver_response(response)

    # TODO:Test
    def import_patterns(self, directory_path: str):
        command = {'cmd': "importpatterns",
                   "msgid": self.msgid, "p1": directory_path}
        response = self._send(command)
        return self._handle_commserver_response(response)

    # TODO:Test
    def start_operator_results(self, start=True):
        command = {'cmd': "startoperatorresults",
                   "msgid": self.msgid, "p1": f"{start}"}
        response = self._send(command)
        self._handle_commserver_response(response)

    # TODO:Test
    def stop_operator_results(self):
        command = {'cmd': "stopoperatorresults",
                   "msgid": self.msgid}
        response = self._send(command)
        self._handle_commserver_response(response)

    # TODO:Test
    def get_io_input(self):
        command = {'cmd': "readioin",
                   "msgid": self.msgid}
        response = self._send(command)
        return self._handle_commserver_response(response)

    # TODO:Test
    # def set_simualted_io_output(self):
    #    command = {'cmd': "readioout",
    #               "msgid": self.msgid}
    #    response = self._send(command)
    #    return self._handle_commserver_response(response)

    # TODO:Test
    def set_io_report(self, mode: Union[str, bool]):
        """Switches I/O register report on or off.

        :param mode: Switch report to on (True) or off (False)
        :type mode: bool, str
        :return: standardized analyzer respond
        :rtype: dict
        """

        command = {'cmd': "reportio",
                   "msgid": self.msgid,
                   "p1": self.translator[mode]}
        response = self._send(command)
        self._handle_commserver_response(response)

    # TODO:Test
    def set_process_number_report(self, mode: Union[str, bool]):
        """Switches process number report on or off.

        :param mode: Switch report to on ("true") or off ("false"). For supported keys see translator.
        :type mode: bool, str
        :return: standardized analyzer response
        :rtype: dict
        """

        command = {'cmd': "reportprocessnumber",
                   "msgid": self.msgid,
                   "p1": self.translator[mode]}
        response = self._send(command)
        self._handle_commserver_response(response)

    # TODO:Test
    def get_io_output(self):
        command = {'cmd': "readioout",
                   "msgid": self.msgid}
        response = self._send(command)
        return self._handle_commserver_response(response)

    # TODO:Test
    def start_script_function(self, function_name: str, function_param: any):
        """ Start script function and return result.

        :param function_name: Name of script function
        :type function_name: str
        :param function_param: Passed param to script function (will always be passed as str.)
        :type function_param: any
        :return: Result of addressed function.
        :rtype: str
        """
        command = {'cmd': "appfunc",
                   "msgid": self.msgid, "p1": function_name, "p2": f"{function_param}"}
        response = self._send(command)
        self._handle_commserver_response(response)

    def _handle_appcmd_response(self, response):
        # change appearance
        response = response.decode("utf-8")  # utf-8 decode type
        response = json.loads(response[2:])
        self.logger.debug(response)
        self._check_response(response)

    def _check_response(self, response):
        # rais exception if not performed right
        if response.get("ok") == False:
            self.logger.debug(f"Optimizer response:{response}")
            self.logger.error(
                "Parsed cmd command is unknown to analyzer: check log and documentation.")
            raise Exception(
                "Parsed cmd command is unknown to analyzer: check log and documentation.")

    def _handle_commserver_response(self, response) -> Dict:
        response = response[2:].decode()
        response = json.loads(response)
        self.logger.debug(response)
        self._check_response(response)
        return response

    def _send(self, command: Dict) -> Dict:
        # print every sended command
        self.logger.info(f"Sended command:{command}")
        # prepare command
        cmd_str = json.dumps(command).encode()
        cmd_str = (len(cmd_str)).to_bytes(2, 'big') + cmd_str
        # adding msgid
        self.msgid += 1
        # actual sending command

        self.s.sendall(cmd_str)

    def _receive(self):
        # response = self.s.recv(4096)  # readed byte count
        analyzer_response = self.s.recv(8192)  # readed byte count
        return analyzer_response

    def _value_parser(self, expect_response=True, **kwargs):
        command = {'cmd': "",
                   "msgid": self.msgid}
        command.update(kwargs)
        self._send(command)
        if not expect_response:
            return

        analyzer_response = self._receive()

        if command['cmd'] == "appcmd":
            self._handle_appcmd_response(analyzer_response)
        else:
            return self._handle_commserver_response(analyzer_response)


with AnalyzerCmd("192.168.2.67") as opti:
    val = opti.run_monitoring_mode("mystart")
