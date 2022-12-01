In the example we build a remote connection (TCP) to an Analyzer4D software and send a command to start a measuring.

.. code-block:: python
    :linenos:

    from qass.tools.networking.analyzer_socket import AnalyzerRemote
     
    ip_address = "111.111.1.111"
    with AnalyzerRemote(ip_address) as opti:
        opti.start_measuring()