from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import optimize
from scipy import signal
from scipy import stats

R = 8.3145  # J/mol.K
F = 96485  # C/mol
T = 293  # K


def estimate_ocp(x, y, w=10):
    id_min = np.nanargmin(np.abs(y))
    sel = slice(id_min - w, id_min + w)
    slope, intercept, *rest = stats.linregress(x[sel], y[sel])

    def f(x):
        return abs(intercept + slope * x)

    res = optimize.minimize_scalar(f)

    return res.x


def estimate_overpotential(x, y, w=10):
    ocp = estimate_ocp(x, y, w=w)
    return x - ocp


def check_inflection(x, y):
    """try to fit low overpotential with negative curvature

    i.e. take the Savitsky-Golay 2nd derivative and select
    the part of the curve with negative curvature

    The method from 10.1021/acs.jpcc.9b06820 does not seem
    to work well for some of our data
    """
    order = np.argsort(np.abs(x))
    xx, yy = x.copy()[order], y.copy()[order]

    deriv = signal.savgol_filter(np.log10(np.abs(yy)), 3, 2, deriv=2)
    sgn = np.sign(deriv)
    (slc,) = np.where(sgn <= 0)
    id_inflection = np.argmax(slc)

    xx = xx[:id_inflection]

    # revert to increasing voltage
    order = np.argsort(xx)
    return xx[order], yy[order]


def tafel_fit(x, y, windows=np.arange(0.025, 0.1, 0.001), clip_inflection=False,tafel_binsize=0.025,lsv_threshold=.8):

    segments = {"cathodic": x < 0, "anodic": x > 0}

    tafel_data, fits = {}, {}
    for segment, slc in segments.items():

        xx, yy = x[slc], y[slc]

        if clip_inflection:
            xx, yy = check_inflection(xx, yy)

        results = fit_all(xx, yy, scan_type=segment, windows=windows)
        d = filter_r2(results,lsv_threshold=lsv_threshold)
        best_fit, subset = find_best_fit(d, tafel_binsize=tafel_binsize)

        tafel_data[segment] = best_fit
        fits[segment] = subset

    return tafel_data, fits


def fit_all(
    x: np.array,
    y: np.array,
    windows: np.array = np.arange(0.01, 0.05, 0.001),
    R2_thresh: float = 0.9,
    scan_type="cathodic",
) -> pd.DataFrame:
    """ fit tafel model on all sub-windows for each window size in `windows` """

    df = []
    for windowsize in windows:
        df.append(fit_windows(x, y, windowsize, n=1, scan_type=scan_type))

    df = pd.concat(df)

    df = df[(df["R2_tafel"] > R2_thresh) & (df["R2_lsv"] > R2_thresh)]

    return df


def fit_windows(
    potential: np.array,
    current: np.array,
    window: float,
    n: int = 1,
    scan_type: str = "cathodic",
) -> pd.DataFrame:
    """fit a tafel model on each sub-window of size `window`
    L137 in ba3cc165515cc335578db76cf6fff4672afacb29

    """

    # explicit loop is over LSV samples, not raw potential values
    window_samples = int(np.round(window / np.median(np.diff(potential))))
    log_current = np.log10(np.abs(current))

    # check for transport effects
    # numerically differentiate the LSV curve
    # find the max and truncate data...
    # note: do this outside the hot loop

    # fit on all intervals of size `window`
    results = []
    for idx in range(len(potential) - window_samples):

        if scan_type == "cathodic":
            # cathodic scans run "backwards" in time
            # start at open circuit and stride backwards towards more negative potential
            mask = slice(-(idx + 1) - window_samples, -(idx + 1))
        elif scan_type == "anodic":
            # anodic scans run forwards/intuitively
            # start at open circuit and stride forwards towards more positive potential
            mask = slice(idx, idx + window_samples)

        # fit Tafel data
        slope_tafel, intercept_tafel, r_tafel, *rest = stats.linregress(
            potential[mask], log_current[mask]
        )

        # fit LSV data
        slope_lsv, _, r_lsv, *rest = stats.linregress(potential[mask], current[mask])

        results.append(
            {
                "j0": 10 ** intercept_tafel,  # exchange current
                "dj/dV": abs(slope_lsv),  # LSV slope ~ j0 in the Tafel regime
                # "dlog(j)/dV": 1000 / slope_tafel,  # tafel slope (mV/decade)
                "dlog(j)/dV": slope_tafel,
                "intercept_tafel": intercept_tafel,
                "slope_tafel": slope_tafel,
                "window_start": potential[idx],
                "window_min": potential[mask].min(),
                "window_max": potential[mask].max(),
                "R2_tafel": r_tafel ** 2,
                "R2_lsv": r_lsv ** 2,
            }
        )

    r = pd.DataFrame(results)
    n_fits, _ = r.shape
    if n_fits == 0:
        return None

    # Tafel residue -- quantify the quality of the Tafel/linearity assumption
    r["residue"] = np.abs(r["dj/dV"] - r["j0"] * (F / n * R * T))

    # save the fitting window size for downstream analysis
    r["window"] = window

    return r


def filter_r2(
    df: pd.DataFrame, r2_threshold: np.array = np.arange(0.9, 1.0, 0.001),lsv_threshold=.8
) -> pd.DataFrame:
    """ record minimal-tafel-residue fits as a function of R^2 threshold """
    rows = []
    print(f'lav_threshold={lsv_threshold}')
    for threshold in r2_threshold:
        sel = (df["R2_tafel"] > threshold) & (df["R2_lsv"] > lsv_threshold)

        # record the fit with minimal tafel residue for each fitting window size
        for w, group in df[sel].groupby("window"):
            if group.size > 0:
                idx = group["residue"].values.argmin()
                rows.append(group.iloc[idx])

    return pd.DataFrame(rows)


def find_best_fit(
    df: pd.DataFrame, tafel_binsize: float = 1
) -> tuple[pd.Series, pd.DataFrame]:
    """select the most stable Tafel fit

    1. discretize the tafel fits by tafel slope
    2. select tafel slope bin with greatest range of fitting window size
    3. select from this tafel slope bin the fit with the best R^2 value
    """
    # bin the tafel slopes
    tslope = df["dlog(j)/dV"]
    nbins = int(np.abs(np.round(tslope.max() - tslope.min() / tafel_binsize)))

    def count_unique_values(x: np.array) -> int:
        return np.unique(x).size

    # nwindows: number of unique window sizes in each tafel slope bin
    # bins: tafel bin edges
    nwindows, bins, counts = stats.binned_statistic(
        tslope, df["window"], statistic=count_unique_values, bins=nbins
    )

    # select the tafel slope bin with the most unique window size values
    # then select all the fits in this tafel slope bin
    id_bin = nwindows.argmax()
    bin_min, bin_max = bins[id_bin], bins[id_bin + 1]
    subset = df[(tslope >= bin_min) & (tslope <= bin_max)]

    # try to filter outliers

    # drop = np.logical_or(
    #     subset["R2_lsv"] < subset["R2_lsv"].mean() - 2*subset["R2_lsv"].std(),
    #     subset["R2_tafel"] < subset["R2_tafel"].mean() - 2*subset["R2_tafel"].std()
    # )
    # subset = subset[~drop]

    # the "best" fit has the highest Tafel R^2 value in this tafel slope bin
    best_fit = subset.sort_values(by="R2_tafel").iloc[-1]
    # best_fit = subset.sort_values(by="R2_lsv").iloc[-1]
    # subset["r2sum"] = subset["R2_tafel"] + subset["R2_lsv"]
    # best_fit = subset.sort_values(by="r2sum").iloc[-1]

    # instead, sort by window size
    #best_fit = subset.sort_values(by="window").iloc[-1]

    return best_fit, subset
