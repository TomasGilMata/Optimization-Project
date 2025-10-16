import matplotlib.pyplot as plt
from .data import get_volatilities, get_returns


def graph(tickers, wanted_return, wanted_volatility, rf, view="mvp", benchmark=None, show_tickers=True, benchmark_label=None):
    # lazy import to avoid circular
    from .optim import portfolios

    everything = portfolios(tickers, wanted_return, wanted_volatility, rf)

    fig = plt.figure(figsize=(9, 5.4), dpi=120)
    plt.gcf().patch.set_alpha(0)           # figure background
    ax = plt.gca()
    ax.set_facecolor('none')               # axes background

    plt.rcParams['text.color'] = '#e5e7eb'
    plt.rcParams['axes.labelcolor'] = '#e5e7eb'
    plt.rcParams['xtick.color'] = '#e5e7eb'
    plt.rcParams['ytick.color'] = '#e5e7eb'

    for side in ['top', 'right', 'bottom', 'left']:
        ax.spines[side].set_color('#cbd5e1')

    plt.tick_params(colors='#e5e7eb', which='both')
    plt.grid(True, color='#94a3b8', alpha=0.35, linewidth=0.8)
    ax.set_axisbelow(True)

    v = (view or "mvp").lower()

    # Benchmark point
    if isinstance(benchmark, (tuple, list)) and len(benchmark) == 2:
        x, y = benchmark[1], benchmark[0]
        label = "Benchmark"
        if benchmark_label:
            label = f"{label} ({benchmark_label})"
        plt.scatter([x], [y], alpha=0.9)
        plt.annotate(label, (x, y), (4, 0), textcoords='offset points')

    # Frontier views
    if v == "mvp":
        plt.plot(everything[6], everything[5])
        plt.scatter([everything[2]], [everything[1]])
        plt.annotate("Minimum Variance Portfolio", (everything[2], everything[1]), (4, 0), textcoords='offset points')
    elif v == "tangent":
        plt.plot(everything[6], everything[5])
        plt.scatter([everything[9]], [everything[8]])
        plt.annotate("Tangent Portfolio", (everything[9], everything[8]), (4, 0), textcoords='offset points')
    elif v == "opt_norf":
        plt.plot(everything[6], everything[5])
        plt.scatter([everything[9]], [everything[8]])
        plt.annotate("Tangent Portfolio", (everything[9], everything[8]), (4, 0), textcoords='offset points')
        plt.scatter([everything[4]], [everything[14]])
        plt.annotate("Optimal Portfolio", (everything[4], everything[14]), (-90, 0), textcoords='offset points')
    elif v == "opt_rf":
        plt.plot(everything[6], everything[5], linestyle="--")
        plt.plot(everything[13], everything[5])
        plt.scatter([everything[9]], [everything[8]])
        plt.annotate("Tangent Portfolio", (everything[9], everything[8]), (4, 0), textcoords='offset points')
        plt.scatter([everything[12]], [everything[15]])
        plt.annotate("Optimal Portfolio + Riskless Asset", (everything[12], everything[15]), (-170, 0), textcoords='offset points')

    if show_tickers:
        vols = get_volatilities(tickers)
        rets = get_returns(tickers)
        for i, t in enumerate(tickers):
            plt.scatter([vols[i]], [rets[i]], alpha=0.6)
            plt.annotate(t, (vols[i], rets[i]), (4, 0), textcoords='offset points', alpha=0.6)

    plt.xlabel('Volatility σ', color='#e5e7eb')
    plt.ylabel('Return μ', color='#e5e7eb')

    ax.relim(); ax.autoscale_view()
    _, ymax = plt.ylim()
    plt.ylim(0, ymax * 1.05)  # a bit of headroom

    plt.tight_layout(pad=1.1)
    return fig
