Unreleased
""""""""""
Planned changes for next releases will be noted here. If you have any suggestions, please contact: okowollik@qass.net

* Set io as line in set_simulated_io_input(args) 
* Save project function

2.1.0
"""""
:Date: February 06, 2023

:AnalyzerVersion: ``QASS optimizer4D sysV11b (2022-05-18)``

:Contributor: Oliver Kowollik

New Features
------------
* New tool added for SSH linux temrinal control in python context:
  
  .. autoclass:: qass.tools.networking.analyzer_ssh.AnalyzerSSH


2.0.2
"""""
:Date: January 23, 2023

:AnalyzerVersion: ``QASS optimizer4D sysV11b (2022-05-18)``

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
* Changelog entries extended by Contributor Tag

2.0.1
"""""
:Date: January 23, 2023

:AnalyzerVersion: ``QASS optimizer4D sysV11b (2022-05-18)``

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

:AnalyzerVersion: ``QASS optimizer4D sysV11b (2022-05-18)``

:Contributor: Oliver Kowollik

Changes
-------
* Keyword changed from ``create_data_buffer`` to ``save_plot_buffer``:
  
  .. automethod:: qass.tools.networking.analyzer_socket.AnalyzerRemote.get_max_amp_per_band

* Classname change from `Samplerates` to:
  
  .. autoclass:: qass.tools.networking.analyzer_socket.Samplerates16Bit

* Changes return value from `Tuple` to `Dict`:
  
  .. automethod:: qass.tools.networking.analyzer_socket.AnalyzerRemote.get_preamp_info


New Features
------------
.. autoclass:: qass.tools.networking.analyzer_socket.ExactSamplerates16Bit 

.. autoclass:: qass.tools.networking.analyzer_socket.ExactSamplerates24Bit

.. automethod:: qass.tools.networking.analyzer_socket.AnalyzerRemote.set_io_ouput


Fixes
-----

* ``KeyBoardInterruption`` now properly raised
  
* Documentation typo in:
  
  .. py:method:: qass.tools.networking.analyzer_socket.AnalyzerRemote.set_multiplexer(args)

* Fix automatic set of MultiPreampInput after use of function. ``Subport`` keyword is now set to `-1` by default:
  
  .. automethod:: qass.tools.networking.analyzer_socket.AnalyzerRemote.set_multiplexer

