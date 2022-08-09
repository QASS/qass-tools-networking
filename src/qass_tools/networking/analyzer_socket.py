import socket
import json
# from turtle import clear
# from xml.etree.ElementTree import Comment
import numpy as np
import time
from enum import Enum, auto, IntEnum
from typing import Any, Dict, Union
import logging
import sys
import threading
import queue
from collections import defaultdict
from retry import retry
from functools import wraps
import warnings


class Amplitudes(Enum):
    """ Enum class to list and check avaible amplitudes in mV to generate sine wave."""
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
    """Avaible selection box choices for channel in multiplexer configuration that will be addressed"""
    CHANNEL_1 = 0
    CHANNEL_2 = 1
    CHANNEL_3 = 2
    CHANNEL_4 = 3


class ChannelPorts(IntEnum):
    """Avaible selection box choices for channel port in multiplexer configuration that will be addressed"""
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
    """Avaible selection box choices for preamplifier port in multiplexer configuration that will be addressed"""
    PREAMP_PORT_1 = 0
    PREAMP_PORT_2 = 1
    PREAMP_PORT_3 = 2
    PREAMP_PORT_4 = 3
    PREAMP_PORT_5 = 4
    PREAMP_PORT_6 = 5
    PREAMP_PORT_7 = 6
    PREAMP_PORT_8 = 7


class Samplerates(IntEnum):
    """Avaible selection box choices for used samplerate in multiplexer configuration"""
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
    """Avaible selection box choices for used oversampling in multiplexer configuration"""
    FFT_OVERSAMPLING_2_TIMES = 1
    FFT_OVERSAMPLING_4_TIMES = 2
    FFT_OVERSAMPLING_8_TIMES = 3
    FFT_OVERSAMPLING_16_TIMES = 4
    FFT_OVERSAMPLING_32_TIMES = 5
    FFT_OVERSAMPLING_64_TIMES = 6
    NONE_FFT_OVERSAMPLING = 0


class FFTWindowing(IntEnum):
    """Avaible selection box choices for used windowing function in multiplexer configuration"""
    FFT_WINDOWING_HANNING = 0
    NONE_FFT_WINDOWING = 1


class FFTLogarithmic(IntEnum):
    """Avaible selection box choices for dispalyed FFT logarithmic base in multiplexer configuration"""
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
    """ Avaible view possibilities in analyzer area view."""
    View_1 = 1
    View_2 = 2
    View_3 = 3
    View_4 = 4


class SysSettingsClass(IntEnum):
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


class ConnectionError(socket.error):
    def __init__(self, ip, port):
        self.msg = f"Connection to ip: {ip} on port: {port} could not be established.\n"

    def __str__(self):
        return self.msg


class NoneRegistrationError(Exception):
    pass


class AnalyzerSyntaxError(Exception):
    pass


class ReceiveThread(threading.Thread):
    """ Receiving thread which runs due to contextmanager the whole time and listen to analyzer socket for responeses.
    Responses will be processed and parsed to a callback function (regular: adds response to queue for main thread to fetch te data."""

    def __init__(self, socket_obj, logger_obj, group=None, target=None, name=None, args=()):
        threading.Thread.__init__(self, group, target, name, args)
        self.lock = threading.RLock()
        self.__callbacks = defaultdict(list)
        self.s = socket_obj
        self.logger = logger_obj

    def register_callbacks(self, recognition: Union[str, int], callback) -> None:
        """ Function to register incomming analyzer response by msg_id or cmd name.
        Parsed callback will be regsitered by added as recognition-callback pair to a dict self.__callbacks.


        Here is used a MultiDict which by default creates a list for every dict entry.
        So it is possible to store mutiple callbacks for one recognition.

        :param recognition: Recognition to identify message.
        :type recognition: str, int
        :param callback: Callback to handle response value
        :type callback: function
        """
        with self.lock:
            self.__callbacks[recognition].append(callback)

    def deregister_callbacks(self, recognition: Union[str, int], user_callback=None) -> None:
        """ Remove callback registration.

        Due to the used MultiDict we have to check if only one vallback has to be removed or the complete registration.

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
        """Handles every complete message. Handling means decoding byte string do dict and apply response to every registered callback.
        Therefore response is not in an unit form, we need a if block which handles recognition over cmd name and message id

        :param response: Compelte analyzer response
        :type response: bytes string
        :param encoding_style: Encoding style used from Json module, defaults to "utf-8"
        :type encoding_style: str, optional
        """
        self.logger.debug(response)
        # change appearance
        response = response.decode(encoding_style)
        response = json.loads(response)

        with self.lock:
            if response['cmd'] in self.__callbacks:
                # reports alwys registered with cmd->only case we need tot est for mutiple callbacks
                length = len(self.__callbacks[response['cmd']])
                if length > 1:
                    # if mutiple callbacks apply response to all of them
                    for idx in range(0, length):
                        self.__callbacks[response['cmd']][idx](response)
                else:
                    self.__callbacks[response['cmd']][0](response)
            # if no report there is only one entry--> [0] always uses right callback
            elif 'resid' in response:
                if response['resid'] in self.__callbacks:
                    self.__callbacks[response['resid']][0](response)
            elif 'msgid' in response:
                if response['msgid'] in self.__callbacks:
                    self.__callbacks[response['msgid']][0](response)
            else:
                warnings.warn(
                    f"Not expected analyzer response (no registration).")
                self.logger.warning(
                    "Not expected analyzer response (no registration):\n")
                self.logger.warning(response)

    def run(self) -> None:
        # TODO: if not signal is received, change to mainthread
        """ Overriden run method of thread module will be executed as the thread starts.

        Method listens to socket in forever loop 'till kill_thread method is executed. Listens for small parts and sets messages together.
        If complete, messsage is parsed to handle_response.
        """
        current_len = 0
        buffer = bytearray()
        READ_SIZE = 4
        self.kill = False
        while not self.kill:
            try:
                buffer.extend(self.s.recv(READ_SIZE))
            # if nothing is received socket runs into failstate (socket.timeout)
            except socket.timeout as e:
                # in this case just continue while loop
                continue
            # catch other socket exception and crash
            except socket.error as e:
                self.logger.error(e)
                if int.from_bytes(buffer, byteorder='big') > 0:
                    self.logger.warning("Unfinished message received:\n")
                    self.logger.warning(buffer)
            # only enter for new current length setting or if message is complete
            while (len(buffer) >= current_len and len(buffer) != 0) or (current_len is 0 and len(buffer) >= 2):
                if current_len is 0:
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

    def kill_thread(self) -> None:
        """End forever loop in run method and join thread."""
        # self.daemon = True
        self.kill = True
        self.logger.info("Receiver thread is now killed.")
        self.join()


class AnalyzerCmd():
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
        self._measuring_active = False
        self._sine_gen_active = False
        self._monitoring_active = False
        self._operator_active = False
        self._operator_functions_active = False
        self._operator_results_active = False

        # short solution logger to sys.stdout
        msg_mode = logging.DEBUG if debug_mode else logging.INFO
        self.logger = self._create_logger(msg_mode)

    def __enter__(self):
        """ Connects the machine to an analyzer reachable over user-given Input of IP (self.ip) and Port (self.port)
        via TCP and returns an instance of the class. Additionally a second thread (called receiving thread) will be started.
        This thread will run until __exit__ method will kill recieve thread.

        :return: Instance of AnalyzerCmd class
        :rtype: AnalyzerCmd object
        """
        # connect to socket
        self._connecting_analyzer()

        # create thread instance
        self.__recv_thread = ReceiveThread(self.s, self.logger,
                                           group=None, target=None, name="receive thread")
        # start thread
        self.__recv_thread.start()
        return self

    def value_exception(self, custom_msg=None):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except:
                    # define logger msg
                    issue = f"{args} out of bounds.\n"
                    if custom_msg:
                        issue = issue+custom_msg
                    self.logger.error(issue)
                    raise
            return wrapper
        return decorator

    def key_exception(self, custom_msg=None, kwargs_key=True):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except:
                    # define logger msg
                    if kwargs_key:
                        issue = f"Used keys: {kwargs} not supported.\n"
                    else:
                        issue = f"Used keys: {args} not supported.\n"
                    if custom_msg:
                        issue = issue+custom_msg
                    self.logger.error(issue)
                    raise
            return wrapper
        return decorator

    def _create_logger(self, level_mode):
        """Creates a logger which will print out to sys.stdout and log custom message and time, log level,
        function name and if avaible line number where log occured.

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

        Retry decorator will retry method funtionalities by occuring ConnectionError. Here set delay layes by 1 second and
        decorator will try again for four times before giving up.

        :raises ConnectionError: Connection error sis raisen if no connection can be established.
        """
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.settimeout(1)
            self.s.connect((self.ip, self.port))
            self.logger.info("Connected to optimizer")
        except socket.timeout:
            raise ConnectionError(self.ip, self.port)

        except socket.error:
            raise ConnectionError(self.ip, self.port)

    def __exit__(self, exc_type, exc_value, traceback):
        """ If contextmanager is left, another two second will be waited before private function will be called to reiceiving thread
        (start in enter method of contextmanager) and also raise and log raisen errors.
        """
        time.sleep(2.0)

        self.__recv_thread.kill_thread()
        # save exit and stop all running services
        if self._measuring_active:
            self._value_parser(expect_reponse=False,
                               cmd="App", p1="stopMeasuring")
        if self._sine_gen_active:
            self._value_parser(expect_reponse=False,
                               cmd="AppCmd", p1="StopSineGen")
        if self._monitoring_active:
            self._value_parser(expect_reponse=False,
                               cmd="startmonitoring", p1="false")
        if self._operator_functions_active:
            self._value_parser(expect_reponse=False,
                               cmd="stoppoperatorfunctionvalues")
        if self._operator_active:
            self._value_parser(expect_reponse=False,
                               cmd="AppCmd", p1="StopSineGen")
        if self._operator_results_active:
            self._value_parser(expect_reponse=False,
                               cmd="stopoperatorresults")

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
        """Method sends a command to the connected analyzer to start a maesuring process."""
        self._value_parser(cmd="AppCmd", p1="startMeasuring")
        self._measuring_active = True

    def start_sineGenerator(self, frequency: int, amplitude: Union[int, Amplitudes]) -> None:
        """Method to start sine wave generation with custom frequency and amplitude settings.

        .. warning:: Sine generator has to be already switched on!
        .. note::Note that you should consider that the sine generator needs a couple µs to start
        .. note::Reminder: Frequency range is limited by used sine generator

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
            (f" Desiered amplitude {amplitude} is not supported by. Please enter one of the following amplitudes to continue: {a}")
            NEWamp = input("Enter new sine amplitude:")
            NEWf = input("Enter new sine frequency:")
            self.start_sineGenerator(NEWf, NEWamp)

    def stop_sineGenerator(self) -> None:
        """Stops generating sine waves."""
        self._value_parser(cmd="AppCmd", p1="StopSineGen")

    def stop_measuring(self) -> None:
        """Method to stop current running measuring process."""
        self._value_parser(cmd="AppCmd", p1="stopMeasuring")
        self._measuring_active = False

    def set_process_comment(self, proc_comm: str) -> None:
        """Set a process comment for current selected process.

        Parsed string will be saved in database under entry: process.comment

        :param proc_comm: Text which should be seen and saved as process comment
        :type proc_comm: str
        """
        self._value_parser(cmd="AppCmd", p1="setprocesscomment", p2=proc_comm)

    def set_area_view(self, split: int) -> None:
        """Set analyzer view to a spit view with up to 4 different splitted proccess. Reversed process to change back to
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

    def save_area_view(self, tempalte_num: int) -> None:
        """Saves current area view settings under template number. Each area can be set different.

        :param tempalte_num: Storage number to save.
        :type tempalte_num: int
        """
        self._value_parser(
            cmd="AppCmd", p1="SaveAreaView", p2=tempalte_num)

    def load_area_view(self, tempalte_num: int) -> None:
        """Load presaved area view template.

        :param tempalte_num: Storage number to load.
        :type tempalte_num: int
        """
        self._value_parser(
            cmd="AppCmd", p1="LoadAreaView", p2=tempalte_num)

    # TODO: not working
    def load_simualtion_buffer(self, file_path: str, channel=Channels.CHANNEL_1) -> None:
        self._value_parser(cmd="AppCmd",
                           p1="SimulationBuffer", p2=f"{channel} {file_path}")

    # TODO: not working
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
        # channel nummer starts in this case by 1
        channel_number += 1
        # check params limits
        if not 0 <= gain < 4096 and not 0 <= count < 201 and not 0 <= delay:
            self.logger.error("Params out of bounds")
            raise ValueError("Params out of bounds")

        settings = {"cmd": "AppCmd", "p1": "Preamp",
                    "p2": f"channel {channel_number} pulsetest {gain} {count} {delay}"}
        self._value_parser(**settings)

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
        port_number += 1
        if not 0 <= gain < 4096 and not 0 <= count < 201 and not 0 <= delay:
            self.logger.error("Params out of bounds")
            raise ValueError("Params out of bounds")

        settings = {"cmd": "AppCmd", "p1": "Preamp",
                    "p2": f"channel {port_number} pulsetest {gain} {count} {delay}"}
        self._value_parser(**settings)

    # TODO: not working
    def frequency_test_port(self, port_number):
        port_number += 1
        self._value_parser(cmd="AppCmd", p1="Preamp",
                           p2=f"port {port_number} frqtest")

    def set_area_scale(self, area_number: int, scale: int = 500) -> None:
        """ Set scale of each view area. Avaible for splitted analyzer view and single view.
        In case of single view area_number equals one.

        Scale should be in range(10,1001)
        Area number should be in range(1,5), but is limited to current activitated area views.

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
        """Set colour scale for area view. Only avaible in area

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
                "Choosen key is out of bounds. Scale should be in range(10,401) and area number should be in range(1,5).")
            raise ValueError(
                "Choosen key is out of bounds. Scale should be in range(10,401) and area number should be in range(1,5).")

    def set_area_time_range(self, area_number: int, start_time: int, time_range: int) -> None:
        """ Set of shown time range for each area.

        :param area_number: Area which shold be addressed
        :type area_number: int
        :param start_time: Start point of time range in ms.
        :type start_time: int
        :param time_range: Range that will be shown from start_time in ms.
        :type time_range: int
        """
        self._value_parser(cmd="AppCmd", p1="SetAreaPosition",
                           p2=f"{area_number} {start_time} {time_range}")

    def load_process(self, process_number: int, start_time=0) -> None:
        """ Load and dispaly by process number.

        :param process_number: Process that will be loaded
        :type process_number: int
        :param start_time: Start time in ms, defaults to 0
        :type start_time: int, optional
        """
        self._value_parser(cmd="AppCmd", p1="LoadProcess",
                           p2=f"{process_number} {start_time}")

    def get_service_parameter(self, param_setting: str) -> str:
        """Get settings out of Service Parameter (Configuration->Settings->Parameter)
        .. note:: Only avaible for user level 8 or higher!

        :param param_setting: Service parameter that should be read
        :type param_setting: str
        :return: Current set service parameter value
        :rtype: str
        """
        settings = self._value_parser(cmd="appfunc", p1="GetServiceParameter",
                                      p2=param_setting)
        return settings.get("result")

    # TODO:Test
    def set_service_parameter(self, param_setting: str, param_value: any) -> None:
        """Set service parameter settings under Configuration->Settings->Parameter
        .. note:: Only avaible for user level 8 or higher!

        :param param_setting: Service parameter that should be set
        :type param_setting: str
        :param param_value: New value of choosen service parameter
        :type param_value: any
        """
        self._value_parser(cmd="appfunc", p1="setServiceParameter",
                           p2=f"{param_setting} {param_value}")
        self.logger.info(
            f"Service parameter {param_setting} is changed to {param_value}")
        # self._value_parser(cmd="appfunc", p1="SetServiceParameter",
        #                   p2=f"{param_name} {param_value} {param_class}")

    # TODO: find way to prove
    def send_analyzer_to_sleep(self, time=2000) -> None:
        """ Command to send Analyzer system in sleep mode.

        :param time: Time to sleep in ms, defaults to 2000
        :type time: int, optional
        """
        self._value_parser(cmd="AppCmd", p1="sysSleep", p2=time)
        self.logger.info("Analyzer tired. Analyzer sleep.")

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
        # TODO: kill
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
        """ Returns current process number (active buffer)

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
        .. warning:: Developer fucntion. No use without required knowledge.
        :param param_one: Setting which AppCmd should be used.
        :type param_one: str
        :param param_two: If needed second parameter to specify params used in AppCmd, defaults to None
        :type param_two: str, optional
        :raises TypeError: Type Check for second parameter, exception is raised if value is not equal to type str.
        """
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
        if kwargs:
            if kwargs.keys() in settings.keys():
                settings.update(kwargs)
            else:
                self.logger.error("Choosen Preamp setting is not exisiting.")
                raise KeyError("Choosen Preamp setting is not exisiting.")
        self._value_parser(**settings)

    def get_analyzer_versions(self) -> str:
        """Method to read out anlyzer version informations and return as string.

        :return: Informations out of info window in analyzer.
        :rtype: str
        """
        val = self._value_parser(cmd="getversions")
        # process response
        analyzer_info = val.get("v")
        while "\\n" in analyzer_info:
            analyzer_info = analyzer_info.replace("\\n", "\n")

        return analyzer_info

    def get_project_info(self) -> Dict:
        """Method to read out analyzer project informations as current used project ID/name or analyer version.

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

    def measuring_mode(self, mode: Union[bool, str]) -> None:
        """Start or stop a measurement. Additionally over mode-key there is the possibility to start monitoring mode.

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
        if self.translator[mode] == "true":
            self._measuring_active = True
        elif self.translator[mode] == "false":
            self._measuring_active = False
        elif self.translator[mode] == "monitor":
            self._monitoring_active = True

    def monitoring_mode(self, mode: Union[bool, str]) -> None:
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
        if self.translator[mode] == "true":
            self._monitoring_active = True
        elif self.translator[mode] == "false":
            self._monitoring_active = False

    def calc_max_amp_per_band(self, **kwargs) -> np.ndarray:
        """Method to calculate maximum amplitude per band. For futher information see default settings below.

        By entering a new value as **kwargs, you are able to change default values, which will be sended.

        Default settings:
        | Type                   | Key | kwargs    | Default value | Action                   |
        | ---------------------- | --------------- | ------------- | ------------------------ |
        #1    | Choose channel buffer    |
        | int|Channels           | channel         | Channel
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
        """ Loads the set test project."""
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
        """ Gets a dictionary with all measure positions and if used an energy value.

        :return: Measurepositions and their calculated energy value.
        :rtype: Dict
        """
        return self._value_parser(cmd="getmaxmeasurepositions")

    def get_preamp_hardware_info(self, preamp_port) -> str:
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
        # TODO: implementation arbitary
        """Start operator functions.

        :param mode: Function can start or end operator function by changing mode to a stopping key, defaults to "start". For more allowed keys look up translator dict
        :type mode: str, bool], optional
        """
        self._value_parser(cmd="startoperatorfunctionvalues",
                           p1=self.translator[mode])
        if self.translator[mode] == "true":
            self._operator_functions_active = True
        elif self.translator[mode] == "false":
            self._operator_functions_active = False

    def stop_operator_function(self) -> None:
        """Stop of running operator function."""
        self._value_parser(cmd="stoppoperatorfunctionvalues")
        self._operator_functions_active = False

    def set_serial_number(self, serial_number: int, process_number: int) -> None:
        """Setting serial number for arbitary process.

        Serial number is stored under in database under process.serial

        :param serial_number: Serial number thast should be set.
        :type serial_number: int
        :param process_number: Porcess which should be connected to serial.
        :type process_number: int
        """
        self._value_parser(cmd="AppCmd", p1="SetProcessSerial",
                           p2=f"{process_number} {serial_number}")

    def set_serial_number_pending_process(self, serial_number: int) -> None:
        """Setting serial number for next process.

        Serial number is stored under in database under process.serial

        :param serial_number: Serial number for next process
        :type serial_number: int
        """
        self._value_parser(cmd="setpendingserial", p1=serial_number)

    def set_comment_pending_process(self, comment: str) -> None:
        """Set process comment for pending process.

        Comment is saved in database under process.comment

        :param comment: Comment for next process.
        :type comment: str
        """
        self._value_parser(cmd="setpendingcomment", p1=comment)

    def set_comment_current_process(self, comment: str):
        # TODO: kill
        """ Sets comment for current activatet process.

        Similair to set_proces_comment but as JSON communication Server command.
        Comment is saved in database under process.comment

        :param comment: Process comment to set
        :type comment: str
        """
        self._value_parser(cmd="setcomment", p1=comment, quiet=False)

    # TODO: implementation arbitary
    def start_operator(self, operator_name: str, operator_command: str) -> None:
        """External start of existing operator by name.

        :param operator_name: Name of network operator that should start
        :type operator_name: str
        :param operator_command: _description_
        :type operator_command: str
        """
        self._value_parser(expect_response=False, cmd="startoperator",
                           p1=operator_name, p2=operator_command)
        self._operator_active = True

    # TODO: implementation arbitary
    def import_operators(self, operator_fielpath: str, force_load: str) -> None:
        """Import a local file on optimizer.
        .. warning:: not implemented
        :param operator_fielpath: Path to operator file that will be imported.
        :type operator_fielpath: str
        :param force_load: _description_
        :type force_load: str
        """
        self._value_parser(expect_response=False, cmd="importoperators",
                           p1=operator_fielpath, p2=force_load)

    def import_patterns(self, directory_path: str) -> None:
        # TODO: implementation arbitary
        """Import all pattern files from a optimizer local directory.

        :param directory_path: Directory path to patterns that will be imported.
        :type directory_path: str
        """
        self._value_parser(expect_response=False, cmd="importpatterns",
                           p1=directory_path)

    def start_operator_results(self, mode: Union[str, bool] = "enable") -> None:
        # TODO: implementation arbitary
        """Sets enable flag to send ot operator results if avaible. Results will be sended separately

        :param mode: Enables start or stops by "disable", defaults to "enable"
        :type mode: str, optional
        """
        self._value_parser(cmd="startoperatorresults",
                           p1=self.translator[mode])

        if self.translator[mode] == "true":
            self._operator_results_active = True
        if self.translator[mode] == "false":
            self._operator_results_active = False

    def stop_operator_results(self) -> None:
        # TODO: implementation arbitary
        """Sets disable flag to send operator results if avaible."""
        self._value_parser(cmd="stopoperatorresults")
        self._operator_results_active = False

    def get_io_input(self) -> int:
        """Current set I/O input register as integer appearance (converted from hex).

        :return: I/O input register as integer appearance
        :rtype: int
        """
        val = self._value_parser(cmd="readioin")
        return val.get("result")

    def get_io_output(self) -> int:
        """Returns set I/O output register as integer appearance of hexa state.

        :return: Set I/O output
        :rtype: int
        """
        val = self._value_parser(cmd="readioout")
        return val.get("result")

    def _shift_binary(self, original_bin: str) -> str:
        """Helper method to convert incomming binary to least significant digit on the right side
        :param original_bin: Incomming binary
        :type original_bin: str
        :return: Shifted binary
        :rtype: str
        """
        # Elias Version didn't worked
        #new_val = 0
        # for i in range(16):
        #    bit_state = (original_bin & (1 << i) >> i)
        #    print("bit state", bit_state)
        #    new_val = new_val | (bit_state << (16-i))

        # return new_val

        # Oli versoion
        # helper list
        new_val = [0] * len(original_bin)
        # save current val to shifted position in list
        for (i, bit) in enumerate(original_bin):
            new_val[len(new_val)-1-i] = bit
        # convert list to string
        return "".join(new_val)

    def _binary_to_hexa(self, binary_str: str) -> str:
        """ Formats incomming binary to hexa representation with leading zeros. And leading "0xf" term.

        :param binary_str: Binary that should be converted to hexa representation.
        :type binary_str: str
        :return: hexa representation
        :rtype: str
        """
        hexa = "0xf" + "{0:0>4x}".format(int(binary_str, 2))
        return hexa

    def set_simualted_io_input(self, io: str):
        """Set simulated I/O input register. I/0 input register can be set by inverted hexa (smallest significant right)
        or by giving in binary representation of seen bits set in I/O register.

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
        :type io: str
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

    def add_process_number_report_callback(self, callback) -> None:
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

    def remove_process_number_report_callback(self, callback) -> None:
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
        """ General syntax to start script function. Response is dependant on called function.

        .. warning:: Service function, should not be used without required kmowledge.
        :param function_name: Name of script function
        :type function_name: str
        :param function_param: Passed param to script function
        :type function_param: any
        :return: Standard analyzer response. Dict contains result of addressed function as str.
        :rtype: Dict
        """
        return self._value_parser(cmd="appfunc",
                                  p1=function_name, p2=function_param)

    def human_confirmation(self, process_IO=False, **kwargs) -> None:
        """ Send human confiramtion over current process. Score and comment can be parsed over kwargs.

        |------------------ kwargs ----------------|
        | comment | Human comment for confirmation |
        | score   | Score value for confirmation   |

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

    # TODO:test
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
        """Creates an automatic analyzer backup."""
        self._value_parser(cmd="AppCmd", p1="writeBackup")

    def reset_failstate(self) -> None:
        """ Reset analyzer failure state and activates I/O ready by this."""
        self._value_parser(cmd="AppCmd", p1="ResetFailstate")

    def _recognition_translator(self, cmd_recognition: str) -> str:
        """Private method to add sended cmd str "response".

        :param cmd_recognition: cmd string which needs to be changend.
        :type cmd_recognition: str
        :return: cmd string which will be sended by analyzer as response.
        :rtype: str
        """
        return "response" + cmd_recognition

    def _check_response(self, response):
        """Private method to check received response for value under key="ok". If value is True, response is approved.

        :param response: Response dict from analyzer to check.
        :type response: dict
        :raises AnalyzerSyntaxError: Raises if command could not be performed, due to false syntax or params out of bounds.
        """
        # rais exception if not performed right
        if response.get("ok") == False:
            self.logger.error(
                "Analyzer could not perform action: check log and documentation.")
            raise AnalyzerSyntaxError(
                "Analyzer could not perform action: check log and documentation.")

    def _send(self, command: Dict) -> None:
        """ Privat method to send commands to analyzer. Command will be encoded to bytestring.

        :param command: Command dict which should be sended to connected analyzer.
        :type command: Dict
        """
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


with AnalyzerCmd(ip="192.168.1.50", debug_mode=True) as opti:
    opti.write_to_database(5, "test")
    #opti.set_service_parameter("pFPGAVersion", 2)
