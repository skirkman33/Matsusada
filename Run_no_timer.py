import os
from Matsusada import Matsusada

# weird syntax error - type exit() in command bar

# sweep parameters
ramp_rate     = 1                       # kV/s
voltage       = 60                      # kV (absolute): 1-120 kV
current_lim   = 10                      # % of 5 mA
fname         = 'FR3_spacer_1600_mu_old_oil_13.txt'     

# create file 
if os.path.isfile(fname):
     raise TypeError('File already exists!')
else:
     f = open(fname, 'w')
                            
# don't edit below
m = Matsusada()
m.output_on()

# start sweep
m.sweep(voltage, current_lim, ramp_rate)                         

data = m.data_list
f.writelines(data)
print('Data saved!')
f.close()
print('Zeroing output')
m.zero_output() 

m.output_off()
m.s = ""