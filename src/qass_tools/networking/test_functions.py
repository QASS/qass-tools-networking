from analyzer_socket import AnalyzerCmd, PreampPorts
from time import sleep


def bla(response):
    print("I did it")


with AnalyzerCmd("192.168.1.50", debug_mode=True) as opti:
    # opti.import_trigger_list(
    #    "/home/opti/2021_09_16_template_Triggerlist_Straightening_V_2.0.ini", append=True)
    opti.import_project_archive(
        "/home/opti/CIS2_ExportTest.tar.gz", "import_test2", overwrite=True)
