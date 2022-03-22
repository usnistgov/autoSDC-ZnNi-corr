import json
from ruamel import yaml
import numpy as np
import pandas as pd

n = 3
relative_rates = None

# 3 cm in -x, and 7 cm in -y
# grid spacing of 7 mm
x, y = 7 * np.mgrid[4:5,0:13]

df = pd.DataFrame({'x': -x.flat[:n], 'y': -y.flat[:n], 'flow': relative_rates})
print(df)

with open('lsv_config.yaml') as f:
    config = yaml.safe_load(f)

print(config['solutions'])

header = {'intent': 'corrosion'}
# expt = json.loads(config['default_experiment'])
expt = config['default_experiment']
# expt = [{"op": "lsv", "initial_potential": -1.1, "final_potential": 0.2, "scan_rate": 0.01, "current_range": "20MA"}]
flow = config['default_flowrate']

print(expt)
print(flow)

instructions = []
for idx, row in df.iterrows():
    header = {'intent': 'corrosion', 'x': row.x, 'y': row.y}
    instructions.append([header, flow, *expt])

print(instructions)

with open('instructions.json', 'r') as f:
    prev_instructions = json.load(f)

instructions = prev_instructions + instructions

with open("lsv-instructions.json", "w") as f:
    json.dump(instructions, f, indent=2)
