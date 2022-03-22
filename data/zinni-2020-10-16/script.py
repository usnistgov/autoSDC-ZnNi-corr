import json
from ruamel import yaml
import numpy as np
import pandas as pd

total_rate = 1
relative_rates = [1, 0.3, 0.1,  0.03, 0.01, 0.1, 0.003]
basic_rates = [{'KOH': x * total_rate, 'K2SO4': (1-x) * total_rate} for x in relative_rates]
# switch the acid ordering to go from neutral to acidic

relative_rates = [1, 0.3, 0.1,  0.03, 0.01, 0.003]
acidic_rates = [{'H2SO4': x * total_rate, 'K2SO4': (1-x) * total_rate} for x in relative_rates[::-1]]
relative_rates = basic_rates + [{'K2SO4': 1.0}] + acidic_rates


x, y = 10 * np.mgrid[0:5,0:5]
df = pd.DataFrame({'x': x.flat[3:14+3], 'y': -y.flat[3:14+3], 'flow': relative_rates})

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

with open("instructions-1.json", "w") as f:
    json.dump(instructions, f, indent=2)
