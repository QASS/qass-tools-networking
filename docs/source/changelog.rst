Unreleased
""""""""""
Planned changes for next releases will be noted here. If you have any suggestions, please contact: okowollik@qass.net

* Set io as line in set_simulated_io_input(args) 
* Save project function

2.2.0
"""""
:Date: May 10, 2023

:AnalyzerVersion: QASS optimizer4D sysV11b (2022-05-18)

:Contributor: Oliver Kowollik

``AnalyzerRemote``

New Features
------------
* Global timeout for each queue item
* Every method from :mod:`qass.tools.networking.analyzer_socket` now contains a ``custom_timeout`` keywordargument, which overwirittes the timeout control for each queue block
* New custom :mod:`qass.tools.networking.analyzer_socket.ReceivingThreadError` Exception class added

Fixes
------
* Documentation :mod:`qass.tools.networking.analyzer_socket.get_io_input`
* Documentation :mod:`qass.tools.networking.analyzer_socket.get_io_output`

Removed
-------
* Custom exception :mod:`qass.tools.networking.analyzer_socket.ConnectionError` removed
* Custom exception :mod:`qass.tools.networking.analyzer_socket.AnalyzerSyntaxError` removed

2.1.1
"""""
:Date: May 05, 2023

:AnalyzerVersion: QASS optimizer4D sysV11b (2022-05-18)

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

:AnalyzerVersion: QASS optimizer4D sysV11b (2022-05-18)

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

:AnalyzerVersion: QASS optimizer4D sysV11b (2022-05-18)

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

:AnalyzerVersion: QASS optimizer4D sysV11b (2022-05-18)

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

:AnalyzerVersion: QASS optimizer4D sysV11b (2022-05-18)

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

