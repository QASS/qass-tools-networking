Unreleased
""""""""""
Planned changes for next releases will be noted here. If you have any suggestions, please contact: okowollik@qass.net

* Set io as line in set_simulated_io_input(args) 
* Save project function

3.2.0
"""""
:Date: November 15, 2023

:AnalyzerVersion: V2.03.30.00 (31 Mai 2023)

:Contributor: Oliver Kowollik

``AnalyzerRemote``

New Features
------------
* New custom exception class :class:`ConnectionError`

Changes
------------
* Add service to auto stopp certain remote startet methods parsing command list to constructor under `auto_stop`

Fixes
------
* Errorhandling is now optimized for more clearity
* Fix :mod:`qass.tools.networking.analyzer_socket.set_process_comment` method. A process number is now needed as first arguemnt.

3.1.0
"""""
:Date: July 10, 2023

:AnalyzerVersion: V2.03.30.00 (31 Mai 2023)

:Contributor: Oliver Kowollik

``AnalyzerRemote``

New Features
------------
* New :mod:`qass.tools.networking.analyzer_socket.write_preamp_s_value` method
* New :mod:`qass.tools.networking.analyzer_socket._write_preamp_eeprom` method
* New :mod:`qass.tools.networking.analyzer_socket.write_preamp_s_value` method
* New :mod:`qass.tools.networking.analyzer_socket.load_project` method
* New :mod:`qass.tools.networking.analyzer_socket.load_project_by_IOid` method
* New :mod:`qass.tools.networking.analyzer_socket.detect_preamp` method
* New :mod:`qass.tools.networking.analyzer_socket.get_preamp_firmware` method
* New :mod:`qass.tools.networking.analyzer_socket.reboot_preamp` method
* Additional convert flag to :mod:`qass.tools.networking.analyzer_socket.get_preamp_info`
* New IntEnum :mod:`qass.tools.networking.analyzer_socket.PreampTypes` class 
* Add dependancies

Fixes
------
* Documentation :mod:`qass.tools.networking.analyzer_socket.get_preamp_info`
* Bug in Receiver Thread
* Rework ReceiverThread handling



3.0.0
"""""
:Date: May 10, 2023

:AnalyzerVersion: V2.03.22.90 (10 Juni 2022)

:Contributor: Oliver Kowollik

``AnalyzerRemote``

New Features
------------
* Timeout for each queue item
* Most methods from :mod:`qass.tools.networking.analyzer_socket` now contain a ``custom_timeout`` keywordargument, which overwirittes the timeout control for each queue block
* Constructor contains new keywordargument ``timeout`` for setting global timeout, default is 2
* New custom :mod:`qass.tools.networking.analyzer_socket.ReceivingThreadError` Exception class added
* New :mod:`qass.tools.networking.analyzer_socket.open` method to use socket without a context manager
* New :mod:`qass.tools.networking.analyzer_socket.close` method to use socket without a context manager

Fixes
------
* Documentation :mod:`qass.tools.networking.analyzer_socket.get_io_input`
* Documentation :mod:`qass.tools.networking.analyzer_socket.get_io_output`

Removed
-------
* Custom exception :mod:`qass.tools.networking.analyzer_socket.ConnectionError` removed

Changes
-------
* Custom exception ``AnalyzerSyntaxError`` to :mod:`qass.tools.networking.analyzer_socket.AnalyzerError`

2.1.1
"""""
:Date: May 05, 2023

:AnalyzerVersion: V2.03.22.90 (10 Juni 2022)

:Contributor: Oliver Kowollik

Fixes
-----
* Update documentation of :mod:`qass.tools.networking.analyzer_ssh.AnalyzerSSH`
* Deactivation of SineGen is running Flag is raised properly 

Changes
-------
* Optimized range control in :mod:`qass.tools.networking.analyzer_socket.AnalyzerRemote.start_sineGenerator` 
* Changend name of :mod:`qass.tools.networking.analyzer_socket.AreaViews` attributes
* New package requirement of paramiko


2.1.0
"""""
:Date: March 29, 2023

:AnalyzerVersion: V2.03.22.90 (10 Juni 2022)

:Contributor: Oliver Kowollik

Fixes
-----
* Update documentation

New Features
------------
* New tool added for SSH linux terminal control in python context: :mod:`qass.tools.networking.analyzer_ssh.AnalyzerSSH`

2.0.2
"""""
:Date: January 23, 2023

:AnalyzerVersion: V2.03.22.90 (10 Juni 2022)

:Contributor: Oliver Kowollik

New Features
------------
* Custom role ``Contributor`` now avaible as sphinx supported docstring type
  
  Example:
  ```
  :Contributor: Oliver Kowollik
  ```

Fixes
-----
* Changelog entries extended by :mod:`Contributor` Tag

2.0.1
"""""
:Date: January 23, 2023

:AnalyzerVersion: V2.03.22.90 (10 Juni 2022)

:Contributor: Oliver Kowollik

New Features
------------
* Custom role ``AnalyzerVersion`` now avaible as sphinx supported docstring type
  
  Example:
  ```
  :AnalyzerVersion: QASS optimizer4D sysV11b (2022-05-18)
  ```

2.0.0
"""""

:Date: January 23, 2023

:AnalyzerVersion: V2.03.22.90 (10 Juni 2022)

:Contributor: Oliver Kowollik

Changes
-------
* Keyword changed from ``create_data_buffer`` to ``save_plot_buffer`` in :mod:`qass.tools.networking.analyzer_socket.AnalyzerRemote.get_max_amp_per_band`
* Classname change from ``Samplerates`` to :mod:`qass.tools.networking.analyzer_socket.Samplerates16Bit`
* :mod:`qass.tools.networking.analyzer_socket.AnalyzerRemote.get_preamp_info` Changes return value from ``Tuple`` to ``Dict``:

New Features
------------
* :mod:`qass.tools.networking.analyzer_socket.ExactSamplerates16Bit`
* :mod:`qass.tools.networking.analyzer_socket.ExactSamplerates24Bit`
* :mod:`qass.tools.networking.analyzer_socket.AnalyzerRemote.set_io_ouput`

Fixes
-----

* :mod:`qass.tools.networking.analyzer_socket.KeyBoardInterruption` now properly raised
* Documentation typo in :mod:`qass.tools.networking.analyzer_socket.AnalyzerRemote.set_multiplexer`
* Fix automatic set of MultiPreampInput after use of function. ``Subport`` keyword is now set to ``-1`` by default:

