# 🔍 Crypto Spot Screener — OKX

A command-line tool to screen crypto spot pairs on **OKX** using various technical analysis strategies, powered by the [`ccxt`](https://github.com/ccxt/ccxt) library.

---

## 📁 Project Structure

```
crypto-spot-screener/
├── main.py                    # CLI entry point
├── cmd.py                     # Exchange, data fetching, and strategy 
├── screener/
│   ├── __init__.py
│   ├── breakout20days.py      # 20-day breakout strategy
│   └── rising3methods.py      # Rising Three Methods candlestick strategy
├── requirements.txt
└── .gitignore
```

---

## ⚙️ Installation

**1. Clone the repository**

```bash
git clone https://github.com/your-username/crypto-spot-screener.git
cd crypto-spot-screener
```

**2. Create and activate a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
.venv\Scripts\activate      # Windows
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

---

## 🚀 Usage

```bash
python main.py --strategy <strategy> --tf <timeframe> [options]
```

### Arguments

| Argument     | Required | Description                                      | Default |
|--------------|----------|--------------------------------------------------|---------|
| `--strategy` | ✅ Yes   | Screening strategy to use (see below)            | —       |
| `--tf`       | ✅ Yes   | Candle timeframe (see below)                     | —       |
| `--limit`    | No       | Number of candles to fetch per symbol            | `100`   |
| `--quote`    | No       | Quote currency filter                            | `USDT`  |
| `--top`      | No       | Only screen top N symbols by volume              | All     |

### Available Strategies

| Strategy         | Description                                      |
|------------------|--------------------------------------------------|
| `breakout_20day` | Detects symbols breaking above their 20-day high |
| `rising3methods` | Detects the Rising Three Methods candlestick pattern |

### Available Timeframes

`1m` `3m` `5m` `15m` `30m` `1H` `2H` `4H` `6H` `12H` `1D` `3D` `1W` `1M`

---

## 📖 Examples

```bash
# Breakout 20-day on 4-hour candles
python main.py --strategy breakout_20day --tf 4H

# Breakout 20-day on daily candles
python main.py --strategy breakout_20day --tf 1D

# Rising Three Methods on daily candles
python main.py --strategy rising3methods --tf 1D

# Screen only top 50 USDT pairs by volume
python main.py --strategy breakout_20day --tf 1D --top 50

# Use BTC as the quote currency
python main.py --strategy rising3methods --tf 4H --quote BTC
```

---

## 📦 Dependencies

| Package | Version  | Purpose                         |
|---------|----------|---------------------------------|
| `ccxt`  | ≥ 4.0.0  | Exchange connectivity & data    |

---

## 📝 License

MIT
