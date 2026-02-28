# 🔍 Crypto Spot Screener — OKX

A command-line tool to screen crypto spot pairs on **OKX** using various technical analysis strategies, powered by the [`ccxt`](https://github.com/ccxt/ccxt) library.

Results can be sent automatically to a **Discord channel** via Webhook notifications.

---

## 📁 Project Structure

```
crypto-spot-screener/
├── main.py                    # CLI entry point
├── cmd.py                     # Exchange, data fetching, and strategy dispatcher
├── notification.py            # Discord Webhook notification module
├── screener/
│   ├── __init__.py
│   ├── buyonbreakout.py       # Buy on Breakout strategy
│   └── rising3methods.py      # Rising Three Methods candlestick strategy
├── .env.example               # Environment variable template
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

**4. Configure Discord Webhook (optional)**

```bash
cp .env.example .env
# Then edit .env and fill in your DISCORD_WEBHOOK_URL
```

> How to get a Discord Webhook URL:
> 1. Open your Discord server
> 2. Go to **Channel Settings → Integrations → Webhooks**
> 3. Click **New Webhook**, copy the URL, and paste it into `.env`

---

## 🚀 Usage

```bash
python main.py --strategy <strategy> --tf <timeframe> [options]
```

### Arguments

| Argument      | Required | Description                                           | Default                      |
|---------------|----------|-------------------------------------------------------|------------------------------|
| `--strategy`  | ✅ Yes   | Screening strategy to use (see below)                 | —                            |
| `--tf`        | ✅ Yes   | Candle timeframe (see below)                          | —                            |
| `--limit`     | No       | Number of candles to fetch per symbol                 | `100`                        |
| `--quote`     | No       | Quote currency filter                                 | `USDT`                       |
| `--top`       | No       | Only screen top N symbols by volume                   | All                          |
| `--webhook`   | No       | Discord Webhook URL for notifications                 | `DISCORD_WEBHOOK_URL` env    |

### Available Strategies

| Strategy         | Description                                              |
|------------------|----------------------------------------------------------|
| `buyonbreakout`  | Detects symbols breaking above their 20-day high         |
| `rising3methods` | Detects the Rising Three Methods candlestick pattern     |

### Available Timeframes

`1m` `3m` `5m` `15m` `30m` `1H` `2H` `4H` `6H` `12H` `1D` `3D` `1W` `1M`

---

## 📖 Examples

```bash
# Buy on Breakout on 4-hour candles
python main.py --strategy buyonbreakout --tf 4H

# Buy on Breakout on daily candles
python main.py --strategy buyonbreakout --tf 1D

# Rising Three Methods on daily candles
python main.py --strategy rising3methods --tf 1D

# Screen only top 50 USDT pairs
python main.py --strategy buyonbreakout --tf 1D --top 50

# Use BTC as the quote currency
python main.py --strategy rising3methods --tf 4H --quote BTC
```

---

## 🔔 Discord Notifications

The screener can send results directly to a Discord channel after each run.

### Setup

**Option 1 — Environment variable (recommended):**

```bash
# In your .env file or shell profile:
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN"

python main.py --strategy rising3methods --tf 1D
```

**Option 2 — CLI argument (one-off):**

```bash
python main.py --strategy rising3methods --tf 1D \
  --webhook "https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN"
```

**Option 3 — Disable notifications:**

```bash
python main.py --strategy rising3methods --tf 1D --webhook ""
```

### What gets sent

Each scan sends **two Discord embeds**:

| Embed          | Contents                                                  |
|----------------|-----------------------------------------------------------|
| **Header**     | Strategy name, scan time (UTC), timeframe, match count    |
| **Results**    | Per-symbol: ticker, signal, close price, volume           |

> ⚠️ **Do Your Own Research!** — always included in the embed footer.

---

## 📦 Dependencies

| Package | Version  | Purpose                        |
|---------|----------|--------------------------------|
| `ccxt`  | ≥ 4.0.0  | Exchange connectivity & data   |

> Discord notifications use Python's built-in `urllib` — no extra packages needed.

---

## 📝 License

MIT
