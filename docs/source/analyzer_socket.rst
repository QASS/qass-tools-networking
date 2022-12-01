Overview
********

The :class:`AnalyzerCmd` class can be used to open a TCP socket to a running Analyzer4D software for remote control.
It can be used to monitor running processes or start measure protocols on remote computers. Additionally it can be used to 

Example
*******
In the example we build a remote connection (TCP) to an Analyzer4D software and send a command to start a measuring.

.. code-block:: python
    :linenos:

    from qass.tools.networking.analyzer_socket import AnalyzerRemote
     
    ip_address = "111.111.1.111"
    with AnalyzerRemote(ip_address) as opti:
        opti.start_measuring()


AnalyzerRemote
******
.. autoclass:: qass.tools.networking.analyzer_socket.AnalyzerRemote
        :members:


Analyzer Helper Classes
******

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