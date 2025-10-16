import numpy as np
import pandas as pd
import yfinance as yf


def _first_index_on(df_index: pd.DatetimeIndex, month: int, day: int):
    mask = (df_index.month == month) & (df_index.day == day)
    idx = df_index[mask]
    if len(idx) == 0:
        raise ValueError("No index found matching the requested month/day in the downloaded data.")
    return idx[0]


def get_returns(tickers):  # μ
    expected_returns = []

    for t in tickers:
        data = yf.download(t, start="2009-12-01", end="2025-01-04", interval="1mo", auto_adjust=True, progress=False)["Close"]
        years = int((len(data) - 1) / 12)

        data.index = pd.to_datetime(data.index)
        first_idx = _first_index_on(data.index, 12, 1)
        data = data.loc[first_idx:].reset_index(drop=True)

        anual_returns = []
        for i in range(years):
            anual_return = round(((data.iloc[(i + 1) * 12].item() - data.iloc[i * 12].item()) / data.iloc[i * 12].item()), 4)
            anual_returns.append(anual_return)
        mean_return = round(np.mean(anual_returns).item(), 2)
        expected_returns.append(mean_return)

    return expected_returns


def get_volatilities(tickers):  # σ
    volatilities = []
    for t in tickers:
        data = yf.download(t, start="2009-12-31", end="2025-01-01", interval="1d", auto_adjust=True, progress=False)["Close"]
        trading_days = 252
        data.index = pd.to_datetime(data.index)
        first_idx = _first_index_on(data.index, 12, 31)
        data = data.loc[first_idx:].reset_index(drop=True)

        daily_returns = []
        for i in range(1, len(data)):
            d_return = round(((data.iloc[i].item() - data.iloc[i - 1].item()) / data.iloc[i - 1].item()), 4)
            daily_returns.append(d_return)

        sigma = round((np.std(daily_returns, ddof=1)) * np.sqrt(trading_days), 2).item()
        volatilities.append(sigma)

    return volatilities


def covariance_matrix(tickers):
    all_returns = []
    for t in tickers:
        data = yf.download(t, start="2009-12-31", end="2025-01-01", interval="1d", auto_adjust=True, progress=False)["Close"]
        data.index = pd.to_datetime(data.index)
        first_idx = _first_index_on(data.index, 12, 31)
        data = data.loc[first_idx:].reset_index(drop=True)

        daily_returns = []
        for i in range(1, len(data)):
            d_return = round(((data.iloc[i].item() - data.iloc[i - 1].item()) / data.iloc[i - 1].item()), 4)
            daily_returns.append(d_return)
        all_returns.append(daily_returns)

    # align lengths
    min_len = min(len(i) for i in all_returns)
    all_returns = [lst[-min_len:] for lst in all_returns]

    matrix_of_returns = np.column_stack([np.asarray(x) for x in all_returns])  # columns are stocks
    cov = np.cov(matrix_of_returns, rowvar=False, ddof=1) * 252  # annualize
    return cov


def compute_benchmark(symbol, rf):
    data = yf.download(symbol, start="2009-12-01", end="2025-01-04", interval="1mo", auto_adjust=True, progress=False)["Close"]
    years = int((len(data) - 1) / 12)

    data.index = pd.to_datetime(data.index)
    first_idx = _first_index_on(data.index, 12, 1)
    data = data.loc[first_idx:].reset_index(drop=True)

    anual_returns = []
    for i in range(years):
        anual_return = round(((data.iloc[(i + 1) * 12].item() - data.iloc[i * 12].item()) / data.iloc[i * 12].item()), 4)
        anual_returns.append(anual_return)
    mean_return = round(np.mean(anual_returns).item(), 2)

    data = yf.download(symbol, start="2009-12-31", end="2025-01-01", interval="1d", auto_adjust=True, progress=False)["Close"]
    trading_days = 252
    data.index = pd.to_datetime(data.index)
    first_idx = _first_index_on(data.index, 12, 31)
    data = data.loc[first_idx:].reset_index(drop=True)

    daily_returns = []
    for i in range(1, len(data)):
        d_return = round(((data.iloc[i].item() - data.iloc[i - 1].item()) / data.iloc[i - 1].item()), 4)
        daily_returns.append(d_return)
    sigma = round((np.std(daily_returns, ddof=1)) * np.sqrt(trading_days), 2).item()  # annualized sd
    shapre = round((mean_return - rf) / sigma, 2)

    return (mean_return, sigma, shapre)
