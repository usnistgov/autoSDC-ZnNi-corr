import json
from ruamel import yaml
import numpy as np
import pandas as pd

total_rate = 1
relative_rates = [1, 0.3, 0.1,  0.03, 0.01, 3e-3, 1e-3, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5]
basic_rates = [{'KOH': x * total_rate, 'K2SO4': (1-x) * total_rate} for x in relative_rates]

# swap ordering of acidic flow rates...
relative_rates = [1, 0.3, 0.1,  0.03, 0.01, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5]
acidic_rates = [{'H2SO4': x * total_rate, 'K2SO4': (1-x) * total_rate} for x in relative_rates[::-1]]

relative_rates = basic_rates + acidic_rates

n_orig = len(relative_rates)

rrates = [1, 0.3, 0.1,  0.03, 0.01, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5]
acidic_rates = [{'H2SO4': x * total_rate, 'K2SO4': (1-x) * total_rate} for x in rrates]
basic_rates = [{'KOH': x * total_rate, 'K2SO4': (1-x) * total_rate} for x in rrates[::-1]]

relative_rates = relative_rates + acidic_rates + basic_rates

n = len(relative_rates)

# 3 cm in -x, and 7 cm in -y
# grid spacing of 7 mm
x, y = 7 * np.mgrid[0:4,0:13]
df = pd.DataFrame({'x': -x.flatten(), 'y': -y.flatten()})

# remove one spot from each row, at the -y extreme
sel = (df.index < 24) | (df.y > df.y.min())
df = df[sel]

print(n)
print(df.shape)

# sort targets to march in +y, then +x
df = df.sort_values(by=['x', 'y'], ascending=[False, False])
df = df.iloc[:n]
df['flow'] = relative_rates

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
