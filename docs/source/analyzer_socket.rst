Overview
********

The :class:`AnalyzerRemote` class can be used to open a TCP socket to a running Analyzer4D software for remote control.
It can be used to monitor running processes or start measuring protocols on remote computers. Available functions are supported since Analyzer version: ``QASS optimizer4D sysV11b (2022-05-18)`` or higher. A higher required Analyzer version will be documented for each function as note.  

Examples
********

Example 1: Initalizing
""""""""""""""""""""""
In the first example we build a remote connection (TCP) to an Analyzer4D software and send a command to start a measuring.

.. code-block:: python
   :linenos:

        from qass.tools.networking.analyzer_socket import AnalyzerRemote

        ip_address = "111.111.1.111"
        with AnalyzerRemote(ip_address) as opti:
            opti.start_measuring()

Example 2: Access functionalities
""""""""""""""""""""""""""""""""""
Simple example how to intialize a socket connection to the optimizer and have access to analyzer functions.
    
.. code-block:: python
    :linenos:

    from qass.tools.networking.analyzer_socket import AnalyzerRemote, Channels, Amplitudes
    import time

    with AnalyzerRemote("111.111.1.111") as opti:
        opti.set_multiplexer(channel=Channels.CHANNEL_1)
        info = opti.get_project_info()
        print(info)
        opti.set_multiplexer(gain=800)

        proc = opti.get_process_number()

        opti.set_process_comment("Hey ich bims, eins Kommentar")

        opti.start_measuring()
        opti.start_sineGenerator(frequency=500, amplitude=Amplitudes.AMP_191_mV)
        time.sleep(2)
        opti.stop_sineGenerator()
        opti.stop_measuring()

Example 3: Debug mode
""""""""""""""""""""""
Example three shows an easy way to debug system in case you need some more detailed information how to process incomming responses. By activating debug mode system will be printing out much more sending and receiving information to stdout.

.. code-block:: python
    :linenos:

    from qass.tools.networking.analyzer_socket import AnalyzerRemote
    import time    
    
    with AnalyzerRemote("192.168.2.67", debug_mode=True) as opti:
        info = opti.get_project_info()
        print(info)

Example 4: Callbacks
""""""""""""""""""""

Example to show how to use report function with an easy callback.

.. code-block:: python
    :linenos:

    from qass.tools.networking.analyzer_socket import AnalyzerRemote
    
    def own_callback_example(result):
        """Function that prints "I/O state changed" everytime it does. Callback function always becomes response as arg. In this case response is used as event. Evertime this event happens print command will happen."""
        if result:
                print("I/O state changed")
    
    with AnalyzerRemote(ip="192.168.2.67") as opti:
        # Start report
        opti.add_io_report_callback(own_callback_example)
        # Do something
        #
        # stop report automatically without active callback
        opti.remove_io_report_callback(own_callback_example)

Example 5: Set analyzer settings
"""""""""""""""""""""""""""""""""

Example to automatically define Analyzer4D settings.

    .. code-block:: python
        :linenos:
    
        from qass.tools.networking.analyzer_socket import AnalyzerRemote, PreampPorts
        
        with AnalyzerRemote(ip="192.168.2.67") as opti:
            project_dict = opti.get_project_info()
            current_state = opti.get_service_parameter("pFPGAVersion")
            if current_state is not 2:
                opti.set_service_parameter("pFPGAVersion", 2)
            opti.pulsetest_port(PreampPorts.PREAMP_PORT_1)
            opti.import_patterns("/my/local/directory/")

AnalyzerRemote
**************
.. autoclass:: qass.tools.networking.analyzer_socket.AnalyzerRemote
        :members:


Analyzer Helper Classes
***********************
.. autoclass:: qass.tools.networking.analyzer_socket.Amplitudes
        :members:

.. autoclass:: qass.tools.networking.analyzer_socket.Channels
        :members:

.. autoclass:: qass.tools.networking.analyzer_socket.ChannelsPorts
        :members:

.. autoclass:: qass.tools.networking.analyzer_socket.PreampPorts
        :members:

.. autoclass:: qass.tools.networking.analyzer_socket.Samplerates16Bit
        :members:

.. autoclass:: qass.tools.networking.analyzer_socket.ExactSamplerates16Bit
        :members:

.. autoclass:: qass.tools.networking.analyzer_socket.ExactSamplerates24Bit
        :members:

.. autoclass:: qass.tools.networking.analyzer_socket.FFTOversampling
        :members:

.. autoclass:: qass.tools.networking.analyzer_socket.FFTWindowing
        :members:

.. autoclass:: qass.tools.networking.analyzer_socket.FFTLogarithmic
        :members:

.. autoclass:: qass.tools.networking.analyzer_socket.SysAmplitudesType
        :members:

.. autoclass:: qass.tools.networking.analyzer_socket.AreaViews
        :members:

.. autoclass:: qass.tools.networking.analyzer_socket.SysSettingsClass
        :members:

.. autoclass:: qass.tools.networking.analyzer_socket.MultiPreampInput
        :members:

.. autoclass:: qass.tools.networking.analyzer_socket.ConnectionError
        :members:

.. autoclass:: qass.tools.networking.analyzer_socket.NoneRegistrationError
        :members:

.. autoclass:: qass.tools.networking.analyzer_socket.AnalyzerSyntaxError
        :members:

.. include:: changelog.rst
