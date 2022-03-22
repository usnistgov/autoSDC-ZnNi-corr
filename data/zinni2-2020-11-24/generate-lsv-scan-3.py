import json
from ruamel import yaml
import numpy as np
import pandas as pd

# test 1.25 mL/min and 10 mL/min
# against 10 / 50 / 100 mV/s
n = 2
relative_rates = None

# 3 cm in -x, and 7 cm in -y
# grid spacing of 7 mm
x, y = 7 * np.mgrid[4:5,0:13]

# df = pd.DataFrame({'x': -x.flat[:n], 'y': -y.flat[:n], 'flow': relative_rates})
df = pd.DataFrame({'x': -x.flat[9:9+n], 'y': -y.flat[9:9+n], 'flow': relative_rates})

print(df)

with open('lsv_config_2.yaml') as f:
    config = yaml.safe_load(f)

print(config['solutions'])

header = {'intent': 'corrosion'}
# expt = json.loads(config['default_experiment'])
flow = config['default_flowrate']

experiments = [
    [{"op": "open_circuit", "duration": 1800, "stabilization_range": 0.002, "stabilization_window": 90, "minimum_duration": 300, "smoothing_window": 10},
     {"op": "cv", "initial_potential": -1.3, "vertex_potential_1": 0.5, "vertex_potential_2": -1.3, "final_potential": 0.5, "scan_rate": 0.075, "cycles": 2, "current_range": "2MA"}],
    [{"op": "open_circuit", "duration": 1800, "stabilization_range": 0.002, "stabilization_window": 90, "minimum_duration": 300, "smoothing_window": 10},
     {"op": "lpr", "initial_potential": -0.012, "final_potential": 0.012, "step_height": 0.0001, "step_time": 0.8, "current_range": "20UA"},
     {"op": "lpr", "initial_potential": -0.012, "final_potential": 0.012, "step_height": 0.0001, "step_time": 0.8, "current_range": "20UA"},
     {"op": "lpr", "initial_potential": -0.012, "final_potential": 0.012, "step_height": 0.0001, "step_time": 0.8, "current_range": "20UA"},
     {"op": "tafel", "initial_potential": -0.25, "final_potential": 0.25, "step_height": 0.005, "step_time": 1, "current_range": "200UA"},
     {"op": "cv", "initial_potential": -1.3, "vertex_potential_1": 0.5, "vertex_potential_2": -1.3, "final_potential": 0.5, "scan_rate": 0.075, "cycles": 2, "current_range": "2MA"}]
]

print(flow)

instructions = []

for count, (idx, row) in enumerate(df.iterrows()):
    header = {'intent': 'corrosion', 'x': row.x, 'y': row.y}
    expt = experiments[count]
    instructions.append([header, flow, *expt])


print(instructions)

# with open('instructions.json', 'r') as f:
#     prev_instructions = json.load(f)

# instructions = prev_instructions + instructions

with open("lsv-instructions-2.json", "r") as f:
    prev_instructions = json.load(f)

instructions = prev_instructions + instructions

with open("lsv-instructions-3.json", "w") as f:
    json.dump(instructions, f, indent=2)
