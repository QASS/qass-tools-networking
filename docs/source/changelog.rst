==========
Changelog
==========

.. _changelog_networking:

Unreleased
==========
Planned changes for next releases will be noted here. If you have any suggestions, please contact: okowollik@qass.net

- Set io as line in set_simulated_io_input(args) 
- Save project function


3.3.1
=====
:Date: May 13, 2024

:AnalyzerVersion: V2.03.99.13 optimierter Aufbau (11 Mär 2024)

:Contributor: Oliver Kowollik

.. tab-set::
  .. tab-item:: New Features
      
    - Expert keyword argument for :mod:`AnalyzerRemote.start_sineGenerator()` method


3.3.0
=====
:Date: April 11, 2024

:AnalyzerVersion: V2.03.99.13 optimierter Aufbau (11 Mär 2024)

:Contributor: Oliver Kowollik

.. tab-set::
  .. tab-item:: New Features
      
    - Added a contribution guideline
    - New :mod:`AnalyzerRemote.set_frequency_mask()` method
    - New :mod:`AnalyzerRemote.use_frequency_mask()` method
    - New :mod:`AnalyzerRemote.teach_frequency_mask()` method
    - New :mod:`AnalyzerRemote.restart_analyzer()` method
    - New :mod:`AnalyzerRemote.start_shell_program()` method
    - New :mod:`AnalyzerRemote.remove_delayed_trigger()` method
    - New :mod:`AnalyzerRemote.free_buffer_datablocks()` method
    - New :mod:`AnalyzerRemote.set_python_init_hook()` method
    - New :mod:`AnalyzerRemote.set_sys_pengui_config()` method
    - New :mod:`AnalyzerRemote.set_failstate()` method
    - New :mod:`AnalyzerRemote.set_sys_python_path()` method
    - New :mod:`AnalyzerRemote.set_frq_mask_container_visible()` method
    - New :mod:`AnalyzerRemote.set_appvar_container_visible()` method
    - New :mod:`AnalyzerRemote.set_GUI_tools_activated()` method
    - New :mod:`AnalyzerRemote.set_classic_menu_view()` method
    - New :mod:`AnalyzerRemote.set_trigger_list()` method


  .. tab-item:: Fixes

    - Paths are now supported to contain whitespaces
    - Fix :mod:`AnalyzerRemote.set_process_comment` method. A process number is now needed as first arguemnt.



3.2.0
=====
:Date: November 15, 2023

:AnalyzerVersion: V2.03.30.00 (31 Mai 2023)

:Contributor: Oliver Kowollik

.. tab-set::
  .. tab-item:: New Features
      
    - New custom exception class :class:`ConnectionError`
    - Add service to auto stopp certain remote startet methods parsing command list to constructor under `auto_stop`

  .. tab-item:: Changes

    - Extend :mod:`AnalyzerRemote.reset_failstate` method by keywords to set application idle and clear notifcation pop-ups

3.1.0 
======

.. tab-set::
  .. tab-item:: New Features
  
    - New :mod:`AnalyzerRemote.write_preamp_s_value()` method
    - New :mod:`AnalyzerRemote.write_preamp_s_value()` method
    - New :mod:`AnalyzerRemote.load_project()` method
    - New :mod:`AnalyzerRemote.load_project_by_IOid()` method
    - New :mod:`AnalyzerRemote.detect_preamp()` method
    - New :mod:`AnalyzerRemote.get_preamp_firmware()` method
    - New :mod:`AnalyzerRemote.reboot_preamp()` method
    - Additional convert flag to :mod:`AnalyzerRemote.get_preamp_info()`
    - New IntEnum :class:`PreampTypes()` class 
    - Add dependancies

  .. tab-item:: Changes

    - Documentation :mod:`AnalyzerRemote.get_preamp_info()`
    - Rework :class:`ReceiverThread` handling

  .. tab-item:: Fixes
  
    - Bug in :class:`ReceiverThread`


3.0.0
======

:Date: May 10, 2023

:AnalyzerVersion: V2.03.22.90 (10 Juni 2022)

:Contributor: Oliver Kowollik


.. tab-set::
  .. tab-item:: New Features

    - Timeout for each queue item
    - Most methods from :class:`AnalyzerRemote` now contain a ``custom_timeout`` keywordargument, which overwirittes the timeout control for each queue block
    - Constructor contains new keywordargument ``timeout`` for setting global timeout, default is 2
    - New custom :class:`ReceivingThreadError` Exception class added
    - New :mod:`AnalyzerRemote.open()` method to use socket without a context manager
    - New :mod:`AnalyzerRemote.close()` method to use socket without a context manager

  .. tab-item:: Fixes

    - Documentation :mod:`AnalyzerRemote.get_io_input()`
    - Documentation :mod:`AnalyzerRemote.get_io_output()`

  .. tab-item:: Removed
    
    - Custom exception :class:`ConnectionError` removed

  .. tab-item:: Changes

    - Custom exception ``AnalyzerSyntaxError`` to :class:`AnalyzerError`

2.1.1
======
:Date: May 05, 2023

:AnalyzerVersion: V2.03.22.90 (10 Juni 2022)

:Contributor: Oliver Kowollik

.. tab-set::
  .. tab-item:: Fixes

    - Update documentation of :class:`AnalyzerSSH`
    - In :class:`AnalyzerRemote` Deactivation of SineGen as Flag is raised properly 

  .. tab-item:: Changes

    - Optimized range control in :mod:`AnalyzerRemote.start_sineGenerator()` 
    - Changend name of :mod:`AnalyzerRemote.AreaViews()` attributes
    - New package requirement of paramiko


2.1.0
======
:Date: March 29, 2023

:AnalyzerVersion: V2.03.22.90 (10 Juni 2022)

:Contributor: Oliver Kowollik

.. tab-set::
  .. tab-item:: New Features

    - New tool added for SSH linux terminal control in python context: :class:`AnalyzerSSH`

  .. tab-item:: Fixes

    - Update documentation

2.0.2
======
:Date: January 23, 2023

:AnalyzerVersion: V2.03.22.90 (10 Juni 2022)

:Contributor: Oliver Kowollik

.. tab-set::
  .. tab-item:: New Features

    - Custom role ``Contributor`` now avaible as sphinx supported docstring type
      
      Example:
      ```
      :Contributor: Oliver Kowollik
      ```
  
  .. tab-item:: Fixes

    - Changelog entries extended by :mod:`Contributor` Tag

2.0.1
======
:Date: January 23, 2023

:AnalyzerVersion: V2.03.22.90 (10 Juni 2022)

:Contributor: Oliver Kowollik

.. tab-set::
  .. tab-item:: New Features

    - Custom role ``AnalyzerVersion`` now avaible as sphinx supported docstring type
  
      Example:
      ```
      :AnalyzerVersion: QASS optimizer4D sysV11b (2022-05-18)
      ```

2.0.0
======

:Date: January 23, 2023

:AnalyzerVersion: V2.03.22.90 (10 Juni 2022)

:Contributor: Oliver Kowollik

.. tab-set::
  .. tab-item:: New Features

    - :class:`ExactSamplerates16Bit`
    - :class:`ExactSamplerates24Bit`
    - :class:`AnalyzerRemote.set_io_ouput()`
    
  .. tab-item:: New Features

    - Keyword changed from ``create_data_buffer`` to ``save_plot_buffer`` in :mod:`AnalyzerRemote.get_max_amp_per_band()`
    - Classname change from ``Samplerates`` to :class:`Samplerates16Bit`
    - :mod:`AnalyzerRemote.get_preamp_info()` Changes return value from ``Tuple`` to ``Dict``:

  .. tab-item:: New Features

    - Exception :class:`KeyBoardInterruption` now properly raised
    - Documentation typo in :mod:`AnalyzerRemote.set_multiplexer()`
    - Fix automatic set of MultiPreampInput after use of function :mod:`AnalyzerRemote.set_multiplexer()`
      ``Subport`` keyword is now set to ``-1`` by default
      

