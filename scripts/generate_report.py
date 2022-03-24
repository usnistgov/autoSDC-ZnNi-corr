"""Process and analyze all raw electrochemical data into results table."""
import os
import pandas as pd
from pathlib import Path

from asdc.analysis.report import load_session

# session keys and sample ids to exclude from analysis
# (for insufficient data quality)
drop_ids = {
    "zinni-2020-10-16": [15, 18],
    "zinni-2020-10-26": [1],
    "zinni2-2020-11-24": [28, 34, 38],
    %"zinni3_1-2020-12-21": [],
}


if __name__ == "__main__":
    data_dir = Path("data")
    data_dir.mkdirs(exists_ok=True)

    dataframes = []
    for idx, (run, drop) in enumerate(drop_ids.items()):
        df = load_session(str(data_dir / run / "data/sdc.db"))
        df = df[~df.id.isin(drop)]
        df["session"] = run
        df["experiment"] = f"dat{idx+1}"
        dataframes.append(df)

    df = pd.concat(dataframes)

    df.sort_values(by="E_oc_stable", inplace=True)
    df.dropna(inplace=True, subset=["pH_med"])
    df.reset_index(inplace=True)
    df.to_json(data_dir / "fulldataset.json")
