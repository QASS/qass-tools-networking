from enum import Enum, IntEnum

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


class Channels(IntEnum):
    """ Available selection box choices for channel in multiplexer configuration that will be addressed""" 
    CHANNEL_1 = 0
    CHANNEL_2 = 1
    CHANNEL_3 = 2
    CHANNEL_4 = 3


class ChannelPorts(IntEnum):
    """ Available selection box choices for channel port in multiplexer configuration that will be addressed""" 
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
    """ Available selection box choices for preamplifier port in multiplexer configuration that will be addressed""" 
    PREAMP_PORT_1 = 0
    PREAMP_PORT_2 = 1
    PREAMP_PORT_3 = 2
    PREAMP_PORT_4 = 3
    PREAMP_PORT_5 = 4
    PREAMP_PORT_6 = 5
    PREAMP_PORT_7 = 6
    PREAMP_PORT_8 = 7


class Samplerates16Bit(IntEnum):
    """ Available selection box choices for used samplerate in multiplexer configuration""" 
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
    """ Available exact samplerates in Hz with 16 Bit ADC.

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
    """ Available exact samplerates in Hz with 24 Bit ADC.

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
    """ Available selection box choices for used oversampling in multiplexer configuration""" 
    FFT_OVERSAMPLING_2_TIMES = 1
    FFT_OVERSAMPLING_4_TIMES = 2
    FFT_OVERSAMPLING_8_TIMES = 3
    FFT_OVERSAMPLING_16_TIMES = 4
    FFT_OVERSAMPLING_32_TIMES = 5
    FFT_OVERSAMPLING_64_TIMES = 6
    NONE_FFT_OVERSAMPLING = 0


class FFTWindowing(IntEnum):
    """ Available selection box choices for used windowing function in multiplexer configuration""" 
    FFT_WINDOWING_HANNING = 0
    NONE_FFT_WINDOWING = 1


class FFTLogarithmic(IntEnum):
    """ Available selection box choices for displayed FFT logarithmic base in multiplexer configuration""" 
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
    NO_FFT_LOGARITHMIC_BASE = 0


class SysAmplitudesType(IntEnum):
    """ System amplitude types available in analyzer software. Helps to represent calculated
    maximum amplitudes in different styles.""" 
    AMPLITUDE_DEFAULT = 0
    #: Amplitude is original ADC output value from hardware
    AMPLITUDE_ADC_OUT = 1
    #: Amplitude is normalized energy value. (timedif x frqdif x normalized amplitude)
    AMPLITUDE_NORM_ENERGY = 2
    #: Amplitude normalized to 1 as full ADC value:
    AMPLITUDE_NORM_ONE = 3
    AMPLITUDE_MILLI_VOLT = 4
    AMPLITUDE_MICRO_VOLT = 5


class AreaViews(IntEnum):
    """ Available view possibilities in analyzer area view.""" 
    VIEW_1 = 1
    VIEW_2 = 2
    VIEW_3 = 3
    VIEW_4 = 4


class SysSettingsClass(IntEnum):
    """ Predefined system settings classes.""" 
    
    #: Wird zur Zeit auch per Voreinstellung in "./config/QASS/analyzer.conf" gespeichert
    NO_CLASS = 0 	
    #: Das ist die Default-Klasse für pVars, die in einem VarSet untergebracht sind
    VAR_SET_CLASS = 1
    #: Die Variable enthält System-Einstellungen, die später auch in ".config/QASS" gespeichert werden
    SYSTEM_CONFIG = 2
    USER_CONFIG = 3     # doc: Wird in "./config/QASS/analyzer.conf" in der USER Sektion gespeichert
    GLOBAL_TRIGGER_CONFIG = 4     # doc: Globale Triggereinstellung
    GLOBAL_MEASURE_CONFIG = 5     # doc Globale MeasureConfig Einstellung
    MEASURE_CONFIG = 6     # doc: MeasureConfig Struktur
    CLIENT_CONFIG = 7     # doc: Branding und application Start Einstellungen
    VIDEO_CONFIG = 8     # doc: This is a configuration Setting for a CAM or VideoRecording
    COLOR_CONFIG = 9
    NETWORK_CONFIG = 10    # doc: A network configuration
    FPGA_CONFIG = 11
    PR_SEARCH_CONFIG = 12
    GUI_CONFIG = 13    # doc: global GUI and StyleSheet settings
    SIM_BUFFER_CONFIG = 14    # doc: Configuration of Simulation files
    BACKUP_CONFIG = 15  # doc: Configuration for backups and automatic backups


class MultiPreampInput(IntEnum):
    """ Enums for Multi Input Preamps. The numeration starts on the uppest left input and goes rowise from left to right, too the lowest input (right side).""" 
    NONE_MULTI_INPUT = 999  # doc: Just a flag, to not use any input values. No internal anlyzer link!
    MULTI_INPUT_1 = 0
    MULTI_INPUT_2 = 1
    MULTI_INPUT_3 = 2
    MULTI_INPUT_4 = 3
    MULTI_INPUT_5 = 4
    MULTI_INPUT_6 = 6

class PreampType(IntEnum):
    """ Serial Number Ring for supported Preamp Types."""
    PASSIVE = 2023
    ACTIVE  = 2113

class AnalyzerRunStatus(IntEnum):
    """Run status of Analyzer Software"""
    IDLE = 0
    MEASURE = 1
    REPLAY = 2
    SCOPE = 3
    MONITOR = 4
    CLEANUP = 5
    LOAD = 6
    SAVE = 7
    FAILSTATE = 8
    SIMULATE = 9
    PAUSED = 10
    SELFTEST = 11

run_status_mapping = {status.name: status for status in AnalyzerRunStatus}
