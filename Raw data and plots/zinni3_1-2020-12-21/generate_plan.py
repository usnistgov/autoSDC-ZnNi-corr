import json
from ruamel import yaml
import numpy as np
import pandas as pd

total_rate = 1

relative_rates = [1, 0.1, 1e-2, 1e-3]
acidic_rates = [{'H2SO4': x * total_rate, 'K2SO4': (1-x) * total_rate} for x in relative_rates]
basic_rates = [{'KOH': x * total_rate, 'K2SO4': (1-x) * total_rate} for x in relative_rates[::-1]]

rates = basic_rates + [{'K2SO4': total_rate}] + acidic_rates

n = len(rates)

# 3 cm in -x, and 7 cm in -y
# grid spacing of 1 cm
x, y = 10 * np.mgrid[0:4,0:12]
df = pd.DataFrame({'x': -x.flatten(), 'y': -y.flatten()})

print(n)
print(df.shape)

# sort targets to march in +y, then +x
df = df.sort_values(by=['x', 'y'], ascending=[False, False])
df = df.iloc[:n]
df['flow'] = rates

# df = pd.DataFrame({'x': x.flat[:n], 'y': -y.flat[:n], 'flow': relative_rates})

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
