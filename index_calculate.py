import pandas as pd

# 1. Bollinger Bands
def calculate_bollinger_bands(close, window=20):
    sma = close.rolling(window).mean()
    std = close.rolling(window).std()
    upper = sma + 2 * std
    lower = sma - 2 * std
    return sma, upper, lower

# 2. MACD
def calculate_macd(close):
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

# 3. RSI
def calculate_rsi(close, period=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 4. Stochastic Oscillator
def calculate_stochastic_oscillator(high, low, close, k_period=14, d_period=3):
    lowest = low.rolling(window=k_period).min()
    highest = high.rolling(window=k_period).max()
    k = 100 * (close - lowest) / (highest - lowest)
    d = k.rolling(window=d_period).mean()
    return k, d

# === 각 지표의 매수/매도/보유 신호 ===
def bollinger_signal(close, lower, middle, upper):
    if close <= lower:
        return "Buy"
    elif close >= upper and close < middle:
        return "Sell"
    else:
        return "Hold"

def macd_signal(macd_today, macd_yesterday, signal_today, signal_yesterday):
    if macd_today < 0 and macd_yesterday < signal_yesterday and macd_today > signal_today:
        return "Buy"
    elif macd_today > 0 and macd_yesterday > signal_yesterday and macd_today < signal_today:
        return "Sell"
    else:
        return "Hold"

def rsi_signal(rsi_today, rsi_yesterday):
    if rsi_yesterday < 30 and rsi_today >= 30:
        return "Buy"
    elif rsi_yesterday > 70 and rsi_today <= 70:
        return "Sell"
    else:
        return "Hold"

def stochastic_signal(k_today, k_yesterday, d_today, d_yesterday):
    if k_today <= 20 and k_yesterday < d_yesterday and k_today > d_today:
        return "Buy"
    elif k_today >= 80 and k_yesterday > d_yesterday and k_today < d_today:
        return "Sell"
    else:
        return "Hold"

# 신호 → 수치 매핑
def signal_to_value(signal):
    return {"Buy": 1.0, "Hold": 0.5, "Sell": 0.0}[signal]

# === 최종 Buy Index 계산 ===
def calculate_buy_index(df: pd.DataFrame) -> float:
    close = df['Close']
    high = df['High']
    low = df['Low']

    # 기술 지표 계산
    sma, upper, lower = calculate_bollinger_bands(close)
    macd, signal = calculate_macd(close)
    rsi = calculate_rsi(close)
    k, d = calculate_stochastic_oscillator(high, low, close)

    # 최신 데이터 기준 신호 추출
    boll_signal = bollinger_signal(close.iloc[-1], lower.iloc[-1], sma.iloc[-1], upper.iloc[-1])
    macd_sig = macd_signal(macd.iloc[-1], macd.iloc[-2], signal.iloc[-1], signal.iloc[-2])
    rsi_sig = rsi_signal(rsi.iloc[-1], rsi.iloc[-2])
    sto_sig = stochastic_signal(k.iloc[-1], k.iloc[-2], d.iloc[-1], d.iloc[-2])

    # 가중치 기반 통합 점수 계산
    weights = {
        "bollinger": 0.2,
        "macd": 0.3,
        "rsi": 0.2,
        "stochastic": 0.4
    }

    score = (
        signal_to_value(boll_signal) * weights["bollinger"] +
        signal_to_value(macd_sig) * weights["macd"] +
        signal_to_value(rsi_sig) * weights["rsi"] +
        signal_to_value(sto_sig) * weights["stochastic"]
    )

    return round(score, 3)  # 소수점 셋째 자리까지 반영

# 사용 예시
import FinanceDataReader as fdr

df = fdr.DataReader("AAPL", "2023-11-01")
buy_index = calculate_buy_index(df)
print("Buy Index:", buy_index)