import sys
sys.dont_write_bytecode = True

import qcodes.parameters
import requests
import json
import qcodes
 
import datetime


def _map_ranges(val, in_min, in_max, out_min, out_max):
	out_val = out_min + ((val - in_min) / (in_max - in_min)) * (out_max - out_min)
	return out_val

sample_calibration_data = {"platform_set_temps": [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250], "avg_recorded_sample_temps": [6.3630638376610476, 7.1976460261612, 8.082703762378795, 9.002880743267097, 9.940208292928014, 10.881409839882307, 11.83440395674989, 12.81263931273207, 13.77848973873806, 14.748377080251604, 15.71516946816863, 16.694209591390518, 17.667133572943918, 18.649760780339925, 19.626774842236678, 20.606107868874126, 21.59758346986142, 22.590618523127034, 23.575151838362142, 24.565704265263115, 25.547037225198984, 26.528505734193537, 27.52130024052547, 28.510341092588902, 29.49051773769101, 30.475609240373597, 31.481641012013903, 32.48111695734706, 33.46159620170801, 34.44531229765871, 35.455469944009266, 36.453529056872576, 37.43700926909237, 38.442461750227636, 39.43031852153464, 40.41264881017012, 41.425057219848775, 42.40685128136198, 43.410103425185056, 44.4015327067231, 45.39130089976629, 46.398161005520365, 47.37985437870351, 48.39066723991884, 49.3689476182812, 50.37980339388512, 51.361397314702955, 52.37690732885799, 53.36963390696644, 54.376550584452104, 55.37923659040651, 56.36953022663084, 57.377393400076905, 58.35252906536365, 59.37389729352358, 60.34245476500625, 61.34638526364173, 62.34960468941841, 63.36199398035171, 64.36273254431774, 65.32893956289433, 66.33919723697045, 67.35242210896097, 68.36098421558145, 69.36595407059819, 70.36885759826885, 71.32499853400786, 72.33638058465547, 73.34320512351565, 74.34666516323087, 75.34995611621456, 76.34815903901986, 77.30393268987413, 78.31389920403379, 79.32034658355802, 80.22310718813819, 81.13673855722948, 82.13157471593516, 83.11156305305356, 84.11959232147692, 85.12338360601868, 86.12340834152363, 87.12101818176174, 88.11688853842602, 89.11144355344322, 90.08747586364922, 91.09221826167615, 92.09331472143613, 93.0919352695172, 94.08845323490866, 95.08266929620657, 96.07577512259498, 97.06941116793874, 98.05277526879766, 99.05230274153661, 100.04933065470598, 101.044517774566, 102.03751510514057, 103.02914023194657, 104.0197889524502, 105.00958434854147, 105.99629828367999, 106.99526069041974, 107.99152316255024, 108.98738936800787, 109.98181258503186, 110.97462542787041, 111.96721112751695, 112.95851963976338, 113.94951837652407, 114.94563021863819, 115.94514468448571, 116.9426380084351, 117.93895093278984, 118.93624545162871, 119.9295550999635, 120.92232647222716, 121.91403145272201, 122.90500597128104, 123.8953902357576, 124.90171467272121, 125.90036811253815, 126.89663500320043, 127.89258969640885, 128.88640084844693, 129.8787815115017, 130.87037487569026, 131.86165291481646, 132.85027395411174, 133.8401425822249, 134.8484212772371, 135.84596244225645, 136.84170993331927, 137.8361506039939, 138.82973757320994, 139.82220027651843, 140.81425653697795, 141.80510489376334, 142.7973645310855, 143.78768752658297, 144.7774581039595, 145.79141364085666, 146.7914411902133, 147.79020214961062, 148.78771548853874, 149.783256864503, 150.7784100293293, 151.77199035315397, 152.76525163162881, 153.7575445179691, 154.74973947205265, 155.74053838172875, 156.7313378546288, 157.71987676788044, 158.74945421004207, 159.74629147096954, 160.74221986852774, 161.73637023446312, 162.7300899651614, 163.72297106243778, 164.71443465782758, 165.70493958076068, 166.69580193032476, 167.68477822205432, 168.6745809510012, 169.66493075891532, 170.65301534134414, 171.6855002832089, 172.68267497606786, 173.67838342542873, 174.673149998761, 175.6670906549744, 176.66046976712235, 177.65220040726874, 178.64479516705893, 179.63679722086113, 180.6278254225736, 181.61812806647262, 182.60777355715285, 183.5981360281277, 184.58827354301323, 185.6200002085684, 186.62814442951384, 187.62640157676623, 188.62369951568735, 189.61900540444503, 190.6141072376667, 191.60840541012345, 192.60264051364754, 193.59517311887072, 194.58725977817565, 195.57946607746322, 196.57194418130206, 197.56368004946427, 198.55416963497245, 199.54520478708488, 200.53475422149083, 201.5871509978595, 202.58386683462004, 203.5799211894604, 204.5752230935963, 205.56922650396785, 206.56238534539472, 207.555263558307, 208.54686773717586, 209.5385085604884, 210.52711455198067, 211.51798449324787, 212.50850540192695, 213.49791997653838, 214.48751676851603, 215.47731733821965, 216.4672693857486, 217.44168139205968, 218.4989794240082, 219.49174721987046, 220.4860219678083, 221.4795585312242, 222.4610705903534, 223.4371850690107, 224.41918575871628, 225.40333002617453, 226.3891454891469, 227.36547800641196, 228.3296434565103, 229.3064991039405, 230.28636083010323, 231.25796886578618, 232.2366196184083, 233.2168174270634, 234.18714928938712, 235.15329830706955, 236.22632863847934, 237.20457045314757, 238.17632288456292, 239.12706909707208, 240.09213288053152, 241.04523475495162, 242.00484201945483, 242.96843085304187, 243.93111863381932, 244.89353473271998, 245.85408134973514, 246.81704919493524, 247.780299839715, 248.74429779788125]}

class CryoCore(qcodes.Instrument):

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        #self.ip = ip
        #self.port = port
        self.sample_temperature : qcodes.Parameter
        self.platform_temperature : qcodes.Parameter #Gets platform temp, Sets platform temp
        qcodes.Parameter("platform_temperature", self, "Platform Temperature", "K", get_cmd=self.get_platform_temp, set_cmd=self.set_platform_temp)
        qcodes.Parameter("sample_temperature", self, "Sample Temperature", "K", get_cmd=self.get_sample_temp, set_cmd=self.set_sample_temp)
        #self.add_parameter("temperature", self.temp_param, {})
    
    def ask(self, question_string : str):
        print("The CryoCore is an http communicating instrument!")
        return f"{self.ip}, {self.port}"

    def get_platform_temp(self):
        resp = requests.get('http://192.168.10.105:47101/v1/sampleChamber/temperatureControllers/platform/thermometer/properties/sample')
        return float(resp.json()["sample"].get("temperature"))
    
    def get_sample_temp(self, options={}):
        """Perform the Get Value instrument operation"""
        resp = requests.get('http://192.168.10.105:47101/v1/sampleChamber/temperatureControllers/user1/thermometer/properties/sample')
        #sample thermometer is controlled through user1
        sampleDict = json.loads(resp.content.decode('utf-8'))['sample']
        actualTemp = sampleDict['temperature']
        value = actualTemp
        return value 
    
    def set_platform_temp(self, value, sweepRate=0.0, options={}):                         
        """Perform the Set Value instrument operation"""

            
        cutoff = 290 #Defines the cutoff temperature to control warmup and cooldown processes.
        #TODO: MAYBE NEW CUTOFF AT 265K ...

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
    
    def set_sample_temp(self, value):
        min = 5 #min sample temperature limited by calibration data
        max = 250 #max sample temperature limited by calibration data
        if value < min or value > max:
            print(f"Temp is outside of {(min, max)} K sample calibration range.")
        

        for i in range(len(sample_calibration_data["platform_set_temps"])): #iterate through all calibration data to see what two indices that the desired temp is between (or on)

            try:
                sample_calibration_data["avg_recorded_sample_temps"][i+1]
            except:
                print("Cannot set sample temp that high!")
                return 
            
            if value >= sample_calibration_data["avg_recorded_sample_temps"][i] and value <= sample_calibration_data["avg_recorded_sample_temps"][i+1]:
                print(sample_calibration_data["avg_recorded_sample_temps"][i])
                print(sample_calibration_data["avg_recorded_sample_temps"][i+1])
                target_platform = _map_ranges(value, sample_calibration_data["avg_recorded_sample_temps"][i], sample_calibration_data["avg_recorded_sample_temps"][i+1], sample_calibration_data["platform_set_temps"][i], sample_calibration_data["platform_set_temps"][i+1])
                self.platform_temperature.set(target_platform)
                print(f"Platform chose {target_platform} K")
                return
 
if __name__ == '__main__':
    my_cryo_core = CryoCore("my_cryo_core")
    print(my_cryo_core.parameters)

    my_cryo_core.sample_temperature.set(150)
    