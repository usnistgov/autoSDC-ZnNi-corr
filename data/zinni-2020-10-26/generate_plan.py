import json
from ruamel import yaml
import numpy as np
import pandas as pd

total_rate = 1
# relative_rates = [1, 0.3, 0.1,  0.03, 0.01, 0.1, 0.003]
relative_rates = [1, 0.5, 1, 0.5, 0.25, 0.1,  0.05, 0.025, 0.01, 0.005, 0.0025, 0.0010]
basic_rates = [{'KOH': x * total_rate, 'K2SO4': (1-x) * total_rate} for x in relative_rates]
# switch the acid ordering to go from neutral to acidic

relative_rates = [1, 0.3, 0.1,  0.03, 0.01, 0.003]
acidic_rates = [{'H2SO4': x * total_rate, 'K2SO4': (1-x) * total_rate} for x in relative_rates[::-1]]

relative_rates = basic_rates + [{'K2SO4': 1.0}]

n = len(relative_rates)

# 3 cm in -x, and 7 cm in -y
x, y = 7 * np.mgrid[0:5,0:10]
df = pd.DataFrame({'x': x.flat[:n], 'y': -y.flat[:n], 'flow': relative_rates})

with open('config.yaml') as f:
    config = yaml.safe_load(f)

header = {'intent': 'corrosion'}
expt = json.loads(config['default_experiment'])
flow = config['default_flowrate']

instructions = []
for idx, row in df.iterrows():
    header = {'intent': 'corrosion', 'x': row.x, 'y': row.y}
    f = flow.copy()
    f['relative_rates'] = row['flow']
    instructions.append([header, f, *expt])

with open("instructions.json", "w") as f:
    json.dump(instructions, f, indent=2)
