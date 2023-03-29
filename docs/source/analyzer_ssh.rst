Overview
********

The :class:`AnalyzerSSH` class extends the possible remote control of an Optimizer4D via python context. The provided methods are msotly designed to extract characteristical values to identify hardware type and status of connected machine.

Examples
********

Example 1: Initializing
"""""""""""""""""""""""
Initializing SSH connection via python context to an connected Linux-based system, in order to send and receive terminal commands.

.. code-block:: python
   :linenos:

        from qass.tools.networking.analyzer_ssh import AnalyzerSSH

        ip_address = "111.111.1.111"
        with AnalyzerSSH(ip_address) as opti_client:
            ....

Example 2: Debug mode
""""""""""""""""""""""
Example two shows an easy way to debug system in case you need some more detailed information how to process incomming responses. By activating debug mode system provide more detailed information to sys.stdout.

.. code-block:: python
    :linenos:

    from qass.tools.networking.analyzer_ssh import AnalyzerSSH   
    
    with AnalyzerSSH("111.111.1.111", debug_mode=True) as opti_client:
        ....

Example 3.1: Access reader functionalities
""""""""""""""""""""""""""""""""""""""""""
Simple example how to access main functionalities.
    
.. code-block:: python
    :linenos:

    from qass.tools.networking.analyzer_ssh import AnalyzerSSH

    with AnalyzerSSH("111.111.1.111") as opti_client:
        info_dict = opti_client.get_all_infos()
        opti_client.export_to_json(info_dict)

Example 3.2: Access reader functionalities
""""""""""""""""""""""""""""""""""""""""""
Same result but now unscrambled into the specific parts. Could be an advantage for understanding programm mechanismen.
    
.. code-block:: python
    :linenos:

    from qass.tools.networking.analyzer_ssh import AnalyzerSSH

    with AnalyzerSSH("111.111.1.111") as opti_client:
        opti_client._detect_harddrives()
        opti_client.logger.info(
            f"Automatic detection of one systemplate and {len(opti_client.datapaths)} dataplates completed.")
        opti_client.check_smartctl()
        opti_client._get_machine_info()
        opti_client._get_systemdrive_info()
        opti_client._get_datadrive_info()
        opti_client.logger.info("All data read and ready to export.")
        opti_client.export_to_json(opti_client.all_infos)
        opti_client.logger.info("Export completed")        

Example 3.3: Access reader functionalities
""""""""""""""""""""""""""""""""""""""""""
Same result but in third way to have see computing in progress bar.
    
.. code-block:: python
    :linenos:

    from qass.tools.networking.analyzer_ssh import AnalyzerSSH

    with AnalyzerSSH("111.111.1.111") as opti_client:
        processes = [opti_client._detect_harddrives, opti_client.check_smartctl,
        opti_client._get_machine_information, opti_client._get_systemdrive_info, opti_client._get_datadrive_info]
        with tqdm(desc="Progress of computing", total=len(processes)) as bar:
                for process_step in processes:
                        process_step()
                        bar.update()
        opti_client.logger.info("All data read and ready to export.")
        opti_client.export_to_json(opti_client.all_infos)
        opti_client.logger.info("Export completed")

Example 4: Standalone
"""""""""""""""""""""
Usage as standalone application.
    
.. code-block:: python
    :linenos:

    from qass.tools.networking.analyzer_ssh import AnalyzerSSH
    
    if __name__ == "__main__":
        with AnalyzerSSH("111.111.1.111") as opti_client:
                info_dict = opti_client.get_all_infos()
                opti_client.export_to_json(info_dict)

AnalyzerSSH
************
.. autoclass:: qass.tools.networking.analyzer_ssh.AnalyzerSSH
        :members: