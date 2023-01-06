import socket
import json
import numpy as np
import time
from enum import Enum, IntEnum
from typing import Any, Dict, List, Union
import logging
import sys
import threading
import queue
from collections import defaultdict
from retry import retry
import warnings


class Amplitudes(Enum):
    """ Enum class to list and check available amplitudes in mV to generate sine wave."""
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
        """Property lists all allowed amplitudes to generate sine wave from.

        :rtype: List
        """
        return list(Amplitudes)


class Channels(IntEnum):
    """Available selection box choices for channel in multiplexer configuration that will be addressed"""
    CHANNEL_1 = 0
    CHANNEL_2 = 1
    CHANNEL_3 = 2
    CHANNEL_4 = 3


class ChannelPorts(IntEnum):
    """Available selection box choices for channel port in multiplexer configuration that will be addressed"""
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
    """Available selection box choices for preamplifier port in multiplexer configuration that will be addressed"""
    PREAMP_PORT_1 = 0
    PREAMP_PORT_2 = 1
    PREAMP_PORT_3 = 2
    PREAMP_PORT_4 = 3
    PREAMP_PORT_5 = 4
    PREAMP_PORT_6 = 5
    PREAMP_PORT_7 = 6
    PREAMP_PORT_8 = 7


class Samplerates16Bit(IntEnum):
    """Available selection box choices for used samplerate in multiplexer configuration"""
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


class ExactSamplerates16Bit(IntEnum):
    """Available exact samplerates in Hz with 16 Bit ADC.

    .. warning:: These values are just for calculations and cannot be used within AnalyzerRemote functions"""
    SAMPLERATE_100_MHz = 100000e3
    SAMPLERATE_50_MHz = 50000e3
    SAMPLERATE_25_MHz = 25000e3
    SAMPLERATE_12_MHz = 12500e3
    SAMPLERATE_6_MHz = 6250e3
    SAMPLERATE_3_MHz = 3125e3
    SAMPLERATE_1600_kHz = 1562.5e3
    SAMPLERATE_800_kHz = 781.25e3
    SAMPLERATE_400_kHz = 390.63e3
    SAMPLERATE_200_kHz = 195.31e3
    SAMPLERATE_100_kHz = 97.66e3


class ExactSamplerates24Bit(IntEnum):
    """Available exact samplerates in Hz with 24 Bit ADC.

    .. warning:: These values are just for calculations and cannot be used within AnalyzerRemote functions"""
    SAMPLERATE_4_MHz = 4000e3
    SAMPLERATE_2_MHz = 2000e3
    SAMPLERATE_1_MHz = 1000e3
    SAMPLERATE_500_kHz = 500e3
    SAMPLERATE_250_kHz = 250e3
    SAMPLERATE_125_kHz = 125e3
    SAMPLERATE_60_kHz = 160.5e3
    SAMPLERATE_30_kHz = 30.25e3


class FFTOversampling(IntEnum):
    """Available selection box choices for used oversampling in multiplexer configuration"""
    FFT_OVERSAMPLING_2_TIMES = 1
    FFT_OVERSAMPLING_4_TIMES = 2
    FFT_OVERSAMPLING_8_TIMES = 3
    FFT_OVERSAMPLING_16_TIMES = 4
    FFT_OVERSAMPLING_32_TIMES = 5
    FFT_OVERSAMPLING_64_TIMES = 6
    NONE_FFT_OVERSAMPLING = 0


class FFTWindowing(IntEnum):
    """Available selection box choices for used windowing function in multiplexer configuration"""
    FFT_WINDOWING_HANNING = 0
    NONE_FFT_WINDOWING = 1


class FFTLogarithmic(IntEnum):
    """Available selection box choices for displayed FFT logarithmic base in multiplexer configuration"""
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
    """System amplitude types available in analyzer software. Helps to represent calculated
    maximum amplitudes in different styles."""
    AMPLITUDE_DEFAULT = 0
    # Amplitude is original ADC output value from hardware
    AMPLITUDE_ADC_OUT = 1
    # Amplitude is normalized energy value. (timedif x frqdif x normalized amplitude)
    AMPLITUDE_NORM_ENERGY = 2
    # Amplitude normalized to 1 as full ADC value:
    AMPLITUDE_NORM_ONE = 3
    AMPLITUDE_MILLI_VOLT = 4
    AMPLITUDE_MICRO_VOLT = 5


class AreaViews(IntEnum):
    """ Available view possibilities in analyzer area view."""
    View_1 = 1
    View_2 = 2
    View_3 = 3
    View_4 = 4


class SysSettingsClass(IntEnum):
    """ Predefined system settings classes."""
    NO_CLASS = 0 	# Wird zur Zeit auch per Voreinstellung in "./config/QASS/analyzer.conf" gespeichert
    # Das ist die Default-Klasse für pVars, die in einem VarSet untergebracht sind
    VAR_SET_CLASS = 1
    # Die Variable enthält System-Einstellungen, die später auch in ".config/QASS" gespeichert werden
    SYSTEM_CONFIG = 2
    USER_CONFIG = 3     # Wird in "./config/QASS/analyzer.conf" in der USER Sektion gespeichert
    GLOBAL_TRIGGER_CONFIG = 4     # Globale Triggereinstellung
    GLOBAL_MEASURE_CONFIG = 5     # Globale MeasureConfig Einstellung
    MEASURE_CONFIG = 6     # MeasureConfig Struktur
    CLIENT_CONFIG = 7     # Branding und application Start Einstellungen
    VIDEO_CONFIG = 8     # This is a configuration Setting for a CAM or VideoRecording
    COLOR_CONFIG = 9
    NETWORK_CONFIG = 10    # A network configuration
    FPGA_CONFIG = 11
    PR_SEARCH_CONFIG = 12
    GUI_CONFIG = 13    # global GUI and StyleSheet settings
    SIM_BUFFER_CONFIG = 14    # Configuration of Simulation files
    BACKUP_CONFIG = 15  # Configuration for backups and automatic backups


class MultiPreampInput(IntEnum):
    """ Enums for Multi Input Preamps. The numeration starts on the uppest left input and goes rowise from left to right, too the lowest input (right side)."""
    NONE_MULTI_INPUT = 999  # Just a flag, to not use any input values
    MULTI_INPUT_1 = 0
    MULTI_INPUT_2 = 1
    MULTI_INPUT_3 = 2
    MULTI_INPUT_4 = 3
    MULTI_INPUT_5 = 4
    MULTI_INPUT_6 = 6


class ConnectionError(socket.error):
    def __init__(self, ip, port):
        self.msg = f"Connection to ip: {ip} on port: {port} could not be established.\n"

    def __str__(self):
        return self.msg


class NoneRegistrationError(Exception):
    """ Error is raised if programm cannot find a registered callback for a command. When this exception occurs, programm run into failstate."""
    pass


class AnalyzerSyntaxError(Exception):
    """ Error is raised if analyzer sends a 'not okay' command back which means that sended command syntax is not supported in this way."""
    pass


class ReceiveThread(threading.Thread):
    """ Receiving thread which runs due to contextmanager the whole time and listens to analyzer socket for responses.
    Responses will be processed and parsed to a callback function (regular: adds response to queue for main thread to fetch te data."""

    def __init__(self, socket_obj, logger_obj, group=None, target=None, name=None, args=()):
        threading.Thread.__init__(self, group, target, name, args)
        self.lock = threading.RLock()
        self.__callbacks = defaultdict(list)
        self.s = socket_obj
        self.logger = logger_obj

    def warn_none_registered_response(self, message):
        """ Warning is used when a not expected or not registered message comes in from analyzer. A warning is send out and the message will be logged."""
        new_message = "Not registered analyzer response:" + str(message)
        self.logger.warning(new_message)
        # warnings.warn(new_message)

    def register_callbacks(self, recognition: Union[str, int], callback) -> None:
        """ Function to register incoming analyzer response by msg_id or cmd name.
        Parsed callback will be registered by adding it as recognition-callback pair to a dict self.__callbacks.


        A MultiDict is used here which by default creates a list for every dict entry (basically a key-list-pair).
        So it is possible to store mutiple callbacks for one recognition.

        :param recognition: Recognition to identify message.
        :type recognition: str, int
        :param callback: Callback to handle response value. Receives the response as an argument.
        :type callback: function
        """
        with self.lock:
            self.__callbacks[recognition].append(callback)

    def deregister_callbacks(self, recognition: Union[str, int], user_callback=None) -> None:
        """ Remove registered callback.

        Due to the used MultiDict we have to check if only one callback has to be removed or the complete entry.

        :param recognition: Recognition to identify message.
        :type recognition: str, int
        :param user_callback: Deregister , defaults to None
        :type user_callback: function, optional
        """
        with self.lock:
            if user_callback:
                self.__callbacks[recognition].remove(user_callback)
                if len(self.__callbacks[recognition]) == 0:
                    self.__callbacks.pop(recognition)
            else:
                self.__callbacks.pop(recognition)

    def handle_response(self, response, encoding_style="utf-8") -> None:
        """Handles every complete message. Handling means decoding the byte string to dict and apply the response to every registered callback.
        Therefore the response is not in unit form, we need an if block which handles recognition over cmd name and message id

        :param response: Complete analyzer response
        :type response: bytes string
        :param encoding_style: Encoding style used from Json module, defaults to "utf-8"
        :type encoding_style: str, optional
        """
        self.logger.debug(response)
        # change appearance
        response = response.decode(encoding_style)
        response = json.loads(response)

        # handle cases
        with self.lock:
            # case start_operator: sends a second message which has no cmd entry
            if "cmd" not in response.keys():
                if "operator" in response.keys() and "finished" in response.keys():
                    self.__callbacks[response["operator"]][0](response)
                    self.deregister_callbacks(response["operator"])
                return
            # reports always use their cmd name as recognition
            elif response['cmd'] in self.__callbacks:
                # reports alwys registered with cmd->only case we need to check for mutiple callbacks
                length = len(self.__callbacks[response['cmd']])
                for idx in range(0, length):
                    self.__callbacks[response['cmd']][idx](response)
            # if no report there is only one entry--> [0] always uses right callback
            # case resid
            elif 'resid' in response:
                if response['resid'] in self.__callbacks:
                    self.__callbacks[response['resid']][0](response)
            # case msgid
            elif 'msgid' in response:
                if response['msgid'] in self.__callbacks:
                    self.__callbacks[response['msgid']][0](response)
            # incooming messages wich are not registered will be just logged as warning
            else:
                self.warn_none_registered_response(response)

    def run(self) -> None:
        """ Overriden run method of thread module will be executed as the thread starts.

        Method listens to socket in forever loop 'till kill_thread method is executed. Listens for small parts and puts messages together.
        If complete, messsage is parsed it is forwarded to the handle_response method.
        """
        current_len = 0
        buffer = bytearray()
        READ_SIZE = 4
        self.kill = False
        while not self.kill:
            try:
                buffer.extend(self.s.recv(READ_SIZE))
            # if nothing is received, socket runs into failstate (socket.timeout)
            except socket.timeout as e:
                # if len(self.__callbacks) != 0:
                continue
                # else:
                #    self.logger.error(
                #        "No signal received altough signal is expected. Programm stopps.")
                #    raise e
            # catch other socket exception and crash
            except socket.error as e:
                self.logger.error(e)
                if int.from_bytes(buffer, byteorder='big') > 0:
                    self.logger.warning("Unfinished message received:\n")
                    self.logger.warning(buffer)
                    raise e
            # only enter for new current length setting or if message is complete
            while (len(buffer) >= current_len and len(buffer) != 0) or (current_len is 0 and len(buffer) >= 2):
                if current_len == 0:
                    # every two first characters of a message are the incoming length
                    current_len = int.from_bytes(buffer[:2], byteorder='big')
                    # cut length away
                    buffer = buffer[2:]
                # if message is complete
                if len(buffer) >= current_len:
                    # seperate message
                    response = buffer[:current_len]
                    # handle response
                    self.handle_response(response)
                    # throw ahdnled part away
                    buffer = buffer[current_len:]
                    # reset current_length
                    current_len = 0
                    timeout = 0

    def kill_thread(self) -> None:
        """End forever loop in run method and join thread."""
        # self.daemon = True
        self.kill = True
        self.logger.info("Receiver thread is now killed.")
        self.join()


class AnalyzerRemote():
    """ Class provides methods for external analyzer control (system operator independant) over a TCP socket."""

    def __init__(self, ip: str, port=17000, debug_mode=False):
        """Constructor provides helper and creates logger module .

        :param ip: Analyzer IP in network.
        :type ip: str
        :param port: Required Analyzer port, by the default always 17000.
        :type port: int
        :param debug_mode: Logs debug messages into sys.stdout
        :type debug_mode: bool

        ::Example::
            analyzer = AnalyzerRemote(ip="192.168.2.67", port=17000)
            analyzer = AnalyzerRemote(ip="192.168.2.67")
            analyzer = AnalyzerRemote("192.168.2.67")
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
        # flags for exit method of context manager
        self._io_report_count = 0
        self._proc_report_count = 0
        self._appvar_report_count = 0
        self._measuring_active = False
        self._sine_gen_active = False
        self._monitoring_active = False
        self._operator_functions_active = False

        # short solution logger to sys.stdout
        msg_mode = logging.DEBUG if debug_mode else logging.INFO
        self.logger = self._create_logger(msg_mode)

    def __enter__(self):
        """ Connects the machine to an analyzer reachable over user-given Input of IP (self.ip) and Port (self.port)
        via TCP and returns an instance of the class. Additionally a second thread (called receiving thread) will be started.
        This thread will run until __exit__ method will kill recieve thread.

        :return: Instance of AnalyzerRemote class
        :rtype: AnalyzerRemote object
        """
        # connect to socket
        self._connecting_analyzer()

        # create thread instance
        self.__recv_thread = ReceiveThread(self.s, self.logger,
                                           group=None, target=None, name="receive thread")
        # start thread
        self.__recv_thread.start()
        return self

    def analyzer_functionality_warning_decorator(func):
        def inner(*args, **kwargs):
            result = func(*args, **kwargs)
            warnings.warn(
                "Analyzer provides no complete implementation for this yet.")
            return result
        return inner

    def _create_logger(self, level_mode):
        """Creates a logger which will print out to sys.stdout and log custom message and time, log level,
        function name and if available line number where log occured.

        :param level_mode: logging msg mode (e.g. logging.debug)
        :type level_mode: Message level that will be displayed
        :return: Logger obj
        """
        logging.basicConfig(stream=sys.stdout, level=level_mode,
                            format='[%(asctime)s]  %(levelname)s: %(message)s')
        logger = logging.getLogger()
        return logger

    @retry(ConnectionError, tries=4, delay=1)
    def _connecting_analyzer(self):
        """ Method to create a TCP socket connection with socket address(ip and port) from constructor

        Retry decorator will retry method calls if a ConnectionError occurs. Here set delay layes by 1 second and
        decorator will try again for four times before giving up.

        :raises ConnectionError: Connection error is raisen if no connection can be established.
        """
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.settimeout(15)
            self.s.connect((self.ip, self.port))
            self.logger.info("Connected to optimizer")
        except socket.timeout:
            raise ConnectionError(self.ip, self.port)
        except socket.error:
            raise ConnectionError(self.ip, self.port)
        except KeyboardInterrupt as e:
            print(e)
            self.__exit__(exc_type=e)

    def __exit__(self, exc_type, exc_value, traceback):
        """ If contextmanager is left, another two seconds will be waited before private function is called on the receiving thread
        (start in enter method of contextmanager) and also raise and log errors.
        """
        time.sleep(2.0)

        self.__recv_thread.kill_thread()
        # save exit and stop all running services
        if self._measuring_active:
            self._value_parser(expect_response=False,
                               cmd="App", p1="stopMeasuring")
        if self._sine_gen_active:
            self._value_parser(expect_response=False,
                               cmd="AppCmd", p1="StopSineGen")
        if self._monitoring_active:
            self._value_parser(expect_response=False,
                               cmd="startmonitoring", p1="false")
        if self._operator_functions_active:
            self._value_parser(expect_response=False,
                               cmd="stoppoperatorfunctionvalues")

        self.s.close()
        self.logger.info("Socket connection closed")
        if exc_type != None:
            self.logger.error(
                f"\nExecution type: {exc_type}\nTraceback: {traceback}")

    @property
    def get_socket_ip(self):
        """Property that gives out connected IP.

        :rtype: str
        """
        return self.ip

    @property
    def get_socket_port(self):
        """Property that gives out connected Port.

        :rtype: int
        """
        return self.port

    @property
    def get_measuring_state(self):
        """Property that gives out if measuring has been started remotely.

        :rtype: boolean
        """
        return self._measuring_active

    @property
    def get_monitoring_state(self):
        """Property that gives out if monitoring has been started remotely.

        :rtype: boolean
        """
        return self._monitoring_active

    @property
    def get_sine_gen_state(self):
        """Property that gives out if sine generator has been activated remotely.

        :rtype: boolean
        """
        return self._sine_gen_active

    @property
    def get_operator_functions_state(self):
        """Property that gives out if operator functions has been activated remotely.

        :rtype: boolean
        """
        return self._operator_functions_active

    @property
    def get_translator(self):
        """ Returns supported keys from translator

        :rtype: List
        """
        return self.translator.keys()

    def start_measuring(self) -> None:
        """Method sends a command to the connected analyzer to start a measuring process."""
        self._value_parser(cmd="AppCmd", p1="startMeasuring")
        self._measuring_active = True

    def start_sineGenerator(self, frequency: int, amplitude: Union[int, Amplitudes]) -> None:
        """Method to start sine wave generation with custom frequency and amplitude settings.

        .. warning:: Sine generator has to be already switched on!
        .. note:: Note that you should consider that the sine generator needs a couple µs to start
        .. note:: Reminder: Frequency range is limited by used sine generator

        :param frequency: Used frequency to generate sine wave with in Hz.
        :type frequency: int
        :param amplitude: Used amplitude to generate sine wave in mV. See Amplitudes class for more all supported amplitude values.
        :type amplitude: int, Amplitudes
        :raises ValueError: Set amplitude has to be equal to one class constances of class Amplitudes. If exception is raised the user is asked to enter new amplitude and frequency.
        """
        a = list(Amplitudes)
        try:
            if amplitude in a or amplitude in Amplitudes:
                self._value_parser(
                    cmd="AppCmd", p1="StartSineGen", p2=f"{frequency} {amplitude}")
                self.logger.info(
                    f"Sine generator startet with f={frequency} Hz and {amplitude} mV amplitude.")
                self._sine_gen_active = True
            else:
                raise ValueError
        except ValueError:
            (f" Desired amplitude {amplitude} is not supported. Please enter one of the following amplitudes to continue: {a}")
            NEWamp = input("Enter new sine amplitude:")
            NEWf = input("Enter new sine frequency:")
            self.start_sineGenerator(NEWf, NEWamp)

    def stop_sineGenerator(self) -> None:
        """Stops generating sine waves."""
        self._value_parser(cmd="AppCmd", p1="StopSineGen")

    def stop_measuring(self) -> None:
        """Method to stop a currently running measurement."""
        self._value_parser(cmd="AppCmd", p1="stopMeasuring")
        self._measuring_active = False

    def set_process_comment(self, proc_comm: str) -> None:
        """Set a process comment for the selected process.

        Parsed string will be saved in database under entry: process.comment

        :param proc_comm: Text which should be seen and saved as process comment
        :type proc_comm: str
        """
        self._value_parser(cmd="AppCmd", p1="setprocesscomment", p2=proc_comm)

    def set_area_view(self, split: int) -> None:
        """Set analyzer view to a split view with up to 4 different splitted process. Reversed process to change back to
        single view.

        :param split: Amount of splitted area views. Limited to 4.
        :type split: int
        :raises ValueError: Raises if split lays out of bounds
        """
        if 0 < split <= 4:
            self._value_parser(
                cmd="AppCmd", p1="SetAreaViews", p2=split)
        else:
            self.logger.error("Split amount vor view is out of bounds.")
            raise ValueError("Split amount vor view is out of bounds.")

    def save_area_view(self, template_num: int) -> None:
        """Saves current area view settings under template number. Each template can be set differently.

        :param template_num: Storage number to save.
        :type template_num: int
        """
        self._value_parser(
            cmd="AppCmd", p1="SaveAreaView", p2=template_num)

    def load_area_view(self, template_num: int) -> None:
        """Load presaved (!) area view template.

        :param template_num: Storage number to load.
        :type template_num: int
        """
        self._value_parser(
            cmd="AppCmd", p1="LoadAreaView", p2=template_num)

    def load_simulation_buffer(self, file_path: str, channel: int, do_not_copy_meta_data=False) -> None:
        """Load and set local simulation buffer for specific channel.

        .. warning:: AppCmds are user functions and due to that not null based. Implemented IntEnums are code based and have to be added by one each.

        :param file_path: Local file path to buffer.
        :type file_path: str
        :param channel: Channel where simulationbuffer gets loaded.
        :type channel: int
        :param do_not_copy_meta_data: Identical to analyzer check box, defaults to False
        :type do_not_copy_meta_data: bool, optional
        """

        # AppCmds are user functions and due to that not null based. Implemented IntEnums are code based and have to be added by one each.
        channel += 1
        if do_not_copy_meta_data:
            p2_string = f"channel {channel} nometa path {file_path}"
        else:
            p2_string = f"channel {channel} path {file_path}"
        self._value_parser(cmd="AppCmd", p1="SimulationBuffer", p2=p2_string)

    def set_simulation_buffer(self, channel_number: Union[str, int, ChannelPorts], mode: str) -> None:
        """ Enable or disable already loaded simualtion buffer channel.

        :param channel_number: Channel to activate simualtion buffer on. Beside normal input, key "all" is supported.
        :type channel_number: str or int or ChannelPorts
        :param mode: If channel should be "enabled" or "disabled" as sim buffer. Check Translator dict for more keywords.
        :type mode: str
        """
        if channel_number == "all":
            self._value_parser(cmd="AppCmd",
                               p1="SimulationBuffer", p2=f"path {self.translator[mode]}")
        else:
            channel_number += 1
            self._value_parser(cmd="AppCmd",
                               p1="SimulationBuffer", p2=f"channel {channel_number} {self.translator[mode]}")

    def start_pulsetest_channel(self, channel_number: Union[int, Channels], gain: int = 800, count: int = 1, delay: int = 0) -> None:
        """ External set of pulse test. Only avaible for exisiting ports and sensors.

        .. warning:: AppCmds are user functions and due to that not null based. Implemented IntEnums are code based and have to be added by one each.

        :param channel_number: Channel where pulsetest gets executed.
        :type channel_number: int or Channels
        :param gain: Used gain for pulsetest, defaults to 800
        :type gain: int, optional
        :param count: Used count for pulsetest, defaults to 1
        :type count: int, optional
        :param delay: Used delay for pulsetest, defaults to 0
        :type delay: int, optional
        :raises ValueError: If gain is out of bounds: range(0,4096) | If count is out of bounds: range(0,200) | If delay is out of bounds: smaller zero
        """

        # AppCmds are user functions and due to that not null based. Implemented IntEnums are code based and have to be added by one each.
        channel_number += 1

        # check params limits
        if not 0 <= gain < 4096 and not 0 <= count < 201 and not 0 <= delay:
            self.logger.error("Params out of bounds")
            raise ValueError("Params out of bounds")

        p2_string = f"channel {channel_number} pulsetest {gain} {count} {delay}"
        self._value_parser(cmd="AppCmd",
                               p1="Preamp", p2=p2_string)

    def start_pulsetest_port(self, port_number: Union[int, PreampPorts], gain: int = 800, count: int = 1, delay: int = 0, multi_preamp_input: Union[int, MultiPreampInput] = MultiPreampInput.NONE_MULTI_INPUT) -> None:
        """External set of pulse test. Only avaible for exisiting ports and sensors.

        .. warning:: AppCmds are user functions and due to that not null based. Implemented IntEnums are code based and have to be added by one each.

        :param port_number: Port where pulsetest gets executed.
        :type port_number: int or PreampPorts
        :param gain: Pulsetest gain in range(0,4096), defaults to 800
        :type gain: int
        :param count: Pulsetest count in range(0,200), defaults to 1
        :type count: int
        :param delay: Pulsetest delay in ms, defaults to 0
        :type delay: int
        :param multi_preamp_input: Input number for Multi Input Preamps, defaults to NONE. Default case is useable for none MultiInput Premaps.
        :type multi_preamp_input: int or MultiPreampInputs
        :raises ValueError: If gain is out of bounds: range(0,4096) | If count is out of bounds: range(0,200) | If delay is out of bounds: smaller zero
        """
        # ..warning AppCmds are user functions and due to that not null based. Implemented IntEnums are code based and have to be added by one each.
        port_number += 1

        # check params limits
        if not 0 <= gain < 4096 and not 0 <= count < 201 and not 0 <= delay:
            self.logger.error("Params out of bounds")
            raise ValueError("Params out of bounds")

        if multi_preamp_input == MultiPreampInput.NONE_MULTI_INPUT:
            p2_string = f"port {port_number} pulsetest {gain} {count} {delay}"
        else:
            # ..warning AppCmds are user functions and due to that not null based. Implemented IntEnums are code based and have to be added by one each.
            multi_preamp_input += 1
            p2_string = f"port {port_number} {multi_preamp_input} pulsetest {gain} {count} {delay}"
        self._value_parser(cmd="AppCmd",
                               p1="Preamp", p2=p2_string)

    # ANALYZER: c++ bug, Peter will fix it
    def change_preamp_input(self, opti_port_number: Union[int, PreampPorts], preamp_input_number: Union[int, MultiPreampInput] = MultiPreampInput.MULTI_INPUT_2) -> None:
        """ Method changes which physical preamp input will be used for datastream output to optimizer.

        Only avaible for multi input preamps.

        .. warning:: AppCmds are user functions and due to that not null based. Implemented IntEnums are code based and have to be added by one each.

        :param opti_port_number: opti port number to adress
        :type opti_port_number: int or PreampPorts
        :param preamp_input_number: Switched input channel from preamp (target), defaults to MULTI_INPUT_2
        :type preamp_input_number: int or MultiPreampInput
        """
        # ..warning AppCmds are user functions and due to that not null based. Implemented IntEnums are code based and have to be added by one each.
        opti_port_number += 1
        preamp_input_number += 1
        self._value_parser(cmd="AppCmd", p1="Preamp",
                           p2=f"port {opti_port_number} switchinput {preamp_input_number}")

    def start_frequency_test_port(self, port_number: Union[int, PreampPorts], multi_preamp_input: Union[int, MultiPreampInput] = MultiPreampInput.NONE_MULTI_INPUT) -> None:
        """Execute a frequency test for a specific port.

        .. warning:: AppCmds are user functions and due to that not null based. Implemented IntEnums are code based and have to be added by one each.

        :param port_number: Port number for frequency test
        :type port_number: int or PreampPorts
        :param preamp_input: Used Input
        :type preamp_input: int or MultiPreampInput, defaults to NONE_MULTI_INPUT for no multi input preamp
        """

        # ..warning AppCmds are user functions and due to that not null based. Implemented IntEnums are code based and have to be added by one each.
        port_number += 1
        if multi_preamp_input == MultiPreampInput.NONE_MULTI_INPUT:
            self._value_parser(cmd="AppCmd", p1="Preamp",
                               p2=f"port {port_number} frqtest")
        else:
            # ..warning AppCmds are user functions and due to that not null based. Implemented IntEnums are code based and have to be added by one each.
            multi_preamp_input += 1
            self._value_parser(cmd="AppCmd", p1="Preamp",
                               p2=f"port {port_number} input {multi_preamp_input} frqtest")

    def start_frequency_test_channel(self, channel_number: Union[int, Channels]) -> None:
        """Execute a frequency test for a specific port. Analyzer isn't resonsing in any way (not in a visual, acoustic
        or information way).

        .. warning:: AppCmds are user functions and due to that not null based. Implemented IntEnums are code based and have to be added by one each.

        :param port_number: Channel number for frequency test
        :type port_number: int or Channels
        """
        # ..warning AppCmds are user functions and due to that not null based. Implemented IntEnums are code based and have to be added by one each.
        channel_number += 1
        self._value_parser(cmd="AppCmd", p1="Preamp",
                           p2=f"channel {channel_number} frqtest")

    def set_area_scale(self, area_number: int, scale: int = 500) -> None:
        """ Set scale of each view area. Available for splitted analyzer view and single view.
        In case of single view area_number equals one.

        Scale should be in range(10,1001) | Area number should be in range(1,5), but is limited to current activated area views.

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
                "Choosen key is out of bounds. Scale should be in range(10,1001) and area number should be in range(1,5).")
            raise ValueError(
                "Choosen key is out of bounds. Scale should be in range(10,1001) and area number should be in range(1,5).")

    def set_area_colour(self, area_number: int, colour_scale: int = 200) -> None:
        """Set the colour scale for area view. Only available in area

        Colour scale should be in range(10,401) | Area should be in range(1,5)

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
                "Choosen key is out of bounds. Scale should be in range(10,401) and area number should be in range(1,5).")
            raise ValueError(
                "Choosen key is out of bounds. Scale should be in range(10,401) and area number should be in range(1,5).")

    def set_area_time_range(self, area_number: int, start_time: int, time_range: int) -> None:
        """ Set of shown time range for each area.

        :param area_number: Area which should be addressed
        :type area_number: int
        :param start_time: Start point of time range in ms.
        :type start_time: int
        :param time_range: Range that will be shown from start_time in ms.
        :type time_range: int
        """
        self._value_parser(cmd="AppCmd", p1="SetAreaPosition",
                           p2=f"{area_number} {start_time} {time_range}")

    def load_process(self, process_number: int, start_time=0) -> None:
        """ Load and display by process number.

        :param process_number: Process that will be loaded
        :type process_number: int
        :param start_time: Start time in ms, defaults to 0
        :type start_time: int, optional
        """
        self._value_parser(cmd="AppCmd", p1="LoadProcess",
                           p2=f"{process_number} {start_time}")

    def get_service_parameter(self, param_setting: str) -> str:
        """Get Values from Service Parameter (Configuration->Settings->Parameter)
        .. note:: Only avaible for user level 8 or higher!

        :param param_setting: Service parameter that should be read
        :type param_setting: str
        :return: Current set service parameter value
        :rtype: str
        """
        settings = self._value_parser(cmd="appfunc", p1="GetServiceParameter",
                                      p2=param_setting)
        return settings.get("result")

    def set_service_parameter(self, param_setting: str, param_value: any) -> None:
        """Set Parameter in Service Parameter (Configuration->Settings->Parameter)
        .. note:: Only avaible for user level 8 or higher!

        :param param_setting: Service parameter that should be set
        :type param_setting: str
        :param param_value: New value of choosen service parameter
        :type param_value: any
        """
        self._value_parser(cmd="AppCmd", p1="setServiceParameter",
                           p2=f"{param_setting} {param_value}")
        self.logger.info(
            f"Service parameter {param_setting} is changed to {param_value}")

    def send_analyzer_to_sleep(self, time=2000) -> None:
        """ Only testing purpose. Command to send Analyzer system in sleep mode.

        :param time: Time to sleep in ms, defaults to 2000
        :type time: int, optional
        """
        self._value_parser(cmd="AppCmd", p1="sysSleep", p2=time)
        self.logger.info("Analyzer tired. Analyzer sleep.")

    def set_appvar(self, appvar_name: str, appvar_value: any) -> None:
        """Set the value of an AppVar by using the name of the AppVar. The prefix "pro_" will result in the AppVar being
        saved in the project and persist between restarts. The prefix "sys_" will result in the AppVar being saved globally
        and made available over all projects.

        If the AppVar doesn't exist yet it will be created.

        :param app_var_name: Name of the AppVar.
        :type app_var_name: str
        :param app_var_value: Value of AppVar. The type can be every datatype supported by python (e.g. float, int, str, json, ...).
        :type app_var_value: any
        """
        self._value_parser(cmd="setappvar", p1=appvar_name, p2=appvar_value)

    def get_appvar(self, appvar_name: str) -> str:
        """Get AppVar value by name.

        :param app_var_name: Name of AppVar to adress.
        :type app_var_name: str
        :return: AppVar value
        :rtype: str

        .. note: If requested Appvar is a json, the parsed value will be changed due to string escape.
        """
        val = self._value_parser(cmd="getappvar", p1=appvar_name)

        return val.get('result')

    def remove_appvar(self, appvar_name: str) -> None:
        """ Clear and remove AppVar by name.

        :param appvar_name: Name of AppVar to remove.
        :type appvar_name: str
        """
        self._value_parser(cmd="clearappvar", p1=appvar_name)

    def remove_appvar_report_callback(self, callback) -> None:
        """ Removes specific callback function from AppVar report callback list.
        By removing all callbacks the report function will be automatically stopped.

        :param callback: Callback function that should be removed from AppVar report functionalities.
        :type callback: function
        """
        self.__recv_thread.deregister_callbacks(
            "responseappvars", callback)
        self._appvar_report_count -= 1
        self.logger.info(
            f"Callback {callback} for AppVar report removed")
        if self._appvar_report_count == 0:
            self._value_parser(cmd="reportappvars",
                               p1="false")
            self.logger.info("Report of AppVar stopped.")

    def add_appvar_report_callback(self, callback) -> None:
        """ Add callback function to report of AppVar. Everytime a AppVar changes, added callback functions will be executed. See networking_example.py for an example.
        By adding first callback the report start automatically und will be stopped by removing all callbacks due to remove function. Beside the executed callback, analyzer sends
        state of all AppVars as information by every change.

        .. warning:: All callbacks need as first param "result" to catch analyzer response, if used or not.

        :param callback: Added callback function when report happens.
        :type callback: function
        """
        if self._appvar_report_count == 0:
            self._value_parser(user_callback=callback, cmd="reportappvars",
                               p1="true")
        else:
            self.__recv_thread.register_callbacks(
                "responseappvars", callback)
        self._appvar_report_count += 1
        self.logger.info(
            f"Callback {callback} for AppVar report added")

    def get_process_number(self) -> int:
        """ Returns current process number (active buffer).

        :return: Process number of selected process
        :rtype: int
        """
        obj = self._value_parser(cmd="getprocessnumber")

        return obj.get("processnumber")

    def create_project(self, project_name: str) -> None:
        """Create new project after used template with custom name.

        .. note:: Name size has to be at least 4. Avoid spaces or other typical forbidden characters in the project name.

        :param project_name: Name of new project
        :type project_name: str
        """
        self._value_parser(cmd="createloadproject", p1=project_name)

    def send_appcmd(self, param_one: str, param_two=None):
        """General method to send arbitrary AppCmd to analyzer.

        .. warning:: Developer function. Do not use without prior knowledge about AppCmds!

        :param param_one: AppCmd
        :type param_one: str
        :param param_two: If needed second parameter to specify params used in AppCmd, defaults to None
        :type param_two: str, optional
        :raises TypeError: Type Check for second parameter, exception is raised if value is not equal to type str.
        """
        if param_two:
            if isinstance(param_two, str):
                self._value_parser(cmd="AppCmd", p1=param_one, p2=param_two)
            else:
                raise TypeError("Second parameter has to be a string.")
        else:
            self._value_parser(cmd="AppCmd", p1=param_one)

    def set_multiplexer(self, channel=Channels.CHANNEL_1, chp=ChannelPorts.CHANNEL_PORT_1, preampport=PreampPorts.PREAMP_PORT_1,
                        fft=True, signal=False, samplerate=Samplerates16Bit.SAMPLERATE_1600_kHz, fftoversampling=FFTOversampling.FFT_OVERSAMPLING_8_TIMES,
                        fftwindowing=FFTWindowing.FFT_WINDOWING_HANNING, fftlogarithmic=FFTLogarithmic.FFT_LOGARITHMIC_BASE_14, filter=True, gain=800, subport=0) -> None:
        """ Method to set preamplifier and multiplexer settings.
        .. warning:: Range of params will not be checked.

        :param channel: Desired channel (Dropdown), defaults to Channels.CHANNEL_1
        :type channel: int or Channels, optional
        :param chp: Desired channelport (Dropdown), defaults to ChannelPorts.CHANNEL_PORT_1
        :type chp: int or Channelports, optional
        :param preampport: Which Preampport should be used, defaults to PreampPorts.PREAMP_PORT_1
        :type preampport: int or PreampPorts, optional
        :param fft: Checkbox if fft buffer should be recorded, defaults to True
        :type fft: bool, optional
        :param signal: Checkbox if signal buffer should be recorded, defaults to False
        :type signal: bool, optional
        :param samplerate: Desired samplerate (Dropdown) defaults to Samplerates16Bit.SAMPLERATE_1600_kHz
        :type samplerate: int or Samplerates16Bit, optional
        :param fftoversampling: Desired FFTOversampling (Dropdown), defaults to FFTOversampling.FFT_OVERSAMPLING_8_TIMES
        :type fftoversampling: int or FFTOversampling, optional
        :param fftwindowing: Desired FFTOversampling (Dropdown), defaults to FFTWindowing.FFT_WINDOWING_HANNING
        :type fftwindowing: int or FFTWindowing, optional
        :param fftlogarithmic: Desired FFTLogarithmic (Dropdown), defaults to FFTLogarithmic.FFT_LOGARITHMIC_BASE_14
        :type fftlogarithmic: int or FFTLogarithmic, optional
        :param filter: If frequency filter should be set, defaults to True
        :type filter: bool, optional
        :param gain: Gain of Preamp, defaults to 800
        :type gain: int, optional
        :param subport: Desired Subport (Dropdown), defaults to 0
        :type subport: int, optional
        """
        self._value_parser(cmd="setpreamp", expect_response=False, channel=channel, chp=chp, preampport=preampport, fft=fft, signal=signal, samplerate=samplerate,
                           fftoversampling=fftoversampling, fftwindowing=fftwindowing, fftlogarithmic=fftlogarithmic, filter=filter, gain=gain, subport=subport)

    def get_analyzer_versions(self) -> str:
        """Method to read out anlyzer version informations and return as string. Information are identical to in-software "about" button.

        :return: Information out of info window in analyzer.
        :rtype: str
        """
        val = self._value_parser(cmd="getversions")
        # process response
        analyzer_info = val.get("v")
        while "\\n" in analyzer_info:
            analyzer_info = analyzer_info.replace("\\n", "\n")

        return analyzer_info

    def get_project_info(self) -> Dict:
        """Method to read out analyzer project informations as current used project ID/name or analyzer version.

        :return: Information about current project.
        :rtype: Dict
        """
        project_info = self._value_parser(cmd="getinfo")

        # process response
        project_info.pop("v")
        project_info.pop("cmd")

        return project_info

    def get_heartbeat(self) -> bool:
        """ Checks if the little guy is still there.

        :return: True if message comes back.
        :rtype: bool
        """
        val = self._value_parser(cmd="heartbeat")
        # process response
        if val:
            self.logger.info("No worries. I'm still alive.")
            return True

    def set_measuring_mode(self, mode: Union[bool, str]) -> None:
        """Start or stop a measurement. Additionally mode provides possibility to start monitoring mode.

        .. list-table:: Keywords on one look
            :widths: 15 25
            :header-rows: 1

            * - Key
              - Measuring mode
            * - monitor
              - Start monitoring
            * - true
              - Start measurement
            * - false
              - Stop measurement

        :param mode: Choosen measuring mode out of table above.
        :type mode: str, bool
        :raises KeyError: if keyword argument "mode" is parsed with invalid values.
        """
        self._value_parser(cmd="startmeasuring", p1=self.translator[mode])
        # flags for context manager exit method
        if self.translator[mode] == "true":
            self._measuring_active = True
        elif self.translator[mode] == "false":
            self._measuring_active = False
        elif self.translator[mode] == "monitor":
            self._monitoring_active = True

    def set_monitoring_mode(self, mode: Union[bool, str]) -> None:
        """Start or stop monitoring modus.

        .. list-table:: Keywords on one look
            :widths: 15 25
            :header-rows: 1

            * - Key
              - Measuring mode
            * - true
              - Start monitoring
            * - false
              - Stop monitoring

        :param mode: Switch between start monitoring ("true") or stop monitoring  ("false"). For supported keys see translator.
        :type mode: str, bool
        :raises KeyError: if keyword argument "mode" is parsed with invalid values.
        """
        self._value_parser(cmd="startmonitoring", p1=self.translator[mode])
        # flags for context manager exit method
        if self.translator[mode] == "true":
            self._monitoring_active = True
        elif self.translator[mode] == "false":
            self._monitoring_active = False

    def get_max_amp_per_band(self, channel=Channels.CHANNEL_1, create_plot_buffer: bool = True, create_data_buffer: bool = False, amplitude_type=SysAmplitudesType.AMPLITUDE_DEFAULT) -> np.ndarray:
        """ Method to return maximum amplitude per band of current active buffer.

        :param channel: Datastream Channel, defaults to Channels.CHANNEL_1
        :type channel: int or Channel, optional
        :param create_plot_buffer: Creates a plot buffer in the Analyzer software, defaults to True
        :type create_plot_buffer: bool, optional
        :param create_data_buffer: Creates a data buffer in the Analyzer software, defaults to False
        :type create_data_buffer: bool, optional
        :param amplitude_type: Amplitude unit, defaults to SysAmplitudesType.AMPLITUDE_DEFAULT
        :type amplitude_type: int or SysAmplitudeType, optional
        :return: Calculated maximum amplitude values per band
        :rtype: np.ndarray
        """
        print("create_plot_buffer:", create_plot_buffer)
        response_dict = self._value_parser(cmd="calcmaxamplitude", channel=channel,
                                           plot=create_plot_buffer, save=create_data_buffer, amplitudetype=amplitude_type)
        # extract important information
        max_amp = response_dict.get("p1")

        return np.fromstring(max_amp, sep=',')

    def load_test_project(self) -> None:
        """ Loads the set test project."""
        self._value_parser(cmd="loadtestproject")

    def load_last_user_project(self) -> None:
        """ Loads last user project before a test project was loaded.

        .. warning:: To use this a test project must be loaded before!!!

        .. note:: If no testproject was loaded beforehand, <name_variable> in analyzer software will not be addressed and
        a new project without name!(="") is going to be created. Once a project like this exist, analyzer cannot perform this again
        and without loading a test project beforehand, function will do nothing (but parse any check).
        """
        self._value_parser(cmd="loaduserproject")

    def get_measure_positions(self) -> Dict:
        """ Gets a dictionary with all measure positions and if used an energy value.

        :return: Measurepositions and their calculated energy value.
        :rtype: Dict
        """
        return self._value_parser(cmd="getmaxmeasurepositions")

    def get_preamp_info(self, preamp_port: Union[PreampPorts, int]) -> str:
        """ Returns a string with serial number, firmware version and S-Value of connected preamp.

        :param preamp_port: Preamp port with connected preamp
        :type preamp_port: int, PreampPorts
        :raises KeyError: Raises if parsed variable is no supported preamp port
        :return: Serial number, firmware version and S-value
        :rtype: str
        """
        if preamp_port in PreampPorts or preamp_port in range(0, 8):
            preamp_hardware_info = self._value_parser(
                cmd="getpreampinfo", p1=preamp_port)
            return preamp_hardware_info.get('p1')
        else:
            self.logger.error(
                "Choosen preampport is not an analyzer system preamp port.")
            raise KeyError(
                "Choosen preampport is not an analyzer system preamp port.")

    def start_operator_function(self, mode: Union[str, bool] = "start") -> None:
        """Start operator functions.

        :param mode: Function can start or end operator function by changing mode to a stopping key, defaults to "start". For more allowed keys look up translator dict.
        :type mode: str, bool, optional
        """
        self._value_parser(cmd="startoperatorfunctionvalues",
                           p1=self.translator[mode])
        # flags for context manager exit method
        if self.translator[mode] == "true":
            self._operator_functions_active = True
        elif self.translator[mode] == "false":
            self._operator_functions_active = False

    def stop_operator_function(self) -> None:
        """Stop of running operator function."""
        self._value_parser(cmd="stoppoperatorfunctionvalues")
        # flags for context manager exit method
        self._operator_functions_active = False

    def set_serial_number(self, serial_number: int, process_number: int) -> None:
        """Setting serial number for arbitary process.

        Serial number is stored in the database using the process.serial attribute

        :param serial_number: Serial number that should be set.
        :type serial_number: int
        :param process_number: Process which should be connected to serial.
        :type process_number: int
        """
        self._value_parser(cmd="AppCmd", p1="SetProcessSerial",
                           p2=f"{process_number} {serial_number}")

    def set_serial_number_pending_process(self, serial_number: int) -> None:
        """Setting serial number for next process.

        Serial number is stored in the database using the process.serial attribute

        :param serial_number: Serial number for next process
        :type serial_number: int
        """
        self._value_parser(cmd="setpendingserial", p1=serial_number)

    def set_comment_pending_process(self, comment: str) -> None:
        """Set process comment for pending process.

        Comment is saved in the database using the process.comment attribute

        :param comment: Comment for next process.
        :type comment: str
        """
        self._value_parser(cmd="setpendingcomment", p1=comment)

    # def set_comment_current_process(self, comment: str) -> None:
     #   """ Sets comment for current activatet process.

#        Similair to set_proces_comment but as JSON communication Server command.
 #       Comment is saved in database under process.comment
#
 #       :param comment: Process comment to set
 #       :type comment: str
 #      """
 #       self._value_parser(cmd="setcomment", p1=comment, quiet=False)

    def start_operator(self, operator_name: str, operator_setting: str, user_callback=None) -> None:
        """Manual start of existing operator by name. By adding a callback function,
        software will execute callback when operator finish.

        .. note:: Every callback needs an argument for passed response, whether it is used or not. 

        :param operator_name: Name of operator that should start
        :type operator_name: str
        :param operator_setting: Operator settings like "loop from 0 to -1 simulation 2"
        :type operator_setting: str
        :param user_callback: function receiving the response as a parameter.
            Will be called after the operator finishes.
        :type user_callback: function
        """
        if user_callback:
            self.__recv_thread.register_callbacks(
                operator_name, user_callback)
        self._value_parser(expect_response=False, cmd="startoperator",
                           p1=operator_name, p2=operator_setting)

    def import_patterns(self, directory_path: str) -> None:
        """Import all pattern files from a optimizer local directory.

        :param directory_path: Directory path to patterns that will be imported.
        :type directory_path: str
        """
        self._value_parser(expect_response=False, cmd="importpatterns",
                           p1=directory_path)

    def import_trigger_list(self, filepath: str, append: bool = False) -> None:
        """ Import a trigger list file from local path. Append option decides already exisitng triggers will be set active or not.

        :param filepath: Local filepath
        :type filepath: str
        :param append: Decision to set already existing trigger list active or passive by extending, defaults to False.
        :type append: bool, optional
        """
        p2_string = f"triggerlist {filepath}"

        if append:
            p2_string = p2_string + " -a"
        self._value_parser(cmd="AppCmd",
                           p1="import", p2=p2_string)

    def import_operator_network(self, filepath: str) -> None:
        """ Import local operator network file. Command runs as root import.

        .. warning:: The current operator network will be replaced.

        :param filepath: Local filepath to operator network file
        :type filepath: str
        """
        self._value_parser(cmd="AppCmd",
                           p1="import", p2=f"opnet {filepath}")

    def import_project_archive(self, filepath: str, project_name: str, keep_original_process_nums: bool = False, overwrite: bool = False) -> None:
        """ Import a complete project archive file (tar.gz). 

        .. warning:: If keep_original_process_nums is set, the proces structure will be kept like before the import. As an example if process 17000 has been exported, this flag will create 16999 empty processes before.

        .. warning:: If overwrite is activated this will be overwrite and delete current activated project.

        :param filepath: Local filepath to archive file
        :type filepath: str
        :param project_name: Name of the now imported project
        :type project_name: str
        :param original_nums: Keeps the original process number, defaults to False
        :type original_nums: bool, optional
        :param overwrite: Overwrites current active project, defaults to False
        :type overwrite: bool, optional
        """
        p2_string = f"{filepath} {project_name}"
        if keep_original_process_nums:
            p2_string = p2_string + " --originalnums"
        if overwrite:
            p2_string = p2_string + " --overwrite"

        self._value_parser(cmd="AppCmd", expect_response=False,
                           p1="importprojectarchive", p2=p2_string)

    def export_operator_network(self, target_filepath: str, export: str = "root") -> None:
        """ Exports operator network as JSON file. Export contains either current activated
        (key:"root"), all (key:"all") or just the network template (key:"template") by parsing the key to export. 

        .. list-table:: Keywords on one look
            :widths: 15 25
            :header-rows: 1

            * - Key
              - Definition
            * - root
              - Exports current active operator network
            * - all
              - Exports all avaible operator networks
            * - template
              - Exports project specific operator network template

        :param folderpath: Target file path
        :type folderpath: str
        :param export: Decided what from operator will be exported. Current activated("root"), all operators or the template, defaults to "root"
        :type export: str, optional
        """
        my_translator = {"root": "-r", "all": "-a", "template": "-t"}
        self._value_parser(cmd="AppCmd", expect_response=True,
                           p1="export", p2=f"opnet {target_filepath} {my_translator[export]}")

    def export_trigger_list(self, target_filepath: str) -> None:
        """ Exports current trigger list to path. Target filepath should contain new file name.

        :param target_filepath: Target file path
        :type target_filepath: str
        """
        self._value_parser(cmd="AppCmd", expect_response=True,
                           p1="export", p2=f"triggerlist {target_filepath}")

    def export_project_archive(self, target_filepath: str, export_name: str, export_process: int = None, export_pengui: bool = True, keep_folder: bool = True) -> None:
        """ Exports current active project to path as tar.gz file. This includes all patterns, trigger list and projects.

        :param target_filepath: Target folder path
        :type target_filepath: str
        :param export_name: Give export file a name
        :type export_name: str
        :param export_process: Exports an example process with measurement data, defaults to None
        :type export_process: int, optional
        :param export_pengui: Exports PenGUI, defaults to True
        :type export_pengui: bool, optional
        :param keep_folder: Preserves folder structure and exports this structure to target, defaults to True
        :type keep_folder: bool, optional
        """
        p2_string = f"{target_filepath} {export_name}"
        if export_process:
            p2_string = p2_string + f" --process {export_process}"
        if export_pengui:
            p2_string = p2_string + " --pengui"
        if keep_folder:
            p2_string = p2_string + " --keepfolder"

        self._value_parser(cmd="AppCmd", expect_response=False,
                           p1="exportprojectarchive", p2=p2_string)

    # TODO: Test in newest analyzer version
    def flash_preamp_firmware(self, preampport: Union[int, PreampPorts], filepath: str) -> None:
        """ Flash preamp firmware by downloaded hexfile. Path should be absolute path.

        :param preampport: Connected Preamp
        :type preampport: int or PreampPorts
        :param filepath: Absolute (!) path to hexfile
        :type filepath: str
        """
        preampport += 1
        self._value_parser(cmd="appfunc", expect_response=False,
                           p1="PreampTool", p2=f"flash {preampport} {filepath}")
        # self._value_parser(cmd="PreampTool",
        #                   p1=f"flash {preampport} {filepath}")

    def set_default_project(self, comment: str = None) -> None:
        """ Set current active project as new default template.

        :param comment: Comment to describe template, defaults to None
        :type comment: str, optional
        """
        if comment:
            self._value_parser(cmd="AppCmd",
                               p1="SaveProjectasDefault", p2=f"-c {comment}")
        else:
            self._value_parser(cmd="AppCmd",
                               p1="SaveProjectasDefault")

    def remove_default_project(self) -> None:
        """ Removes current project template."""
        self._value_parser(cmd="AppCmd",
                               p1="SaveProjectasDefault", p2=f"-e")

    # TODO: Test
    @analyzer_functionality_warning_decorator
    def start_operator_results(self, mode: Union[str, bool] = "enable") -> None:
        """ Sets enable flag to send ot operator results if avaible. Results will be sended separately

        :param mode: Enables start or stops by "disable", defaults to "enable"
        :type mode: str, optional
        """
        self._value_parser(cmd="startoperatorresults",
                           p1=self.translator[mode])

    # TODO: Test
    @analyzer_functionality_warning_decorator
    def stop_operator_results(self) -> None:
        """ Sets operator results to stop."""
        self._value_parser(cmd="stopoperatorresults")

    def get_io_input(self) -> int:
        """ Current set I/O input register as integer appearance (converted from hex).

        :return: I/O input register as integer appearance
        :rtype: int
        """
        val = self._value_parser(cmd="readioin")
        return val.get("result")

    def get_io_output(self) -> int:
        """ Returns set I/O output register as integer appearance of hexa state.

        :return: Set I/O output
        :rtype: int
        """
        val = self._value_parser(cmd="readioout")
        return val.get("result")

    def _shift_binary(self, original_bin: str) -> str:
        """Helper method to convert incoming binary to least significant digit on the right side

        :param original_bin: Incoming binary
        :type original_bin: str
        :return: Shifted binary
        :rtype: str
        """
        # Elia's Version didn't worked
        # new_val = 0
        # for i in range(16):
        #    bit_state = (original_bin & (1 << i) >> i)
        #    print("bit state", bit_state)
        #    new_val = new_val | (bit_state << (16-i))

        # return new_val

        # Oli's version
        # helper list
        new_val = [0] * len(original_bin)

        # save current val to shifted position in list
        for (i, bit) in enumerate(original_bin):
            new_val[len(new_val)-1-i] = bit

        # convert list to string and return
        return "".join(new_val)

    def _binary_to_hexa(self, binary_str: str) -> str:
        """ Formats incoming binary to hexa representation with leading zeros. And leading "0xf" term.

        :param binary_str: Binary that should be converted to hexa representation.
        :type binary_str: str
        :return: hexa representation
        :rtype: str
        """
        hexa = "0xf" + "{0:0>4x}".format(int(binary_str, 2))
        return hexa

    def set_simulated_io_input(self, io: str) -> None:
        """Set simulated I/O input register. I/0 input register can be set by inverted hexa (smallest significant right)
        or by providing a binary representation of seen bits set in I/O register.

        First 8 digits are first I/O input register
        Second 8 digits are second I/O input register
        Give in all inputs as strings only!

        .. list-table:: I/O Input possibilities
            :widths: 25 25
            :header-rows: 1

            * - Binary Representation
              - Hexadecimal Representation
            * - "00000000 00000000"
              - "0xf0000"
            * - "10000000 00000000"
              - "0xf0001"
            * - "01000000 00000000"
              - "0xf0002"
            * - "11000000 00000000"
              - "0xf0003"
            * - "00100000 00000000"
              - "0xf0004"
            * - "10100000 00000000"
              - "0xf0005"
            * - "01100000 00000000"
              - "0xf0006"
            * - "11100000 00000000"
              - "0xf0007"
            * - "00010000 00000000"
              - "0xf0008"
            * - "10010000 00000000"
              - "0xf0009"
            * - "01010000 00000000"
              - "0xf000A"
            * - "11010000 00000000"
              - "0xf000B"
            * - "00110000 00000000"
              - "0xf000C"
            * - "10110000 00000000"
              - "0xf000D"
            * - "01110000 00000000"
              - "0xf000E"
            * - "11110000 00000000"
              - "0xf000F"
            * - ...
              - ...
            * - "10001000 00000000"
              - "0xf0011"
            * - ...
              - ...

        :param io: Combination of bits set to I/O input register (one and two), defaults to "0xf0000". For further information see extended summary.
        :type io: str
        :raises ValueError: If parsed I/O input is not supported in this form. Means no from like "00000000 00000000" or "0xf0000". 
        """
        # helper
        bin_ref = "00000000 00000000"
        hexa_ref = "0xf0000"
        # case handler
        if len(io) == len(bin_ref):  # binary case
            # replace white space if needed
            if " " in io:
                io = io.replace(" ", "")  # delete space
            # shift binary to least signifcant bit right
            io_binary = self._shift_binary(io)
            # convert binary to hexa
            io_hexa = self._binary_to_hexa(io_binary)
        elif len(io) == len(hexa_ref):  # hexa case
            io_hexa = io
        else:
            self.logger.error(
                "Given format of I/O input register state is not supported. Please check extended method documentation.")
            raise ValueError(
                "Given format of I/O input register state is not supported. Please check extended method documentation.")

        self._value_parser(cmd="setsimioin",
                           p1=io_hexa)

    def add_io_report_callback(self, callback) -> None:
        """Adds callback function to report of I/O register. Everytime I/O register changes, added callback functions will be executed. See networking_example.py for an example.
        By adding first callback the report start automatically und will be stopped by removing all callbacks due to remove function.

        .. warning:: All callbacks need as first param "result" to catch analyzer response, if used or not.

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
        """ Removes specific callback function from I/O report callback list. By removing all callbacks the report function will be automatically stopped.

        :param callback: Callback function that should be removed from I/O report functionalities.
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

    def add_process_number_report_callback(self, callback) -> None:
        """ Adds callback function to report of process number. Everytime the process number changes, added callback functions will be executed. See networking_example.py for an example. By adding first callback the report start automatically und will be stopped by removing all callbacks due to remove function.

        .. warning:: All callbacks need as first param "result" to catch analyzer response, if used or not.

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

    def set_io_ouput(self, io_line: int, state: bool) -> None:
        """ Sets single I/O ouput line. As parameter only line number of third I/O line is required.

        .. warning:: Changing output line 3.1 - 3.3 is not possible. 

        .. list-table:: I/O Output possibilities
            :widths: 25 25
            :header-rows: 1

            * - I/O line
              - parameter
            * - 3.1
              - 1
            * - 3.2
              - 2
            * - 3.3
              - 3
            * - 3.4
              - 4
            * - 3.5
              - 5
            * - 3.6
              - 6
            * - 3.7
              - 7
            * - 3.8
              - 8

        :param io_line: Line number in range(1,8)
        :type io_line: int
        :param state: Set Line high or low
        :type state: bool
        """
        self._value_parser(expect_response=True,
                           cmd="appcmd", p1="setioout", p2=f"{io_line} {state}")

    def remove_process_number_report_callback(self, callback) -> None:
        """ Removes specific callback function from process number report callback list. By removing all callbacks the report function will be automatically stopped.

        :param callback: Callback function that should be removed from process number report functionalities.
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

    # TODO: Test
    def start_script_function(self, function_name: str, function_param: any) -> None:
        """ General syntax to start script function. Response is depending on called function.

        .. warning:: Service function, should not be used without prior kmowledge about remote scripts

        :param function_name: Name of script function
        :type function_name: str
        :param function_param: Passed param to script function
        :type function_param: any
        :return: Standard Analyzer response. Dict contains result of addressed function as str.
        :rtype: Dict
        """
        return self._value_parser(cmd="appfunc",
                                  p1=function_name, p2=function_param)

    def set_human_confirmation(self, process_IO=False, **kwargs) -> None:
        """ Send human confiramtion over current process. Score and comment can be parsed over kwargs.

        .. list-table:: Possible keyword arguments
            :widths: 15 25
            :header-rows: 1

            * - Key
              - Definition
            * - comment
              - Human comment for confirmation
            * - score
              - Score value for confirmation

        :param process_IO: Confirmation if current process is IO or NIO, defaults to False
        :type process_IO: bool
        :raises ValueError: If kwargs key is not supported
        """
        translator = {False: "NIO", True: "IO"}
        settings = {"cmd": "confirmation",
                    "p1": translator[process_IO]}
        if kwargs:
            if kwargs.keys() not in ["comment", "score"]:
                self.logger.error(
                    "Key is not supported for operation human_confirmation")
                raise ValueError(
                    "Key is not supported for operation human_confirmation")
            if "comment" in kwargs.keys():
                settings["p2"] = kwargs["comment"]
            if "score" in kwargs.keys():
                settings["score"] = kwargs["score"]

        self._value_parser(expect_response=False, **settings)

    def write_to_database(self, result: any, comment=None) -> None:
        """ Writes database query for an entry with current project_id, process, process_id, result and comment as values

        :param result: Result which should be saved in database
        :type result: any
        :param comment: Comment for result, defaults to None
        :type comment: str, optional
        """
        if comment:
            self._value_parser(expect_response=False, cmd="humanconfirmationresult",
                               p1=result, p2=comment)
        else:
            self._value_parser(expect_response=False, cmd="humanconfirmationresult",
                               p1=result)

    def write_backup(self) -> None:
        """Creates an automatic Analyzer backup."""
        self._value_parser(cmd="AppCmd", p1="writeBackup")

    def reset_failstate(self) -> None:
        """ Reset Analyzer failure state and activates I/O ready by this."""
        self._value_parser(cmd="AppCmd", p1="ResetFailstate")
    # TODO: profibus
    # TODO: profibus report

    def _recognition_translator(self, cmd: str) -> str:
        """ Private method to add "response" to already sended cmd str for later recognition.

        :param cmd: cmd string which needs to be changend.
        :type cmd: str
        :return: cmd string which will be sended by analyzer as response.
        :rtype: str
        """
        if cmd == "reportappvars":
            return "responseappvars"
        else:
            # case normal communication server command
            return "response" + cmd

    def _check_response(self, response):
        """Private method to check received response for value under key="ok". If value is True, response is approved.

        :param response: Response dict from analyzer to check.
        :type response: dict
        :raises AnalyzerSyntaxError: if command could not be performed, due to false syntax or params out of bounds.
        """
        # rais exception if not performed right
        if response.get("ok") == False:
            self.logger.error(
                "Analyzer could not perform action: check log and documentation.")
            raise AnalyzerSyntaxError(
                "Analyzer could not perform action: check log and documentation.")

    def _send(self, command: Dict) -> None:
        """ Private method to send commands to analyzer. Command will be encoded to bytestring.

        :param command: Command dict which should be sent to connected analyzer.
        :type command: Dict
        """
        # print every sended command
        self.logger.info(f"Command sent:{command}")
        # prepare command
        cmd_str = json.dumps(command).encode()
        cmd_str = (len(cmd_str)).to_bytes(2, 'big') + cmd_str
        # actual sending command
        self.s.sendall(cmd_str)

    def _value_parser(self, expect_response=True, user_callback=None, **kwargs) -> Dict:
        """ Function to coordinate sending parsed command settings and take back answer from receiver thread.

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

        # if response is expected:
        # register callback before sending
        if expect_response and user_callback == None:
            q = queue.Queue()
            def callback(result, queue_var=q): return queue_var.put(result)
            self.__recv_thread.register_callbacks(recognition, callback)
        elif expect_response:
            self.__recv_thread.register_callbacks(
                recognition, user_callback)

        # send command in any case
        self._send(command)

        # receive response if avaible and expected
        # reports are handled external
        if expect_response and user_callback == None:
            # get resonse out of queue
            analyzer_response = q.get()
            # deregister callback
            self.__recv_thread.deregister_callbacks(recognition)
            # check response for failure
            self._check_response(analyzer_response)
            return analyzer_response


class AnalyzerCmd(AnalyzerRemote):
    """ Depricated class naming. Inherit from normal class.

    .. deprecated:: 1.1
    Use AnalyzerRemote class instead.

    :param AnalyzerRemote: Inherited class
    :type AnalyzerRemote: class
    """

    def __init__(self, ip: str, port=17000, debug_mode=False):
        super().__init__(ip, port, debug_mode)
        warnings.warn(
            f"Class Name AnalyzerCmd is deprecated. Please use AnalyzerRemote!")
