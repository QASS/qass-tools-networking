Overview
********

The :class:`AnalyzerCmd` class can be used to open a TCP socket to a running Analyzer4D software for remote control.
It can be used to monitor running processes or start measure protocols on remote computers. Additionally it can be used to 

Example
*******
In the example we provide the path to a buffer file to the :class:`Buffer` class and use the with-statement to open it to read the process number.

.. code-block:: python
    :linenos:

     from qass.tools.analyzer.buffer_parser import Buffer

     buffer_file = "path/to/my/buffer_file"
     with Buffer(buffer_file) as buff:
        print(buff.process)


Buffer
******
