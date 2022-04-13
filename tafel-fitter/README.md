# tafel-fitter

A Tafel analysis library based on [10.1021/acs.jpcc.9b06820](https://dx.doi.org/10.1021/acs.jpcc.9b06820). This repository is a fork of the reference implementation https://github.com/MEG-LBNL/Tafel_Fitter.

Example:

```python
df = pd.read_csv("Input_files/test1.csv")

x = df["overpotential"].values
y = df["current"].values
u = tafel.estimate_overpotential(x, y)
tafel_data, fits = tafel.tafel_fit(u, y, windows=np.arange(0.025, 0.25, 0.001))


plt.plot(u, np.log10(np.abs(y)), marker="o")
lims = plt.gca().get_ylim()

colors = ["g", "m"]
for idx, (segment, best_fit) in enumerate(tafel_data.items()):

    plt.plot(u, np.log10(best_fit["j0"]) + best_fit["dlog(j)/dV"]*u, color=colors[idx])
    plt.axhline(np.log10(best_fit["j0"]), label=f"j0 {segment}", color=colors[idx])
    plt.axvline(best_fit["window_min"], color='k', alpha=0.2, linestyle="--")
    plt.axvline(best_fit["window_max"], color='k', alpha=0.2, linestyle="--")

plt.ylim(*lims)
plt.xlabel("overpotential (V)")
plt.ylabel("log current")
plt.legend(loc="lower right")

plt.axvline(0, color="k", alpha=0.5)
plt.show()
```