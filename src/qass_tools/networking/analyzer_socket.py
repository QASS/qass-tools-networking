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
    def __init__(self, socket, group=None, target=None, name=None, args=()):
        threading.Thread.__init__(self, group, target, name, args)
        self.return_value = "Receiver thread is now killed."
        self.lock = threading.RLock()
        self.__callbacks = {}
        self.s = socket

    def register_callback(self, msg_id, callback):
        with self.lock:
            self.__callbacks[msg_id] = callback

    def deregister_callbacks(self, msg_id):
        pass

    def handle_response(self, response):
        if 'msgid' in response:
            with self.lock:
                if response['msgid'] in self.__callbacks:
                    self.__callbacks[response['msgid']](response)

    def run(self):
        current_len = None
        buffer = ""
        READ_SIZE = 5
        self.kill = False
        while not self.kill:
            buffer += self.s.recv(READ_SIZE)
            while len(buffer) > current_len or (current_len is None and len(buffer) >= 2):
                if current_len is None:
                    current_len = int.from_bytes(buffer[:2], byteorder='big')
                    buffer = buffer[2:]

                if len(buffer) >= current_len:
                    response = buffer[:current_len]
                    self.handle_response(response)
                    buffer = buffer[current_len:]
                    current_len = None

    def kill_thread(self):
        self.daemon = True
        self.kill = True
        self.join()
        # return self.return_value


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
        self.__recv_thread = ReceiveThread(self.s,
                                           group=None, target=None, name="receive thread")
        self.__recv_thread.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        time.sleep(2.0)
        self.__recv_thread.kill_thread
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

    def set_area_view(self, area_type) -> None:
        self._value_parser(
            cmd="AppCmd", p1="setprocesscomment", p2=SysAreaViews.View_1)

    def save_area_view(self, tempalte_num: int) -> None:
        self._value_parser(
            cmd="AppCmd", p1="SaveAreaView", p2=tempalte_num)

    def load_area_view(self, tempalte_num: int) -> None:
        self._value_parser(
            cmd="AppCmd", p1="LoadAreaView", p2=tempalte_num)

    def load_simualtion_buffer(self, file_path: str, channel=Channels.CHANNEL_1) -> None:
        self._value_parser(cmd="AppCmd",
                           p1="SimulationBuffer", p2=f"{channel} {file_path}")

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

    def frequency_test(self, kind, input="channel"):
        """External 50 kHz sine signal frequency test. Only avaible for exisiting ports and sensors.

        setting keys:
        | Type   | Keys                | Meaning                          |
        |--------|---------------------|----------------------------------|
        | kind   | "number of channel" | Channel is choosen for pulsetest |
        | kind   | "number of port"    | Port is choosen for pulsetest    |
        | input  | "channel"           | Channel is choosen for pulsetest |
        | input  | "port"              | Port is choosen for pulsetest    |

        :param kind: Used port/channel number to test.
        :type kind: Port/Channel number
        :param input: What to test. Either channel or port, defaults to "channel"
        :type input: str, optional
        :raises KeyError: If input for frequency test is not choosen to be "channel" or "port".
        """
        if input == "channel":
            kind += 1
            self._value_parser(cmd="AppCmd",
                               p1="Preamp", p2=f"channel {kind} frqtest")
        elif input == "port":
            kind += 1
            self._value_parser(cmd="AppCmd",
                               p1="Preamp", p2=f"port {kind} frqtest")
        else:
            self.logger.error(
                "Only a choosen channel or a port can be tested. Check your key.")
            raise KeyError(
                "Only a choosen channel or a port can be tested. Check your key.")

    def pulse_test(self, kind, input="channel", **kwargs) -> None:
        """External set of pulse test. Only avaible for exisiting ports and sensors.

        setting keys:
        | Type   | Keys                | Meaning                          |
        |--------|---------------------|----------------------------------|
        | kind   | "number of channel" | Channel is choosen for pulsetest |
        | kind   | "number of port"    | Port is choosen for pulsetest    |
        | input  | "channel"           | Channel is choosen for pulsetest |
        | input  | "port"              | Port is choosen for pulsetest    |
        | ------------------------- kwargs ------------------------------ |
        | kwargs | gain                | Pulsetest gain in range(0,4096)  |
        | kwargs | count               | Pulsetest count in range(0,200)  |
        | kwargs | delay               | Pulsetest delay (geater null)    |

        :param kind: Used port/channel number to test.
        :type kind: Port/Channel number
        :param input: What to test. Either channel or port, defaults to "channel"
        :type input: str, optional
        :raises ValueError: If gain is out of bound: range(0,4096)
        :raises ValueError: If count is out of bound: range(0,200)
        :raises ValueError: If delay is out of bound: smaller zero
        :raises KeyError: If input for pulsetest is not choosen to be "channel" or "port".
        """
        if "gain" in kwargs:
            if not (0 < kwargs["gain"] < 4095):
                self.logger.error(
                    "Choosen pulsetest gain is not avaible. The gain should be in range of 0 to 4095.")
                raise ValueError(
                    "Choosen pulsetest gain is not avaible. The gain should be in range of 0 to 4095.")
            else:
                gain = kwargs["gain"]
        else:
            gain = 800
        if "count" in kwargs:
            if kwargs["count"] > 200 or kwargs["count"] < 0:
                self.logger.error(
                    "Choosen pulsetest count is not avaible. The gain should be in range of 0 to 200.")
                raise ValueError(
                    "Choosen pulsetest count is not avaible. The gain should be in range of 0 to 200.")
            else:
                count = kwargs["count"]
        else:
            count = 1
        if "delay" in kwargs:
            if kwargs["delay"] < 0:
                self.logger.error(
                    "Choosen pulsetest delay is not avaible. The delay should be equal or greater null.")
                raise ValueError(
                    "Choosen pulsetest delay is not avaible. The delay should be equal or greater null.")
            else:
                delay = kwargs["delay"]
        else:
            delay = 0

        if input == "channel":
            kind += 1
            self._value_parser(cmd="AppCmd",
                               p1="Preamp", p2=f"channel {kind} pulse {gain} {count} {delay}")
        elif input == "port":
            kind += 1
            self._value_parser(cmd="AppCmd",
                               p1="Preamp", p2=f"port {kind} pulse {gain} {count} {delay}")
        else:
            self.logger.error(
                "Only a choosen channel or a port can be tested. Check your key.")
            raise KeyError(
                "Only a choosen channel or a port can be tested. Check your key.")

    def set_area_scale(self, area_number, scale=500) -> None:
        if scale in range(10, 1001):
            self._value_parser(cmd="AppCmd",
                               p1="SetAreaScale", p2=f"{area_number} {scale}")
        else:
            self.logger.error(
                "Choosen scale is out of bounds. Should be in range(10,1001).")
            raise ValueError(
                "Choosen scale is out of bounds. Should be in range(10,1001).")

    def set_app_var(self, app_var_name: str, app_var_value: any) -> None:
        """Parse value to specific AppVar operator in operator network of analyzer.

        There has to be an already existing AppVar operator which can accessed by (matching) name.

        :param app_var_name: Name of existing AppVar operator.
        :type app_var_name: str
        :param app_var_value: Value which should be assigned to operator. As value can be choosed any datatyp supported by python (e.g. float, int, str, json, ...).
        :type app_var_value: any
        """

        self._value_parser(cmd="setappvar", p1=app_var_name, p2=app_var_value)

    def set_app_var_appcmd(self, app_var_name: str, value: any) -> None:
        """Parse value to specific AppVar operator in operator network of analyzer.

        An extra method is provided because this method works with an general analyzer AppCommand.

        .. seealso:: set_app_var()

        :param app_var_name: Name of existing AppVar operator.
        :type app_var_name: str
        :param app_var_value: Value which should be assigned to operator. As value can be choosed any datatyp supported by python (e.g. float, int, str, json, ...).
        :type app_var_value: any
        """

        self._value_parser(cmd="AppCmd", p1="SetAppVar",
                           p2=f"{app_var_name} {value}")

    def get_app_var(self, app_var_name: str) -> None:
        """Get value of AppVar by name.

        :param app_var_name: Name of AppVar to adress.
        :type app_var_name: str
        :return: AppVar value
        :rtype: any
        """
        val = self._value_parser(cmd="getappvar", p1=app_var_name)

        return val.get('result')

    def remove_app_var(self, app_var_name: str) -> None:
        """ Clear and remove AppVar by name.

        :param app_var_name: Naem of AppVar to remove.
        :type app_var_name: str
        """
        self._value_parser(cmd="clearappvar", p1=app_var_name)

    def get_app_vars_report(self, mode: Union[bool, str] = "enabled") -> Dict:
        """ Get report about existing AppVars and their changes.

        Return dict contains list of AppVars with name and value, as access time and unixtime.

        :param mode: Can be set to enabled or disabled, defaults to enbaled
        :type mode: bool, str, optional
        :return: AppVar report
        :rtype: Dict
        """

        val = self._value_parser(cmd="reportappvars", p1=self.translator[mode])
        # process response
        val_dict = {"appvar_list": val.get("appvar_list"), "access_time": val.get(
            "appvar_readdate"), "unix_time": val.get("unixtime")}

        return val_dict

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

        Default settings:
        | Type             | Multiplexer     | Value        |
        | ---------------- | ----------------| ------------ |
        | Channels         | channel         | Channel #1   |
        | ChannelPorts     | chp             | Port 1       |
        | PreampPorts      | preampport      | Preampport 1 |
        | Samplerates      | fft             | enabled      |
        | Boolean          | signal          | disabled     |
        | FFTOversampling  | samplerate      | 1600 kHz     |
        | FFTOversampling  | fftoversampling | 8 times      |
        | FFTWindowing     | fftwindowing    | Hanning      |
        | FFTLogarithmic   | fftlogarithmic  | Base 14      |
        | Boolean          | filter          | disabled     |
        | Integer          | gain            | 800          |
        | Integer          | subport         | not used     |

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
                    'gain': "800",
                    'subport': "0"
                    }
        # gain limit 5000
        # if kwargs:
        #    if kwargs.keys() in [*settings.keys()]:
        #        pass
        #    else:
        #        self.logger.error("Choosen seeting is not avaible in multiplexer")
        #        raise KeyError("Choosen seeting is not avaible in multiplexer")
        settings.update(kwargs)
        self._value_parser(settings)

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
        """Start or stop monitoring modus.

        Short settings:
        | Measuring mode    | Key       |
        | ----------------- | --------- |
        | start monitoring  | "true"    |
        | stop monitoring   | "false"   |

        :param mode: Switch between start monitoring ("true") or stop monitoring  ("false"). For supported keys see translator.
        :type mode: str, bool
        :raises KeyError: Raises if keyword argument "mode" is parsed with invalid values.
        """
        self._value_parser(cmd="startmonitoring", p1=self.translator[mode])

    def calc_max_amp_per_band(self, **kwargs):
        """Method to calculate maximum amplitude per band. 

        By entering a new value as **kwargs, you are able to change default values, which will be sended.

        Default settings:
        | Type | Key | kwargs    | Default value | Action                   |
        | ---- | --------------- | ------------- | ------------------------ |
        | int  | channel         | Channel #1    | Choose channel buffer    |
        | bool | plot            | true          | Creates plot buffer      |
        | bool | save            | false         | Creates buffer with data |
        | int  | amplitudetype   | Default       | Type calced of amplitude |

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
        for kwarg in kwargs.keys():
            if kwarg not in settings.keys():
                self.logger.error(
                    "Choosen settings key is not supported in this method.")
                raise ValueError(
                    "Choosen settings key is not supported in this method.")
            if kwarg == "amplitudetype" and kwargs[kwarg] not in SysAmplitudesType:
                self.logger.error(
                    "Choosen amplitudetype is not a analyzer system aplitude type.")
                raise ValueError(
                    "Choosen amplitudetype is not a analyzer system aplitude type.")

        settings.update(kwargs)
        self.logger.info(
            f"Updated settings to {kwargs.items()}")
        response_dict = self._value_parser(**settings)
        # extract important information
        max_amp = response_dict.get("p1")

        return np.fromstring(max_amp, sep=',')

    def load_test_project(self):
        command = {'cmd': "loadtestproject", "msgid": self.msgid}
        response = self._send(command)
        return self._handle_commserver_response(response)

    def load_last_user_project(self):
        command = {'cmd': "loaduserproject", "msgid": self.msgid}
        response = self._send(command)
        return self._handle_commserver_response(response)

    def get_max_measure_positions(self) -> Dict:
        """_summary_

        :return: Measurepositions and calculated energy value.
        :rtype: Dict
        """
        return self._value_parser(cmd="getmaxmeasurepositions")

    # TODO: Source code or peter ---'t:2023;sn:980;s:1;'
    def get_preamp_settings(self, preampport: PreampPorts):
        """_summary_

        _extended_summary_

        :param preampport: _description_
        :type preampport: PreampPorts
        :raises KeyError: Raises if parsed variable is no PreampPorts enum
        :return: _description_
        :rtype: _type_
        """
        if preampport in PreampPorts:
            return self._value_parser(cmd="getpreampinfo", p1=preampport)
        else:
            self.logger.error(
                "Choosen preampport is not a analyzer system preampport.")
            raise KeyError(
                "Choosen preampport is not a analyzer system preampport.")

    def start_operator_function(self, mode: Union[str, bool] = "enabled") -> None:
        """_summary_

        :param mode: Mode if start is enabled., defaults to "enabled"
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

    # TODO:understand command
    def start_operator(self, operator_name: str, operator_command: str) -> None:
        """External start of existing operator by name.

        :param operator_name: Name of network operator that should start
        :type operator_name: str
        :param operator_command: _description_
        :type operator_command: str
        """
        self._value_parser(cmd="startoperator",
                           p1=operator_name, p2=operator_command)

    def import_operators(self, operator_fielpath: str, force_load: str) -> None:
        """Import a local file on optimizer.

        :param operator_fielpath: Path to operator file that will be imported.
        :type operator_fielpath: str
        :param force_load: _description_
        :type force_load: str
        """
        self._value_parser(cmd="importoperators",
                           p1=operator_fielpath, p2=force_load)

    def import_patterns(self, directory_path: str) -> None:
        """Import all pattern files from a optimizer local directory.

        :param directory_path: Directory path to patterns that will be imported.
        :type directory_path: str
        """
        self._value_parser(cmd="importpatterns",
                           p1=directory_path)

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

    def shift_binary(self, original_bin: str) -> str:
        """Helper to shift binary strings (partwise).

        :param binary_part: binary string
        :type binary_part: str
        :param shift: Shifted chars in string as a loop of string size, defaults to 3
        :type shift: int, optional
        :return: Shifted binary string
        :rtype: str
        """
        old_val = original_bin

        new_val = 0

        for i in range(24):
            bit_state = (old_val & (1 << i) >> i)
            new_val = new_val | (bit_state << (24-i))

        # generic solution
        shifted_idx_list = []
        dig_list = list(binary_part)

        # find shifting idx
        for idx in range(0, len(binary_part)):
            shift_idx = idx + shift
            if shift_idx > len(binary_part)-1:
                shift_idx = shift_idx - len(binary_part)
            shifted_idx_list.append(shift_idx)

        # zip and sort
        zipped = zip(dig_list, shifted_idx_list)
        sorted_list = sorted(zipped, key=lambda x: x[1])
        shifted_list, _ = zip(*sorted_list)

        # join shifted digs
        shifted_part = "".join(shifted_list)

        # hardcoded solution
        # shifted_part = binary_part[3] + \
        #    binary_part[0] + binary_part[1] + binary_part[2]

        return shifted_part

    def binary_to_hexa(self, binary_str: str):
        if "_" in binary_str:
            shifted_binary = ""
            binary_list = binary_str.split("_")
            for (idx, binary_group) in enumerate(binary_list):
                shifted_binary_group = self.shift_binary(binary_group)
                binary_list[idx] = shifted_binary_group
            new_bin = "".join(binary_list)
        else:
            pass
        # "0000_0000_0000_0000"
        # "0000000000000000"

        deci_num = int(new_bin, 2)
        print(binary_str)
        print(new_bin)
        print(hex(deci_num))

        return self.invert_hexa(hex(deci_num))

    def invert_hexa(self, hex_num):
        hex_num = hex_num[2:]
        inverted = hex_num[::-1]
        return "0x" + inverted
        # sorting = [0,1,6,5,4,3]

    def deci_to_binary():
        pass

    def set_simualted_io_input(self, io: str):
        """Set simulated I/O input register. Seting rule based on hexa.

        IO_0000_0000_0000_0000 = "0xf0000"
        IO_1000_0000_0000_0000 = "0xf0001"
        IO_0100_0000_0000_0000 = "0xf0002"
        IO_1100_0000_0000_0000 = "0xf0003"
        IO_0010_0000_0000_0000 = "0xf0004"
        IO_1010_0000_0000_0000 = "0xf0005"
        IO_0110_0000_0000_0000 = "0xf0006"
        IO_1110_0000_0000_0000 = "0xf0007"
        IO_0001_0000_0000_0000 = "0xf0008"
        IO_1001_0000_0000_0000 = "0xf0009"
        IO_0101_0000_0000_0000 = "0xf000A"
        IO_1101_0000_0000_0000 = "0xf000B"
        IO_0011_0000_0000_0000 = "0xf000C"
        IO_1011_0000_0000_0000 = "0xf000D"
        IO_0111_0000_0000_0000 = "0xf000E"
        IO_1111_0000_0000_0000 = "0xf000F"

        IO_1000_1000_0000_0000 = "0xf0011"
        ...

        :param io: Combination on set I/Os register, defaults to "0xf0000"
        :type io: str
        """
        hexa = self.binary_to_hexa(io)
        self._value_parser(cmd="setsimioin",
                           p1=hexa)

    def set_io_report(self, mode: Union[str, bool]):
        """Switches I/O register report on or off.

        :param mode: Switch report to on (True) or off (False)
        :type mode: bool, str
        :return: standardized analyzer respond
        :rtype: dict
        """
        self._value_parser(cmd="reportio",
                           p1=self.translator[mode])

    def set_process_number_report(self, mode: Union[str, bool]):
        """Switches process number report on or off.

        :param mode: Switch report to on ("enable") or off ("disable"). For supported keys see translator.
        :type mode: bool, str
        :return: standardized analyzer response
        :rtype: dict
        """
        self._value_parser(cmd="reportprocessnumber",
                           p1=self.translator[mode])

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

    """def _handle_appcmd_response(self, response):
        self.logger.debug(response)
        # change appearance
        response = response.decode("utf-8")  # utf-8 decode type
        response = json.loads(response[2:])

        self._check_response(response)"""

    def _handle_response(self, response, encoding_style="utf-8"):
        self.logger.debug(response)
        # change appearance
        response = response[2:].decode(encoding_style)  # utf-8 decode type
        response = json.loads(response)
        self._check_response(response)
        # if expect_return:
        #    return response
        return response

    def _check_response(self, response):
        # rais exception if not performed right
        if response.get("ok") == False:
            self.logger.error(
                "Analyzer could not perform action: check log and documentation.")
            raise Exception(
                "Analyzer could not perform action:: check log and documentation.")

    """def _handle_commserver_response(self, response) -> Dict:
        self.logger.debug(response)
        response = response[2:].decode()
        response = json.loads(response)
        print("response length:", len(str(response)))

        self._check_response(response)
        return response"""

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

    def _thread_listening(self):
        timeout = False
        storage_buffer = ctypes.create_unicode_buffer(1)
        while not timeout:
            self.s.recv_into(storage_buffer)
            buff = storage_buffer.value
            print(buff)
            analyzer_response = buff

            # stop conditions
            if analyzer_response:
                return analyzer_response
            # if first message is received listen one round more if analayzer sends more
            if int.from_bytes(buff, byteorder="big") == 1:
                timeout = True
            else:
                timeout = False
        return analyzer_response

    def _receive(self):
        self.rarth.start()
        return self.rarth.thread_return()

    """def _receive(self):
        resp = self.s.recv(4096)
        print(resp)
        length = resp[:2]
        length = int.from_bytes(length, byteorder="big")
        print(length)
        return resp
    """

    def _value_parser(self, expect_response=True, **kwargs):
        if expect_response:
            queue = Queue()
            def callback(result, queue=queue): return queue.put(result)
            self._receiver_thread.registerCallback(self.msgid, callback)

        # command ground structure
        command = {'cmd': "",
                   "msgid": self.msgid}
        # specify final command
        command.update(kwargs)
        # send command
        self._send(command)

        if expect_response:
            result = queue.get()
            analyzer_response = self._receive()
            # handle response
            return self._handle_response(analyzer_response)


with AnalyzerCmd("192.168.2.67", debug_mode=True) as opti:
    proc_val = opti.get_process_number()
    print(proc_val)
