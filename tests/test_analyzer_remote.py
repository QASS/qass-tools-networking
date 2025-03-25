from qass.tools.networking.analyzer_socket import AnalyzerRemote ,Amplitudes,PreampPorts, AnalyzerError
import time
import pytest

IP = "192.168.2.134"
PORT = 17000

"""
Found Bugs:
    -  "reportappvars" liefert im response keine res_id
    - "startoperatorfunctionvalues" always return 'ok' == True
    - Vorbedingung: add & remove appvar 'foo'. Danach liefert get_appvar('foo') 'ok' == True aber 'result' fehlt
    - "getversions" liefert kein 'ok' bug?
    - "getinfo" kein 'ok' bug?
    - "getmaxmeasurepositions" kein 'ok' kein resid...
    - Gibt es "stoppoperatorfunctionvalues" noch oder kann das raus?
"""

def test_connect():
    client = AnalyzerRemote(IP,PORT)
    client.connect()
    client.disconnect()
    
    
def test_context_manager():
    with AnalyzerRemote(IP) as client:
        pass


def test_context_manager():
    with AnalyzerRemote(IP) as client:
        pass
    
    
def test_get_socket_ip():
    with AnalyzerRemote(IP) as client:
        assert client.get_socket_ip == IP
        
        
def test_get_socket_port():
    with AnalyzerRemote(IP) as client:
        assert client.get_socket_port == PORT
        
        
def test_get_measuring_state():
    with AnalyzerRemote(IP) as client:
        assert client.get_measuring_state == False
        
        
def test_get_monitoring_state():
    with AnalyzerRemote(IP) as client:
        assert client.get_monitoring_state == False


def test_get_sine_gen_state():
    with AnalyzerRemote(IP) as client:
        assert client.get_sine_gen_state == False


def test_get_operator_functions_state():
    with AnalyzerRemote(IP) as client:
        assert client.get_operator_functions_state == False

# def test_start_measuring():
#     with AnalyzerRemote(IP) as client:
#         assert client.start_measuring()
        
def test_monitoring_mode():
    with AnalyzerRemote(IP) as client:
        client.set_monitoring_mode(True)
        time.sleep(0.3)
        assert client.get_monitoring_state
        client.set_monitoring_mode(False)
        
        
def test_sine_generator():
    with AnalyzerRemote(IP) as client:
        client.start_sineGenerator(frequency=400,amplitude=Amplitudes.AMP_446_mV)
        assert client.get_sine_gen_state
        client.stop_sineGenerator()


def test_get_set_appvar():
    bar = {}
    
    def set_bar(data):
        bar['data'] = data
        
    with AnalyzerRemote(IP) as client:
        client.set_appvar('foobar',42)
        assert int(client.get_appvar('foobar')) == 42
        
        client.remove_appvar('foobar')
        assert client.get_appvar('foobar') == None
        
        assert len(bar) == 0
        client.add_appvar_report_callback(set_bar)
        client.set_appvar('foobar',13)
        time.sleep(0.2)
        assert bar['data']['action'] == 'changed'
        
def test_get_process_number():
    with AnalyzerRemote(IP) as client:
        assert client.get_process_number() > 0
        
def test_get_analyzer_version():
    with AnalyzerRemote(IP) as client:
        assert client.get_analyzer_versions().startswith('Analyzer4D version: ')
        
def test_get_project_info():
    with AnalyzerRemote(IP) as client:
        assert 'projectid' in client.get_project_info()
        
def test_get_measure_positions():
    with AnalyzerRemote(IP) as client:
        assert 'mp0' in client.get_measure_positions() 
    
def test_get_preamp_info():
    with AnalyzerRemote(IP) as client:
        with pytest.raises(AnalyzerError):
            assert client.get_preamp_info(PreampPorts.PREAMP_PORT_1)
            
def test_operator():
    with AnalyzerRemote(IP) as client:       
        # client.start_operator('TemplateMatching','')
        
        with pytest.raises(AnalyzerError):
            client.start_operator('foobar','')
        
        # client.stop_operator_function()
     
        
def test_input_register():
    bar = {}
    def set_value(data):
        bar['data'] = data
        
    with AnalyzerRemote(IP) as client:  
        
        client.set_simulated_io_input('00000000 00000000')
        client.set_simulated_io_input_line("4.1",False)
        client.set_simulated_io_input_line("4.2",False)     
        client.set_simulated_io_input_line("4.3",False)     
        client.set_simulated_io_input_line("4.4",False)  
        time.sleep(0.1) 
        assert client.get_io_input() == 0
        client.set_simulated_io_input_line("1.3",True)
        time.sleep(0.1)    
        assert client.get_io_input() == 4
        
        client.add_io_report_callback(set_value)
        client.set_simulated_io_input_line("1.4",True)
        time.sleep(0.1)  
        assert bar['data']['ioin'] == (1<<2 | 1<<3)
        
def test_output_register():
    bar = {}
    def set_value(data):
        bar['data'] = data
        
    with AnalyzerRemote(IP) as client:
        for i in range(4,9):
            client.set_io_output(i,False)
            
        time.sleep(0.1)
        register = client.get_io_output()
        assert register == 1
        
        client.add_io_report_callback(set_value)
        
        client.set_io_output(4,True)
        time.sleep(0.1)
        assert bar['data']['ioout'] == (1<<3 | 1<<0)

def test_process_numbers():
    bar = {}
    def set_value(data):
        bar['data'] = data
        
    with AnalyzerRemote(IP) as client:
        for i in range(4,9):
            client.add_process_number_report_callback(set_value)
            
            number = client.get_process_number()
            
            # client.start_measuring()
            # time.sleep(0.5)
            # client.stop_measuring()
            
            if number > 0:
                client.load_process(number-1)
            time.sleep(0.5)
            # time.sleep(3)
            
            assert bar['data']['processnumber'] == number-1