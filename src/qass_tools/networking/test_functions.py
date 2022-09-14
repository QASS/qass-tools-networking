from analyzer_socket import AnalyzerCmd
import json

with AnalyzerCmd("192.168.1.50") as opti:
    j = json.dumps({"a": 1})
    opti.set_appvar("testytest", j)
    result = opti.get_app_var("testytest")
    print(result)
