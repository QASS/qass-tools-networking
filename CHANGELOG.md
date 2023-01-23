# Changelog

All notable changes to this project will be documented in this file simultaneously to inplemented Git pipelines.

## [3.0.0] - 2023-01-25

### Added

- Changelog file

- Class ExactSamplerates16Bit

- Class ExactSamplerates24Bit

- Function set_io_ouput(io_line: int, state: bool)

- Analyzer version - function - management

### Changed

- In function get_max_amp_per_band(channel=Channels.CHANNEL_1, create_plot_buffer: bool = True, __create_data_buffer__: bool = False, amplitude_type=SysAmplitudesType.AMPLITUDE_DEFAULT) -> ndarray keyword argument is changed to get_max_amp_per_band(self, channel=Channels.CHANNEL_1, create_plot_buffer: bool = True, __save_plot_buffer__: bool = False, amplitude_type=SysAmplitudesType.AMPLITUDE_DEFAULT) -> np.ndarray

- Classname Samplerates to Samplerates16Bit

- Return from get_preamp_info(self, preamp_port: Union[PreampPorts, int]) -> __tuple__ too get_preamp_info(self, preamp_port: Union[PreampPorts, int]) -> __Dict__

### Removed

- None

### Fixed

- KeyBoardInterruption Exception is now properly raised

- Documentation bug in set_multiplexer

- Bug in set_multiplexer(channel=Channels.CHANNEL_1, chp=ChannelPorts.CHANNEL_PORT_1, preampport=PreampPorts.PREAMP_PORT_1, fft=True, signal=False, samplerate=Samplerates16Bit.SAMPLERATE_1600_kHz, fftoversampling=FFTOversampling.FFT_OVERSAMPLING_8_TIMES, fftwindowing=FFTWindowing.FFT_WINDOWING_HANNING, fftlogarithmic=FFTLogarithmic.FFT_LOGARITHMIC_BASE_14, filter=True, gain=800, subport=0) -> None where Multiplexer were in MultiInputPreamp state after use of function

### Unreleased

Planned changes for next releases will be noted here. If you have any suggestions, please contact: okowollik@qass.net

- None
