import ctypes
import socket
import json
from turtle import clear
import numpy as np
import time
from enum import Enum, auto, IntEnum
from typing import Any, Dict, Union
import logging
import sys
import threading
import queue
from collections import defaultdict


class Amplitudes(Enum):
    """ Enum class to list and check avaible amplitudes in mV to generate sine wave. 
    """
    AMP_64_mV = 64
    AMP_128_mV = 128
    AMP_191_mV = 191
    AMP_255_mV = 255
    AMP_318_mV = 318
    AMP_382_mV = 382
    AMP_446_mV = 446
    AMP_509_mV = 509
    AMP_573_mV = 573
    AMP_637_mV = 637
    AMP_700_mV = 700
    AMP_764_mV = 764
    AMP_828_mV = 828
    AMP_891_mV = 891
    AMP_955_mV = 955

    @property
    def get_list(self):
        """Property lists all allowed amplitudes to generate sine wave from:

        :rtype: List
        """
        return list(Amplitudes)


class Channels(IntEnum):
    CHANNEL_1 = 0
    CHANNEL_2 = 1
    CHANNEL_3 = 2
    CHANNEL_4 = 3


class ChannelPorts(IntEnum):
    CHANNEL_PORT_1 = 0
    CHANNEL_PORT_2 = 1
    CHANNEL_PORT_3 = 2
    CHANNEL_PORT_4 = 3
    CHANNEL_PORT_5 = 4
    CHANNEL_PORT_6 = 5
    CHANNEL_PORT_7 = 6
    CHANNEL_PORT_8 = 7
    CHANNEL_VIRT_PORT_9 = 8
    CHANNEL_VIRT_PORT_10 = 9
    CHANNEL_VIRT_PORT_11 = 10
    CHANNEL_VIRT_PORT_12 = 11
    CHANNEL_VIRT_PORT_13 = 12
    CHANNEL_VIRT_PORT_14 = 13
    CHANNEL_VIRT_PORT_15 = 14
    CHANNEL_VIRT_PORT_16 = 15
    CHANNEL_NOT_USED = 17


class PreampPorts(IntEnum):
    PREAMP_PORT_1 = 0
    PREAMP_PORT_2 = 1
    PREAMP_PORT_3 = 2
    PREAMP_PORT_4 = 3
    PREAMP_PORT_5 = 4
    PREAMP_PORT_6 = 5
    PREAMP_PORT_7 = 6
    PREAMP_PORT_8 = 7


class Samplerates(IntEnum):
    SAMPLERATE_100_MHz = 0
    SAMPLERATE_50_MHz = 1
    SAMPLERATE_25_MHz = 2
    SAMPLERATE_12_MHz = 3
    SAMPLERATE_6_MHz = 4
    SAMPLERATE_3_MHz = 5
    SAMPLERATE_1600_kHz = 6
    SAMPLERATE_800_kHz = 7
    SAMPLERATE_400_kHz = 8
    SAMPLERATE_200_kHz = 9
    SAMPLERATE_100_kHz = 10


class FFTOversampling(IntEnum):
    FFT_OVERSAMPLING_2_TIMES = 1
    FFT_OVERSAMPLING_4_TIMES = 2
    FFT_OVERSAMPLING_8_TIMES = 3
    FFT_OVERSAMPLING_16_TIMES = 4
    FFT_OVERSAMPLING_32_TIMES = 5
    FFT_OVERSAMPLING_64_TIMES = 6
    NONE_FFT_OVERSAMPLING = 0


class FFTWindowing(IntEnum):
    FFT_WINDOWING_HANNING = 0
    NONE_FFT_WINDOWING = 1


class FFTLogarithmic(IntEnum):
    FFT_LOGARITHMIC_BASE_1 = 1
    FFT_LOGARITHMIC_BASE_2 = 2
    FFT_LOGARITHMIC_BASE_3 = 3
    FFT_LOGARITHMIC_BASE_4 = 4
    FFT_LOGARITHMIC_BASE_5 = 5
    FFT_LOGARITHMIC_BASE_6 = 6
    FFT_LOGARITHMIC_BASE_7 = 7
    FFT_LOGARITHMIC_BASE_8 = 8
    FFT_LOGARITHMIC_BASE_9 = 9
    FFT_LOGARITHMIC_BASE_10 = 10
    FFT_LOGARITHMIC_BASE_11 = 11
    FFT_LOGARITHMIC_BASE_12 = 12
    FFT_LOGARITHMIC_BASE_13 = 13
    FFT_LOGARITHMIC_BASE_14 = 14
    FFT_LOGARITHMIC_BASE_15 = 15
    FFT_LOGARITHMIC_BASE_16 = 16
    NONE_FFT_OVERSAMPLING = 0


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


class SysAreaViews(IntEnum):
    View_1 = 0
    View_2 = 1
    View_3 = 2
    View_4 = 3


class ReceiveThread(threading.Thread):
    def __init__(self, socket_obj, logger_obj, group=None, target=None, name=None, args=()):
        threading.Thread.__init__(self, group, target, name, args)
        self.return_value = "Receiver thread is now killed."
        self.lock = threading.RLock()
        self.__callbacks = defaultdict(list)
        self.s = socket_obj
        self.logger = logger_obj

    def register_callbacks(self, recognition: Union[str, int], callback) -> None:
        """ Function to register incomming analyzer response by msg_id or cmd name.
        Parsed callback will be regsitered to handle response.

        :param recognition: Recognition to identify message.
        :type recognition: str, int
        :param callback: Callback to handle response value
        :type callback: function
        """
        with self.lock:
            self.__callbacks[recognition].append(callback)

    def deregister_callbacks(self, recognition: Union[str, int], user_callback=None) -> None:
        """ Remove callback registration.

        :param recognition: Recognition to identify message.
        :type recognition: str, int
        """
        with self.lock:
            if user_callback:
                self.__callbacks[recognition].remove(user_callback)
                if len(self.__callbacks[recognition]) == 0:
                    self.__callbacks.pop(recognition)
            else:
                self.__callbacks.pop(recognition)

    def handle_response(self, response, encoding_style="utf-8") -> None:
        self.logger.debug(response)
        # change appearance
        response = response.decode(encoding_style)
        response = json.loads(response)

        with self.lock:
            if response['cmd'] in self.__callbacks:
                length = len(self.__callbacks[response['cmd']])
                if length > 1:
                    for idx in range(0, length):
                        self.__callbacks[response['cmd']][idx](response)
                else:
                    self.__callbacks[response['cmd']][0](response)
            elif 'resid' in response:
                if response['resid'] in self.__callbacks:
                    self.__callbacks[response['resid']][0](response)
            elif 'msgid' in response:
                if response['msgid'] in self.__callbacks:
                    self.__callbacks[response['msgid']][0](response)

    def run(self) -> None:
        current_len = 0
        buffer = bytearray()
        READ_SIZE = 4
        self.kill = False
        while not self.kill:
            try:
                buffer.extend(self.s.recv(READ_SIZE))
            except socket.timeout as e:
                continue
            except socket.error as e:
                self.logger.error(e)
                if int.from_bytes(buffer, byteorder='big') > 0:
                    self.logger.warning("Unfinished message received")
                    self.logger.warning(buffer)
            while (len(buffer) >= current_len and len(buffer) != 0) or (current_len is 0 and len(buffer) >= 2):
                if current_len is 0:
                    current_len = int.from_bytes(buffer[:2], byteorder='big')
                    buffer = buffer[2:]

                if len(buffer) >= current_len:
                    response = buffer[:current_len]
                    self.handle_response(response)
                    buffer = buffer[current_len:]
                    current_len = 0

    def kill_thread(self) -> None:
        #self.daemon = True
        self.kill = True
        self.join()


class AnalyzerCmd():
    """ Class for external analyzer control (system operator independant) over a TCP socket.
    """

    def __init__(self, ip: str, port=17000, debug_mode=False):
        """Constructor of the class defines details for logger object.

        :param ip: Analyzer IP in network.
        :type ip: str
        :param port: Required Analyzer port, by the default always 17000.
        :type port: int
        :param debug_mode: Logs debug messages into sys.stdout
        :type debug_mode: bool

        ::Example::
            analyzer = AnalyzerCmd(ip="192.168.2.67", port=17000)
            analyzer = AnalyzerCmd(ip="192.168.2.67")
            analyzer = AnalyzerCmd("192.168.2.67")
        """
        # helper
        self.ip = ip
        self.port = port
        # message ID to assign command to analyzer and specific response
        self.msgid = 0
        self.translator = {True: "true", "start": "true", "true": "true",
                           "beginn": "true", "enabled": "true", "enable": "true", "on": "true",
                           False: "false", "stop": "false", "end": "false", "disabled": "false",
                           "false": "false", "disable": "false", "monitor": "monitor"}
        self._io_report_count = 0
        self._proc_report_count = 0
        self._appvar_report_count = 0
        # short solution logger to sys.stdout
        msg_mode = logging.DEBUG if debug_mode else logging.INFO
        logging.basicConfig(stream=sys.stdout, level=msg_mode,
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

        # create thread instance
        self.__recv_thread = ReceiveThread(self.s, self.logger,
                                           group=None, target=None, name="receive thread")
        self.__recv_thread.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        time.sleep(2.0)
        self.__recv_thread.kill_thread()
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
        self._value_parser(cmd="AppCmd", p1="startMeasuring")

    def start_sineGenerator(self, frequency: int, amplitude: Amplitudes) -> None:
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
                self._value_parser(
                    cmd="AppCmd", p1="StartSineGen", p2=f"{frequency} {amplitude}")
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
        self._value_parser(cmd="AppCmd", p1="StopSineGen")

    def stop_measuring(self) -> None:
        """Command to stop current measuring process.
        """
        self._value_parser(cmd="AppCmd", p1="stopMeasuring")

    def set_process_comment(self, proc_comm: str) -> None:
        """Set a process comment for current selected process.

        Parsed string will be saved in database under entry: process.comment

        :param proc_comm: Text which should be seen and saved as process comment
        :type proc_comm: str
        """
        self._value_parser(cmd="AppCmd", p1="setprocesscomment", p2=proc_comm)

    # TODO:test not implemented in analyzer
    def set_area_view(self, area_amount: int) -> None:
        if 0 < area_amount <= 4:
            self._value_parser(
                cmd="AppCmd", p1="SetAreaView", p2=area_amount)
        else:
            self.logger.error("Area split is out of bounds")
            raise ValueError("Area split is out of bounds")

    def save_area_view(self, tempalte_num: int) -> None:
        """Saves current area view settings under template number. Each area can be se different.

        :param tempalte_num: Storage number to save
        :type tempalte_num: int
        """
        self._value_parser(
            cmd="AppCmd", p1="SaveAreaView", p2=tempalte_num)

    def load_area_view(self, tempalte_num: int) -> None:
        """Load presaved area view tempalte. 

        :param tempalte_num: Storage number to load
        :type tempalte_num: int
        """
        self._value_parser(
            cmd="AppCmd", p1="LoadAreaView", p2=tempalte_num)

    # TODO:test
    def load_simualtion_buffer(self, file_path: str, channel=Channels.CHANNEL_1) -> None:
        self._value_parser(cmd="AppCmd",
                           p1="SimulationBuffer", p2=f"{channel} {file_path}")

    # TODO:test
    def set_simualtion_buffer(self, channel=Channels.CHANNEL_1, mode="enable") -> None:
        keys = ["all", *Channels]
        if channel in keys:
            if channel == "all":
                self._value_parser(cmd="AppCmd",
                                   p1="SimulationBuffer", p2=self.translator[mode])
            else:
                self._value_parser(cmd="AppCmd",
                                   p1="SimulationBuffer", p2=f"{channel} {self.translator[mode]}")
        else:
            self.logger.error("Choosed channel is not supported")
            raise KeyError("Choosed channel is not supported")

    # TODO:test
    def pulsetest_channel(self, channel_number, gain: int, count: int, delay: int) -> None:
        """External set of pulse test. Only avaible for exisiting ports and sensors.

        :param channel_number: Channel where pulsetest gets executed.
        :type channel_number: int or Channels
        :param gain: Pulsetest gain in range(0,4096)
        :type gain: int
        :param count: Pulsetest count in range(0,201)
        :type count: int
        :param delay: Pulsetest delay (geater null)
        :type delay: int
        :raises ValueError: If gain is out of bounds: range(0,4096) | If count is out of bounds: range(0,200) | If delay is out of bounds: smaller zero
        """
        channel_number += channel_number
        if not 0 <= gain < 4096 and not 0 <= count < 201 and not 0 <= delay:
            self.logger.error("Params out of bounds")
            raise ValueError("Params out of bounds")

        settings = {"cmd": "AppCmd", "p1": "Preamp",
                    "p2": f"channel {channel_number} pulsetest {gain} {count} {delay}"}
        self._value_parser(**settings)

    # TODO:test
    def pulsetest_port(self, port_number, gain: int, count: int, delay: int) -> None:
        """External set of pulse test. Only avaible for exisiting ports and sensors.

        :param port_number: Port where pulsetest gets executed.
        :type port_number: int or Channels
        :param gain: Pulsetest gain in range(0,4096)
        :type gain: int
        :param count: Pulsetest count in range(0,201)
        :type count: int
        :param delay: Pulsetest delay (geater null)
        :type delay: int
        :raises ValueError: If gain is out of bounds: range(0,4096) | If count is out of bounds: range(0,200) | If delay is out of bounds: smaller zero
        """
        port_number += port_number
        if not 0 <= gain < 4096 and not 0 <= count < 201 and not 0 <= delay:
            self.logger.error("Params out of bounds")
            raise ValueError("Params out of bounds")

        settings = {"cmd": "AppCmd", "p1": "Preamp",
                    "p2": f"channel {port_number} pulsetest {gain} {count} {delay}"}
        self._value_parser(**settings)

    # TODO:test
    def frequency_test_port(self, port_number):
        self._value_parser(cmd="AppCmd", p1="Preamp",
                           p2=f"port {port_number} frqtest")

    def set_area_scale(self, area_number: int, scale=500) -> None:
        """ Set scale of each area independant.

        Scale should be in range(10,1001)
        Area should be in range(1,5)

        :param area_number: Which area should be addressed
        :type area_number: int
        :param scale: which scale should be used, defaults to 500
        :type scale: int, optional
        :raises ValueError: If parsed variables are out of bounds. See extended function summary.
        """
        if scale in range(10, 1001) and 0 < area_number <= 4:
            self._value_parser(cmd="AppCmd",
                               p1="SetAreaScale", p2=f"{area_number} {scale}")
        else:
            self.logger.error(
                "Choosen key is out of bounds. Scale should be in range(10,1001) and Area numbers betweeen 1 and (inclusive) 4.")
            raise ValueError(
                "Choosen sckeyale is out of bounds. Scale should be in range(10,1001) and Area numbers betweeen 1 and (inclusive) 4.")

    def set_area_colour(self, area_number: int, colour_scale=200):
        """Set colour scale of each area independant.

        Colour scale should be in range(10,401)
        Area should be in range(1,5)

        :param area_number: Which area should be addressed
        :type area_number: int
        :param colour_scale: which scale should be used, defaults to 200
        :type colour_scale: int, optional
        :raises ValueError: If parsed variables are out of bounds. See extended function summary.
        """
        if colour_scale in range(10, 401) and 0 < area_number <= 4:
            self._value_parser(cmd="AppCmd",
                               p1="SetAreaColor", p2=f"{area_number} {colour_scale}")
        else:
            self.logger.error(
                "Choosen key is out of bounds. Scale should be in range(10,401) and Area numbers betweeen 1 and (inclusive) 4.")
            raise ValueError(
                "Choosen key is out of bounds. Scale should be in range(10,401) and Area numbers betweeen 1 and (inclusive) 4.")

    def set_area_time_range(self, area_number: int, start_time: int, time_range: int):
        """ Set of shown time range for each area.

        :param area_number: Area which shold be addressed
        :type area_number: int
        :param start_time: Start point of time range in ms.
        :type start_time: int
        :param time_range: Range that will be shown from start_time
        :type time_range: int
        """
        self._value_parser(expect_response=False, cmd="Appcmd", p1="SetAreaPosition",
                           p2=f"{area_number} {start_time} {time_range}")

    def set_appvar(self, appvar_name: str, appvar_value: any) -> None:
        """Parse value to specific AppVar operator in operator network of analyzer.

        There has to be an already existing AppVar operator which can accessed by (matching) name.

        :param app_var_name: Name of existing AppVar operator.
        :type app_var_name: str
        :param app_var_value: Value which should be assigned to operator. As value can be choosed any datatyp supported by python (e.g. float, int, str, json, ...).
        :type app_var_value: any
        """
        self._value_parser(cmd="setappvar", p1=appvar_name, p2=appvar_value)

    def set_appvar_appcmd(self, appvar_name: str, value: any) -> None:
        """Parse value to specific AppVar operator in operator network of analyzer.

        An extra method is provided because this method works with an general analyzer AppCommand.

        .. seealso:: set_appvar()

        :param app_var_name: Name of existing AppVar operator.
        :type app_var_name: str
        :param app_var_value: Value which should be assigned to operator. As value can be choosed any datatyp supported by python (e.g. float, int, str, json, ...).
        :type app_var_value: any
        """

        self._value_parser(cmd="AppCmd", p1="SetAppVar",
                           p2=f"{appvar_name} {value}")

    def get_app_var(self, appvar_name: str) -> None:
        """Get value of AppVar by name.

        :param app_var_name: Name of AppVar to adress.
        :type app_var_name: str
        :return: AppVar value
        :rtype: any
        """
        val = self._value_parser(cmd="getappvar", p1=appvar_name)

        return val.get('result')

    def remove_appvar(self, appvar_name: str) -> None:
        """ Clear and remove AppVar by name.

        :param appvar_name: Naem of AppVar to remove.
        :type appvar_name: str
        """
        self._value_parser(cmd="clearappvar", p1=appvar_name)

    def remove_appvar_report_callback(self, callback):
        """Removes specific callback function from AppVar report callback list. 
        By removing all callbacks the report function will be automatically stopped.

        ..see also:: add_appvar_report_callback
        :param callback: Callback function that should be removed from AppVar report functionallities.
        :type callback: function
        """
        self.__recv_thread.deregister_callbacks(
            "responsereportappvars", callback)
        self._appvar_report_count -= 1
        self.logger.info(
            f"Callback {callback} for AppVar report removed")
        if self._appvar_report_count == 0:
            self._value_parser(cmd="reportappvars",
                               p1="false")
            self.logger.info("Report of AppVar stopped.")

    def add_appvar_report_callback(self, callback):
        """Add callback function to report of AppVar. Everytime a AppVar changes, added callback functions will be executed. See networking_example.py for an example.
        By adding first callback the report start automatically und will be stopped by removing all callbacks due to remove function.

        .. warning:: All callbacks need as first param "result" to catch analyzer response, if used or not.
        ..see also:: remove_appvar_report_callback
        :param callback: Added callback function when report happens.
        :type callback: function
        """
        if self._appvar_report_count == 0:
            self._value_parser(user_callback=callback, cmd="reportappvars",
                               p1="true")
        else:
            self.__recv_thread.register_callbacks(
                "responsereportappvars", callback)
        self._proc_report_count += 1
        self.logger.info(
            f"Callback {callback} for AppVar report added")

    def get_process_number(self) -> int:
        """Send command to give out process number as return.

        :return: Process number of current selected process
        :rtype: int
        """
        obj = self._value_parser(cmd="getprocessnumber")

        return obj.get("processnumber")

    def create_project(self, project_name: str) -> None:
        """Create new project after used template with custom name.

        .. note:: Name size has to be at least 4. Avoid spaces or other typical forbidden characters in choosen name.

        :param project_name: Name of new project
        :type project_name: str
        """
        self._value_parser(cmd="createloadproject", p1=project_name)

    def send_AppCmd(self, param_one: str, param_two=None) -> None:
        """General method to send arbitrary AppCmd to analyzer.

        :param param_one: Setting which AppCmd should be used.
        :type param_one: str
        :param param_two: If needed second parameter to specify params used in AppCmd, defaults to None
        :type param_two: str, optional
        :raises TypeError: Type Check for second parameter, exception is raised if value is not equal to type str.
        """
        command = {'cmd': "AppCmd", 'msgid': self.msgid, 'p1': param_one}

        if param_two:
            if param_two == str:
                self._value_parser(cmd="AppCmd", p1=param_one, p2=param_two)
            else:
                raise TypeError("Second parameter has to be a string.")
        else:
            self._value_parser(cmd="AppCmd", p1=param_one)

    def set_preamp(self, **kwargs) -> None:
        """Method to set preamplifier and multiplexer settings.

        By entering a new value as **kwargs, you are able to change default values, which will be sended.
        .. warning:: Range of params will not be checked.
        Default settings:
        | Type                  | Multiplexer     | Value        |
        | --------------------- | ----------------| ------------ |
        | Channels        | int | channel         | Channel #1   |
        | ChannelPorts    | int | chp             | Port 1       |
        | PreampPorts     | int | preampport      | Preampport 1 | 
        | Boolean               | fft             | enabled      |
        | Boolean               | signal          | disabled     |
        | samplerate      | int | samplerate      | 1600 kHz     |
        | FFTOversampling | int | fftoversampling | 8 times      |
        | FFTWindowing    | int | fftwindowing    | Hanning      |
        | FFTLogarithmic  | int | fftlogarithmic  | Base 14      |
        | Boolean               | filter          | disabled     |
        | Integer         | int | gain            | 800          |
        | Integer         | int | subport         | 0            |

        """
        # helper dict with default values
        settings = {'cmd': "setpreamp",
                    'channel': Channels.CHANNEL_1,
                    'chp': ChannelPorts.CHANNEL_PORT_1,
                    'preampport': PreampPorts.PREAMP_PORT_1,
                    'fft': True,
                    'signal': False,
                    'samplerate': Samplerates.SAMPLERATE_1600_kHz,
                    'fftoversampling': FFTOversampling.FFT_OVERSAMPLING_8_TIMES,
                    'fftwindowing': FFTWindowing.FFT_WINDOWING_HANNING,
                    'fftlogarithmic': FFTLogarithmic.FFT_LOGARITHMIC_BASE_14,
                    'filter': True,
                    'gain': 800,
                    'subport': 0
                    }
        settings.update(kwargs)
        self._value_parser(**settings)

    def get_analyzer_versions(self) -> str:
        """Method to read out anlyzer version informations.

        :return: Informations out of info window in analyzer.
        :rtype: str
        """
        val = self._value_parser(cmd="getversions")
        # process response
        infos = val.get("v")
        while "\\n" in infos:
            analyzer_info = analyzer_info.replace("\\n", "\n")

        return analyzer_info

    def get_project_info(self) -> Dict:
        """Method to read out anlyzer informations as current used project ID/name or analyer version.

        :return: Informations about current project.
        :rtype: Dict
        """
        project_info = self._value_parser(cmd="getinfo")
        # process response
        project_info.pop("v")
        project_info.pop("cmd")

        return project_info

    def get_heartbeat(self) -> bool:
        """ Check if the little guy is still there.

        :return: True if message comes back.
        :rtype: bool
        """
        val = self._value_parser(cmd="heartbeat")
        # process response
        if val:
            self.logger.info("No worries. I'm still alive.")
            return True

    def run_measuring_mode(self, mode: Union[bool, str]) -> None:
        """Start or stop a measurement.

        Short settings:
        | Measuring mode    | Key       |
        | ----------------- | --------- |
        | start monitoring  | "monitor" |
        | start measurement | "true"    |
        | stop measurement  | "false"   |

        :param mode: Choosen measuring mode out of table above.
        :type mode: str, bool
        :raises KeyError: Raises if keyword argument "mode" is parsed with invalid values.
        """
        self._value_parser(cmd="startmeasuring", p1=self.translator[mode])

    def run_monitoring_mode(self, mode: Union[bool, str]) -> None:
        """Start or stop monitoring modus. See

        Short settings:
        | Measuring mode    | Key       |
        | ----------------- | --------- |
        | Start monitoring  | "true"    |
        | Stop monitoring   | "false"   |

        :param mode: Switch between start monitoring ("true") or stop monitoring  ("false"). For supported keys see translator.
        :type mode: str, bool
        :raises KeyError: Raises if keyword argument "mode" is parsed with invalid values.
        """
        self._value_parser(cmd="startmonitoring", p1=self.translator[mode])

    def calc_max_amp_per_band(self, **kwargs):
        """Method to calculate maximum amplitude per band. For futher information see default settings below. 

        By entering a new value as **kwargs, you are able to change default values, which will be sended.

        Default settings:
        | Type                   | Key | kwargs    | Default value | Action                   |
        | ---------------------- | --------------- | ------------- | ------------------------ |
        | int|Channels           | channel         | Channel #1    | Choose channel buffer    |
        | bool                   | plot            | true          | Creates plot buffer      |
        | bool                   | save            | false         | Creates buffer with data |
        | int|SysAmplitudeTypes  | amplitudetype   | Default       | Calced amplitude type    |

        .. warning:: Check supported datatypes and range manually, as a automatic overproof is not provided yet.
        :param user_dict: Possibility to parse your own dictionary instead of editing the default one, defaults to None
        :type user_dict: Dict, optional
        :raises ValueError: Parsed key or related value is not supported.
        """

        # command to build for analyzer
        settings = {'cmd': "calcmaxamplitude", 'channel': Channels.CHANNEL_1,
                    'plot': True,
                    'save': False,
                    'amplitudetype': SysAmplitudesType.AMPLITUDE_DEFAULT
                    }
        # Check for right kwargs keys
        if kwargs:
            if kwargs.keys() not in settings.keys():
                self.logger.error(
                    "Choosen settings key is not supported in this method.")
                raise ValueError(
                    "Choosen settings key is not supported in this method.")
            settings.update(kwargs)
            self.logger.info(
                f"Updated settings to {kwargs.items()}")
        response_dict = self._value_parser(**settings)
        # extract important information
        max_amp = response_dict.get("p1")

        return np.fromstring(max_amp, sep=',')

    def load_test_project(self) -> None:
        """ Loads the set test project.
        """
        self._value_parser(cmd="loadtestproject")

    def load_last_user_project(self) -> None:
        """ Load last user project before a test project was loaded.

        .. warning:: To use this a test project must be laoded before!!!
        .. note:: If no testproject was laoded beforehand, name_variable in analyzer software will be not addressed and 
        a new project without name!(="") will be created. Once a project like this exist, analyzer cannot perform this action gainst 
        and without laoding a test project beforehand, function will do nothing.
        """
        self._value_parser(cmd="loaduserproject")

    def get_measure_positions(self) -> Dict:
        """ Gets a dictionary with all measure positions and if used a energy value.

        :return: Measurepositions and their calculated energy value.
        :rtype: Dict
        """
        return self._value_parser(cmd="getmaxmeasurepositions")

    def get_preamp_hardware_info(self, preamp_port):
        """ Returns a string with hadware infos to preamplifier connected to parsed port

        :param preamp_port: Preamp port with connected preampifier
        :type preamp_port: preamp_port or corresponding int value
        :raises KeyError: Raises if parsed variable is no supported preamp port
        :return: Hardware infos about preamplifier
        :rtype: str
        """
        if preamp_port in PreampPorts or preamp_port in range(0, 8):
            preamp_hardware_info = self._value_parser(
                cmd="getpreampinfo", p1=preamp_port)
            return preamp_hardware_info.get('p1')
        else:
            self.logger.error(
                "Choosen preampport is not a analyzer system preamp port.")
            raise KeyError(
                "Choosen preampport is not a analyzer system preamp port.")

    def start_operator_function(self, mode: Union[str, bool] = "start") -> None:
        """_summary_

        :param mode: Function can start or end operator function by changing mode to a stopping key, defaults to "start". For more allowed keys look up translator dict
        :type mode: Union[str, bool], optional
        """
        self._value_parser(cmd="startoperatorfunctionvalues",
                           p1=self.translator[mode])

    def stopp_operator_function(self) -> None:
        """Stop of running operator function
        """
        self._value_parser(cmd="stoppoperatorfunctionvalues")

    def set_serial_number_pending_process(self, serial_number: int) -> None:
        """Setting serial number for next process.

        :param serial_number: Serial number for next process
        :type serial_number: int
        """
        self._value_parser(cmd="setpendingserial", p1=serial_number)

    def set_comment_pending_process(self, comment: str) -> None:
        """Set process comment for pending process.

        :param comment: Comment for next process.
        :type comment: str
        """
        self._value_parser(cmd="setpendingcomment", p1=comment)

    def set_comment_current_process(self, comment: str):
        """ Sets comment for current activatet process.

        Similair to set_proces_comment but as JSON communication Server command.

        :param comment: Process comment to set
        :type comment: str
        """
        self._value_parser(cmd="setcomment", p1=comment, quiet=False)

    def start_operator(self, operator_name: str, operator_command: str) -> None:
        """External start of existing operator by name.

        :param operator_name: Name of network operator that should start
        :type operator_name: str
        :param operator_command: _description_
        :type operator_command: str
        """
        self._value_parser(cmd="startoperator",
                           p1=operator_name, p2=operator_command, expect_response=False)

    def import_operators(self, operator_fielpath: str, force_load: str) -> None:
        """Import a local file on optimizer.

        :param operator_fielpath: Path to operator file that will be imported.
        :type operator_fielpath: str
        :param force_load: _description_
        :type force_load: str
        """
        self._value_parser(cmd="importoperators",
                           p1=operator_fielpath, p2=force_load, expect_response=False)

    def import_patterns(self, directory_path: str) -> None:
        """Import all pattern files from a optimizer local directory.

        :param directory_path: Directory path to patterns that will be imported.
        :type directory_path: str
        """
        self._value_parser(cmd="importpatterns",
                           p1=directory_path, expect_response=False)

    def start_operator_results(self, mode: Union[str, bool] = "enable") -> None:
        """Sets enable flag to send ot operator results if avaible. Results will be sended separately

        :param mode: Enables start or stops by "disable", defaults to "enable"
        :type mode: str, optional
        """
        self._value_parser(cmd="startoperatorresults",
                           p1=self.translator[mode])

    def stop_operator_results(self) -> None:
        """Sets disable flag to send ot operator results if avaible.
        """
        self._value_parser(cmd="stopoperatorresults")

    def get_io_input(self) -> int:
        """Current set I/O input as integer.

        :return: I/O input register as integer appearance
        :rtype: int
        """
        val = self._value_parser(cmd="readioin")
        return val.get("result")

    def get_io_output(self) -> int:
        """Returns set I/O output as integer appearance of hexa state. 

        :return: Set I/O output
        :rtype: int
        """
        val = self._value_parser(cmd="readioout")
        return val.get("result")

    def _shift_binary(self, original_bin: int) -> str:
        """Helper to invert incomming binaries.

        :param original_bin: Incomming binary
        :type original_bin: int
        :return: Inversed binary
        :rtype: int
        """
        new_val = 0
        new_binary = ""
        for i in range(16):
            bit_state = (original_bin & (1 << i) >> i)
            new_val = new_val | (bit_state << (24-i))

        return new_val

    def _binary_to_hexa(self, binary_str: str):
        deci_num = int(binary_str, 2)
        print(binary_str)
        print(hex(deci_num))

        return hex(deci_num)

    """def invert_hexa(self, hex_num):
        hex_num = hex_num[2:]
        inverted = hex_num[::-1]
        return int("0x" + inverted)
        # sorting = [0,1,6,5,4,3]"""

    def set_simualted_io_input(self, io: str = "0xf0000"):
        """Set simulated I/O input register. I/0 input register can be set by inverted hexa (smallest significant left)
        or by giving in binary representation of set bits in I/O register. I/O register in binary should be parsed like real analyzer setting.

        First 8 digits are first I/O input register
        Second 8 digits are second I/O input register
        Give in all inputs as strings only!
        "00000000 00000000" = "0xf0000"
        "10000000 00000000" = "0xf0001"
        "01000000 00000000" = "0xf0002"
        "11000000 00000000" = "0xf0003"
        "00100000 00000000" = "0xf0004"
        "10100000 00000000" = "0xf0005"
        "01100000 00000000" = "0xf0006"
        "11100000 00000000" = "0xf0007"
        "00010000 00000000" = "0xf0008"
        "10010000 00000000" = "0xf0009"
        "01010000 00000000" = "0xf000A"
        "11010000 00000000" = "0xf000B"
        "00110000 00000000" = "0xf000C"
        "10110000 00000000" = "0xf000D"
        "01110000 00000000" = "0xf000E"
        "11110000 00000000" = "0xf000F"

        "10001000 00000000" = "0xf0011"
        ...

        :param io: Combination on bits set to I/O input register (one and two), defaults to "0xf0000". For further informations see extended summary.
        :type io: int
        """
        if len(io) == 17:  # binary case
            self.logger.error("Binary appearance is not supported yet")
            raise Exception("Developer Error")
            # io = io.replace(" ", "")  # delete space
            # shift binary from smallest significant left (analyzer) to right
            #io = self.shift_binary(int(io))
            # formate binary to hexa
            #io = self.binary_to_hexa(io)

        self._value_parser(cmd="setsimioin",
                           p1=io)

    def add_io_report_callback(self, callback) -> None:
        """Add callback function to report of I/O register. Everytime I/O register changes, added callback functions will be executed. See networking_example.py for an example.
        By adding first callback the report start automatically und will be stopped by removing all callbacks due to remove function.

        .. warning:: All callbacks need as first param "result" to catch analyzer response, if used or not.
        ..see also:: remove_io_report_callback
        :param callback: Added callback function when report happens.
        :type callback: function
        """
        if self._io_report_count == 0:
            self._value_parser(user_callback=callback, cmd="reportio",
                               p1="true")
        else:
            self.__recv_thread.register_callbacks("responsereportio", callback)
        self._io_report_count += 1
        self.logger.info(f"Callback {callback} for I/O report added")

    def remove_io_report_callback(self, callback) -> None:
        """Removes specific callback function from I/O report callback list. 
        By removing all callbacks the report function will be automatically stopped.

        ..see also:: add_io_report_callback
        :param callback: Callback function that should be removed from I/O report functionallities.
        :type callback: function
        """
        self.__recv_thread.deregister_callbacks(
            self._recognition_translator("reportio"), callback)
        self._io_report_count -= 1
        self.logger.info(f"Callback {callback} for I/O report removed")
        if self._io_report_count == 0:
            self._value_parser(cmd="reportio",
                               p1="false")
            self.logger.info("I/O report stopped")

    def add_process_number_report_callback(self, callback):
        """Add callback function to report of process number. Everytime the process number changes, added callback functions will be executed. See networking_example.py for an example.
        By adding first callback the report start automatically und will be stopped by removing all callbacks due to remove function.

        .. warning:: All callbacks need as first param "result" to catch analyzer response, if used or not.
        ..see also:: remove_process_number_report_callback
        :param callback: Added callback function when report happens.
        :type callback: function
        """
        if self._proc_report_count == 0:
            self._value_parser(user_callback=callback, cmd="reportprocessnumber",
                               p1="true")
        else:
            self.__recv_thread.register_callbacks(
                "responsereportprocessnumber", callback)
        self._proc_report_count += 1
        self.logger.info(
            f"Callback {callback} for process number report added")

    def remove_process_number_report_callback(self, callback):
        """Removes specific callback function from process number report callback list. 
        By removing all callbacks the report function will be automatically stopped.

        ..see also:: add_io_report_callback
        :param callback: Callback function that should be removed from process number report functionallities.
        :type callback: function
        """
        self.__recv_thread.deregister_callbacks(
            "responsereportprocessnumber", callback)
        self._proc_report_count -= 1
        self.logger.info(
            f"Callback {callback} for process number report removed")
        if self._proc_report_count == 0:
            self._value_parser(cmd="reportprocessnumber",
                               p1="false")
            self.logger.info("Report of process number stopped.")

    def start_script_function(self, function_name: str, function_param: any):
        """ Start script function and return result.

        :param function_name: Name of script function
        :type function_name: str
        :param function_param: Passed param to script function
        :type function_param: any
        :return: Result of addressed function.
        :rtype: str
        """
        self._value_parser(cmd="appfunc",
                           p1=function_name, p2=function_param)
    # def human_cofirmation --> expect_response=False

    def write_to_database(self, result: any, comment: str):
        self._value_parser(cmd="appfunc",
                           p1=function_name, p2=function_param)

    def _recognition_translator(self, cmd_recognition: str):
        return "response" + cmd_recognition

    def _check_response(self, response):
        # rais exception if not performed right
        if response.get("ok") == False:
            self.logger.error(
                "Analyzer could not perform action: check log and documentation.")
            raise Exception(
                "Analyzer could not perform action:: check log and documentation.")

    def _send(self, command: Dict) -> Dict:
        # print every sended command
        self.logger.info(f"Sended command:{command}")
        # prepare command
        cmd_str = json.dumps(command).encode()
        cmd_str = (len(cmd_str)).to_bytes(2, 'big') + cmd_str
        # actual sending command
        self.s.sendall(cmd_str)

    def _value_parser(self, expect_response=True, user_callback=None, **kwargs) -> Dict:
        """Function to coordinate sending parsed command settings and take back answer from receiver thread.

        By kwargs specification of each command will be set.

        :param expect_response: Flag to not wait for analyzer response, defaults to True
        :type expect_response: bool, optional
        :return: Analyzer response
        :rtype: dict
        """
        # adding msgid
        self.msgid += 1

        # command ground structure
        command = {'cmd': "",
                   "msgid": self.msgid}
        # specify final command
        command.update(kwargs)
        # decide which recognition should be used, if possible use msgid
        if command['cmd'] == "AppCmd":
            recognition = self.msgid
        else:
            recognition = self._recognition_translator(command['cmd'])
        # register callback before sending
        if expect_response and user_callback == None:
            q = queue.Queue()
            def callback(result, queue_var=q): return queue_var.put(result)
            self.__recv_thread.register_callbacks(recognition, callback)
        elif expect_response:
            self.__recv_thread.register_callbacks(
                recognition, user_callback)
        # send command
        self._send(command)

        # receive response
        if expect_response and user_callback == None:
            # get resonse out of queue
            analyzer_response = q.get()
            # deregister callback
            self.__recv_thread.deregister_callbacks(recognition)
            # check response for failure
            self._check_response(analyzer_response)
            return analyzer_response


with AnalyzerCmd(ip="192.168.2.67") as opti:
    opti.set_area_time_range(1, 5, 2)
