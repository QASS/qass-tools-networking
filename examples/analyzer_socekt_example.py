import time
from qass_tools.networking import analyzer_socket as socket


with socket.AnalyzerCmd(ip="192.168.2.67") as opti:
    opti.set_preamp(channel=3)
    info = opti.get_info()
    print(info)
    opti.set_preamp(gain=800)

    proc = opti.get_process_number()

    opti.set_process_comment("Hey ich bims, eins Kommentar")

    opti.start_measuring()
    opti.start_sineGenerator(500, 191)
    time.sleep(2)
    opti.stop_sineGenerator()
    opti.stop_measuring()