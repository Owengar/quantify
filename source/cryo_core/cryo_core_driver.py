import sys
sys.dont_write_bytecode = True

import requests
import json
import sys
import qcodes
 
import datetime


class CryoCore(qcodes.Instrument):

    def __init__(self, name, ip, port, **kwargs):
        super().__init__(name, **kwargs)
        self.ip = ip
        self.port = port
        self.temp_param = qcodes.Parameter("temperature", self, "Temperature", "K", get_cmd=self.get_get_temp(), set_cmd=self.get_set_temp())

        #self.add_parameter("temperature", self.temp_param, {})
    
    def ask(self, question_string : str):
        print("The CryoCore is an http communicating instrument!")
        return f"{self.ip}, {self.port}"


    def get_get_temp(instrument):
        def get_temp():
            return instrument.performGetValue('Get Temp')
        return get_temp
    
    def get_set_temp(instrument):
        def set_temp(value):
            instrument.performSetValue('Set Temp', value)
        return set_temp
    
    def performGetValue(self, quant, options={}):
        """Perform the Get Value instrument operation"""
        if quant.name == 'Get Temp':
            resp = requests.get('http://192.168.10.105:47101/v1/sampleChamber/temperatureControllers/user1/thermometer/properties/sample')
            #sample thermometer is controlled through user1
            sampleDict = json.loads(resp.content.decode('utf-8'))['sample']
            actualTemp = sampleDict['temperature']
            value = actualTemp
        return value 
    
    def performSetValue(self, quant, value, sweepRate=0.0, options={}):                         
        """Perform the Set Value instrument operation"""
        if quant.name == 'Set Temp':
            
            cutoff = 290.0 #Defines the cutoff temperature to control warmup and cooldown processes.

            resp   = requests.get('http://192.168.10.105:47101/v1/controller/properties/systemGoal')
            state = json.loads(resp.content.decode('utf-8'))['systemGoal'] #This gives the current state of the cryostat
            target = float(value) #This gives the target value that the user has provided through labber
            
            if state == 'Cooldown':
                if target > cutoff:
                    resp = requests.post('http://192.168.10.105:47101/v1/controller/methods/abortGoal()')
                    resp = requests.post('http://192.168.10.105:47101/v1/controller/methods/warmup()')
                    resp = requests.put("http://192.168.10.105:47101/v1/controller/properties/platformTargetTemperature", json={"platformTargetTemperature": target})
                else:
                    resp = requests.put("http://192.168.10.105:47101/v1/controller/properties/platformTargetTemperature", json={"platformTargetTemperature": target})
                    #resp   = requests.get('http://192.168.10.102:47101/v1/controller/properties/platformTargetTemperature')
                    #newSetpoint = json.loads(resp.content.decode('utf-8'))['platformTargetTemperature']
            else:
                if target < cutoff:
                    resp = requests.post('http://192.168.10.105:47101/v1/controller/methods/abortGoal()')
                    resp = requests.put("http://192.168.10.105:47101/v1/controller/properties/platformTargetTemperature", json={"platformTargetTemperature": target})
                    #resp   = requests.get('http://192.168.10.105:47101/v1/controller/properties/platformTargetTemperature')
                    #newSetpoint = json.loads(resp.content.decode('utf-8'))['platformTargetTemperature']
                    resp = requests.post('http://192.168.10.105:47101/v1/controller/methods/cooldown()')
                else:
                    resp = requests.put("http://192.168.10.105:47101/v1/controller/properties/platformTargetTemperature", json={"platformTargetTemperature": target})
                    #If the target temp is over the cutoff and the system is not cooling down, no further action is needed
        return value
 
if __name__ == '__main__':
    my_cryo_core = CryoCore("my_cryo_core", "192.168.10.105", "47101")
    print(my_cryo_core.parameters)
    