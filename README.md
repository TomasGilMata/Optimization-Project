# Portfolio Optimizer (Mean–Variance / Markowitz)
Application that will calculate the optimal allocations of a given portfolio according to the Mean Variance portfolio optimization method by Markowitz.
The app downloads prices with **yfinance**, computes the **mean–variance frontier**, the **minimum-variance** and **tangent** portfolios, and renders a clean interactive plot (hover to read off σ and μ). You can target either a desired return **μ** or a desired volatility **σ**. Optionally compare to a benchmark (e.g. `^GSPC`) and show the individual tickers in the graph.

## Preview
<img width="2847" height="875" alt="preview1" src="https://github.com/user-attachments/assets/9ecbe3b6-4384-4ddb-9ca3-085214b02feb" />
<img width="2810" height="1327" alt="preview2" src="https://github.com/user-attachments/assets/62dfcb89-ddbc-4597-aba8-2dfa1b7daea8" />



## Features

- Download prices from Yahoo Finance via `yfinance`
- Annualized **expected returns**  and **volatility** (annualized from daily returns)
- Optimization based on formulas derived from the Lagrangian function to minimize the standard deviation of a portfolio with the conditions that the weights of assets add up to one and that the expected return is equal to a certain defined value.
- **Minimum variance**, **tangent**, and **optimal** portfolios (with and without risk-free asset)
- Clean plot with hover display and optional labeled tickers
- Optional **benchmark Sharpe ratio** chip


## Structure

    portfolio-optimizer/
    ├─ app.py
    ├─ requirements.txt
    ├─ README.md
    ├─ portfolio/
    │  ├─ __init__.py
    │  ├─ data.py         # yfinance + returns/volatility/covariance/benchmark
    │  ├─ optim.py        # Markowitz math & portfolios
    │  └─ plotting.py     # matplotlib plotting
    └─ templates/
       └─ index.html      # UI (Jinja2)

> The folder must be named **templates/** (plural) and sit **next to** `app.py`.

## How to Run

    # 1) Virtual environment
    python -m venv .venv
    # Windows (PowerShell): .venv\Scripts\Activate.ps1
    # macOS/Linux:          source .venv/bin/activate

    # 2) Dependencies
    pip install -r requirements.txt

    # 3) Start server
    python app.py

Open: **http://127.0.0.1:5000**

## Inputs (UI)

- **Tickers** (comma separated, e.g., `AAPL, MSFT, KO`)
- **Target return μ (%)** *or* **Target volatility σ (%)** (leave the other blank)
- **Risk-free rate (%)**
- **Benchmark** (optional, e.g., `^GSPC`)
- **Views**: Minimum Variance · Tangent · Optimal (no RF) · Optimal (+ RF)
- **Show tickers**: toggles individual asset points and labels

## Methodology (implemented)

**Expected returns (μ) — monthly → annual**
- Uses **adjusted monthly closes** (`interval="1mo"`).
- Window: `start="2009-12-01"`, `end="2025-01-04"`.
- Aligns to the **first available Dec 1** row (avoids partial years/IPO issues).
- For each year *t*:  
  `μ_t = Close(Dec t) / Close(Dec t-1) − 1`  
  `μ = mean({μ_t})`.

**Volatility (σ) — daily → annual**
- Uses **adjusted daily returns** (`interval="1d"`).
- Window: `start="2009-12-31"`, `end="2025-01-01"`.
- Aligns to the **first available Dec 31** row.
- `r_i = (P[i] − P[i−1]) / P[i−1]`  
  `σ_annual = stdev(r, ddof=1) * sqrt(252)`.

**Covariance (Σ)**
- From the same daily returns; series clipped to a **common length**.
- Annualized by **×252**.

**Frontier & portfolios (Markowitz)**
- `A = 1ᵀ Σ⁻¹ 1`, `B = 1ᵀ Σ⁻¹ μ`, `C = μᵀ Σ⁻¹ μ`, `Δ = AC − B²`.
- **MVP**, **tangent** (with risk-free), and **optimal** (with/without risk-free) computed in **closed form**.
- **Sharpe**: `(μ_p − r_f) / σ_p`.

## Tips & Troubleshooting

- **TemplateNotFound**: ensure `templates/index.html` is next to `app.py`. If needed, set an absolute `template_folder`.
- **yfinance** (limits/retries/missing data): reduce the number of tickers or remove problematic ones.
- **Unattainable targets** (e.g., σ below MVP): the app raises a descriptive error.
- **Windows/Anaconda/CWD**: run `python app.py` from the **project root**.

## Requirements

    Flask>=3.0.0
    yfinance>=0.2.40
    numpy>=1.26
    pandas>=2.2
    matplotlib>=3.8

## Disclaimer

Historical estimates only. **Not investment advice.**

## License

MIT

