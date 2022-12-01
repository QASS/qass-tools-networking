Overview
********

The :class:`AnalyzerCmd` class can be used to open a TCP socket to a running Analyzer4D software for remote control.
It can be used to monitor running processes or start measure protocols on remote computers. Additionally it can be used to 

Examples
********
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

.. autoclass:: qass.tools.networking.analyzer_socket.Amplitudes
        :members:

.. autoclass:: qass.tools.networking.analyzer_socket.Channels
        :members:

.. autoclass:: qass.tools.networking.analyzer_socket.ChannelsPorts
        :members:

.. autoclass:: qass.tools.networking.analyzer_socket.PreampPorts
        :members:

.. autoclass:: qass.tools.networking.analyzer_socket.Samplerates
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