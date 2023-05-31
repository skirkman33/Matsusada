import socket, time, re

class Matsusada:
    # parameters
    TCP_IP        = "134.105.64.201"
    TCP_PORT      = 10001
    BUFFER_SIZE   = 1024
    data_list     = []

    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.TCP_IP, self.TCP_PORT))
        print("Socket to Matsusada opened.")
        self.enable_remote()
        self.current_limit(10)
        self.restore_output()
        
    def enable_remote(self):
        myMsg = "#1 REN \r"
        self.s.send(myMsg.encode())
        print("Remote operation enabled.")
        
    def current_limit(self, current):
        myMsg = "#1 ICN {:.2f} \r"
        self.s.send(myMsg.format(current).encode())
        print(myMsg.format(current))

    def restore_output(self):
        myMsg = "#1 RST \r"
        self.s.send(myMsg.encode())
        
    def output_on(self):
        myMsg = "#1 SW1 \r"
        self.s.send(myMsg.encode())

        print("Output on")
        self.zero_output()
    
    def output_off(self):
        myMsg = "#1 SW0 \r"
        self.s.send(myMsg.encode())
        self.s.close()
        print("Output off.")

    def zero_output(self):
        self.send_voltage(0)
        v = self.read_voltage()
        while float(v) > 0.1: 
            time.sleep(2)
            v = self.read_voltage()
            print(v)
        print("Zeroed")
    
    def send_voltage(self, voltage):
        v = 5*voltage/6
        myMsg = "#1 VCN {:.2f} \r"
        print(myMsg.format(v))
        self.s.send(myMsg.format(v).encode())
 
    def sweep(self, voltage, current, ramp_rate):
        if voltage > 120:
            raise TypeError('Valid voltage range: 0 - 120 [kV]')

        if current > 100:
            raise TypeError('Valid current range: 0 - 100 %')

        ramp_time     = voltage/ramp_rate  # sec
        self.rate = ramp_rate

        v_s = 5*voltage/6
        swp_time = voltage/ramp_rate
        myMsg = "#1 VSWP {:.2f} \r"
        print(myMsg.format(v_s))
        self.s.send(myMsg.format(v_s).encode())
        
        myMsg1 = "#1 TSWP {:.2f} \r"
        print(myMsg1.format(ramp_time))
        self.s.send(myMsg1.format(ramp_time).encode())
        
        myMsg2 = '#1 ISWP {:.2f} \r'
        print(myMsg2.format(current))
        self.s.send(myMsg2.format(current).encode())
        
        myMsg3 = "#1 SWP ON \r"
        self.s.send(myMsg3.encode())
        start_time = time.time()
        print("Sweep on")

        while (time.time() - start_time) < (ramp_time + 1):     
            self.read_save(start_time)
        self.swp_off()
    
    def zero_swp(self):
        myMsg2 = "#1 SWPEV 0 \r"
        self.s.send(myMsg2.encode())
    
    def swp_off(self):
        myMsg1 = "#1 SWP OFF \r"
        self.s.send(myMsg1.encode())

    def output_status(self):
        buffer1 = ""
        myMsg1 = "#1 SW? \r"
        self.s.send(myMsg1.encode())
        while True:
            msg = self.s.recv(self.BUFFER_SIZE) 
            buffer1 += str(msg)
           # print('Buffer = ' + buffer1)
            if len(buffer1) > 8:
                break
            return buffer1

    def status_query(self):
        buffer1 = ""
        myMsg1 = "#1 STS \r"
        self.s.send(myMsg1.encode())
        while True:
            msg = self.s.recv(self.BUFFER_SIZE) 
            buffer1 += str(msg)
            print('Buffer = ' + buffer1)
            if len(buffer1) > 8:
                break

    def read_voltage(self):
        myMsg = "#1 VM \r"
        self.s.send(myMsg.encode()) 
        buffer = ""
        v1 = ""
        v2 = ""
        while True:
            data = self.s.recv(self.BUFFER_SIZE) 
            buffer += str(data)
            # print('Buffer = ' + buffer)
            if '=' not in str(buffer):
                continue
            if buffer[len(buffer)-2] == 'r':
                break
        y = buffer.split(".")
        y1 = re.findall(r'\d+', y[0])
        y2 = re.findall(r'\d+', y[1])
        for p in y1:
            v1 += p
        for p in y2:
            v2 += p
        v = v1 + '.' + v2
        print(v)
        return v

    def read_current(self):
        myMsg = "#1 IM \r"
        self.s.send(myMsg.encode()) 
        buffer = ""
        i1 = ""
        i2 = ""
        while True:
            data = self.s.recv(self.BUFFER_SIZE) 
            buffer += str(data)
            if '=' not in str(buffer):
                continue
            if buffer[len(buffer)-2] == 'r':
                break
        y = buffer.split(".")
        y1 = re.findall(r'\d+', y[0])
        y2 = re.findall(r'\d+', y[1])
        for p in y1:
            i1 += p
        for p in y2:
            i2 += p
        i = i1 + '.' + i2
        return i

    def read_save(self, start_time): 
        # save as floats? # check how long this takes 
        x = self.read_voltage()
        y = self.read_current()
        t = str(time.time() - start_time)
        self.data_list.append(t + ", " + x + ", " + y +"\n")

    def read_set_voltage(self):
        myMsg = "#1 VCN? \r"
        self.s.send(myMsg.encode()) 
        buffer = ""
        while True:
            data = self.s.recv(self.BUFFER_SIZE) 
            print(data)
            buffer += str(data)
            if '=' not in str(buffer):
                continue
            if (buffer[len(buffer)-2] == 'r') and (buffer[len(buffer)-3] == '\\'):
                break
        v = buffer.split("=")[1].split("\\")[0]
        return v