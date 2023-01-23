Changelog
*********
All notable changes to this project will be documented in this file simultaneously to implemented Git pipelines.

2.0.0
"""""

:Date: January 23, 2023

:AnalyzerVersion: ``QASS optimizer4D sysV11b (2022-05-18)``

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

* Custom role ``AnalyzerVersion`` now avaible as sphinx supported docstring type
  
  Example:
  ```
  :AnalyzerVersion: QASS optimizer4D sysV11b (2022-05-18)
  ```

Fixes
-----

* ``KeyBoardInterruption`` now properly raised
  
* Documentation typo in:
  
  .. py:method:: qass.tools.networking.analyzer_socket.AnalyzerRemote.set_multiplexer(args)

* Fix automatic set of MultiPreampInput after use of function. ``Subport`` keyword is now set to `-1` by default:
  
  .. automethod:: qass.tools.networking.analyzer_socket.AnalyzerRemote.set_multiplexer

Unreleased
""""""""""
Planned changes for next releases will be noted here. If you have any suggestions, please contact: okowollik@qass.net

* None
