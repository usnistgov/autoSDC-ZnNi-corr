import json
from ruamel import yaml
import numpy as np
import pandas as pd

# test 1.25 mL/min and 10 mL/min
# against 10 / 50 / 100 mV/s
n = 6
relative_rates = None

# 3 cm in -x, and 7 cm in -y
# grid spacing of 7 mm
x, y = 7 * np.mgrid[4:5,0:13]

# df = pd.DataFrame({'x': -x.flat[:n], 'y': -y.flat[:n], 'flow': relative_rates})
df = pd.DataFrame({'x': -x.flat[3:3+n], 'y': -y.flat[3:3+n], 'flow': relative_rates})

print(df)

with open('lsv_config_2.yaml') as f:
    config = yaml.safe_load(f)

print(config['solutions'])

header = {'intent': 'corrosion'}
expt = json.loads(config['default_experiment'])
flow = config['default_flowrate']

print(expt)
print(flow)

instructions = []

values = []
for flow_rate in [1.25, 10]:
    for scan_rate in [0.01, 0.05, 0.1]:
        values.append((flow_rate, scan_rate))

for count, (idx, row) in enumerate(df.iterrows()):
    header = {'intent': 'corrosion', 'x': row.x, 'y': row.y}
    f = flow.copy()
    e = expt.copy()

    flow_rate, scan_rate = values[count]
    f['flow_rate'] = flow_rate
    e[1]['scan_rate'] = scan_rate
    instructions.append([header, f, *e])


print(instructions)

# with open('instructions.json', 'r') as f:
#     prev_instructions = json.load(f)

# instructions = prev_instructions + instructions

with open("lsv-instructions.json", "r") as f:
    prev_instructions = json.load(f)

instructions = prev_instructions + instructions

with open("lsv-instructions-2.json", "w") as f:
    json.dump(instructions, f, indent=2)
