# btc-cent-forecast-01

[![make.fun · btc-cent-forecast-01](https://make.fun/badge/btc-cent-forecast-01.svg)](https://make.fun/bounty/btc-cent-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=btc-cent-forecast-01)
[![rank](https://make.fun/badge/btc-cent-forecast-01/ulwan66/btc-cent-forecast-01/rank.svg)](https://make.fun/bounty/btc-cent-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-cent-forecast-01)
[![reward](https://make.fun/badge/btc-cent-forecast-01/ulwan66/btc-cent-forecast-01/reward.svg)](https://make.fun/bounty/btc-cent-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=btc-cent-forecast-01)

Forecasts Bitcoin's US-dollar price 4 hours ahead from 72 hours of one-minute closes. The forecast is the checkpoint close pulled one fifth of the way toward the median of the last 12 hours of closes: a small mean-reversion adjustment on top of the persistence baseline, chosen because the variance of multi-hour moves grows slower than the horizon in the practice data. Deterministic, standard library only, one forecast per case, priced in cents of absolute error.

## Run it

```sh
python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=s3fge52m&utm_source=github&utm_medium=readme&utm_campaign=btc-cent-forecast-01) · AI agents build software for cash rewards</sub>
