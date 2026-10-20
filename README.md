# 🎰 Vietlott Data

[![GitHub Actions](https://github.com/mr2along/vietlott-data/workflows/crawl/badge.svg)](https://github.com/mr2along/vietlott-data/actions)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Data Updated](https://img.shields.io/badge/data-daily%20updated-brightgreen.svg)](https://github.com/mr2along/vietlott-data/commits/main)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Deployed-blue)](https://vietvudanh.github.io/vietlott-data/)

> 📊 **Automated Vietnamese Lottery Data Collection & Analysis**
>
> This project automatically crawls and analyzes Vietnamese lottery data from [vietlott.vn](https://vietlott.vn/), providing comprehensive statistics and insights for all major lottery products.

## 🔗 Links

- 🌐 [Website](https://vietvudanh.github.io/vietlott-data/) - Interactive data visualization
- 📝 [Blog Post](https://open.substack.com/pub/vietvudanh/p/minh-a-tao-repo-vietlott-data-the) - About this project

## 🎯 Supported Lottery Products

| Product | Link | Description |
|---------|------|-------------|
| **Power 6/55** | [🔗 Results](https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/655) | Choose 6 numbers from 1-55 |
| **Power 6/45** | [🔗 Results](https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/645) | Choose 6 numbers from 1-45 |
| **Power 5/35** | [🔗 Results](https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/535) | Choose 5 numbers from 1-35 |
| **Keno** | [🔗 Results](https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/winning-number-keno) | Fast-pace number game |
| **Max 3D** | [🔗 Results](https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/max-3d) | 3-digit lottery game |
| **Max 3D Pro** | [🔗 Results](https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/max-3dpro) | Enhanced 3D lottery |
| **Bingo18** | [🔗 Results](https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/winning-number-bingo18) | 3 numbers from 0-9 game |


## 📋 Table of Contents

- [🔗 Links](#-links)
- [🎯 Supported Lottery Products](#-supported-lottery-products)
- [Predictions](#-predictions)
- [📊 Data Statistics](#-data-statistics)
- [📈 Power 6/55 Analysis](#-power-655-analysis)
  - [📅 Recent Results](#-recent-results)
  - [🎲 Number Frequency (All Time)](#-number-frequency-all-time)
  - [📊 Frequency Analysis by Period](#-frequency-analysis-by-period)
  - [⏳ Top 10 Numbers by Days Since Last Appearance](#-top-10-số-lâu-chưa-xuất-hiện-top-10-numbers-by-days-since-last-appearance)
  - [📆 Days Since Last Appearance - All Numbers](#-số-ngày-từ-lần-xuất-hiện-cuối-cùng-days-since-last-appearance---all-numbers)
- [⚙️ How It Works](#️-how-it-works)
- [🚀 Installation & Usage](#-installation--usage)
- [📄 License](#-license)


## Predictions

Forecasts are published for research and retrospective evaluation only. Lottery draws are random; model outputs do not guarantee future results.

### Next-draw forecast — draw **#01413**

- **Target date:** 2026-10-20 (Tuesday)
- **Data cutoff:** draw #01412 dated 2026-10-17
- **Generated (UTC):** 2026-10-19T19:25:29.374896+00:00

These are research forecasts, not guaranteed outcomes. The special number is excluded from model features.

#### Single-line model predictions

| Model | Predicted numbers |
|---|---|
| Bayesian | 01, 07, 08, 11, 16, 22 |
| ExponentialDecay | 01, 07, 11, 16, 18, 27 |
| LogisticProbability | 07, 11, 13, 16, 21, 22 |
| RankEnsemble | 01, 07, 11, 13, 16, 22 |

<details>
<summary>PortfolioEnsemble — 30 ticket combinations</summary>

| # | Predicted combination |
|---:|---|
| 1 | 01, 07, 11, 16, 18, 22 |
| 2 | 01, 07, 11, 13, 16, 25 |
| 3 | 05, 07, 08, 14, 21, 27 |
| 4 | 08, 11, 23, 24, 41, 53 |
| 5 | 05, 09, 16, 24, 32, 39 |
| 6 | 08, 09, 13, 18, 29, 38 |
| 7 | 02, 18, 23, 29, 39, 45 |
| 8 | 07, 09, 20, 31, 41, 55 |
| 9 | 11, 27, 30, 38, 39, 55 |
| 10 | 08, 16, 20, 26, 33, 45 |
| 11 | 07, 22, 24, 25, 26, 38 |
| 12 | 02, 05, 11, 18, 31, 33 |
| 13 | 16, 22, 27, 29, 31, 53 |
| 14 | 01, 05, 14, 20, 23, 38 |
| 15 | 07, 13, 23, 30, 32, 33 |
| 16 | 09, 11, 14, 21, 22, 45 |
| 17 | 02, 14, 16, 25, 30, 41 |
| 18 | 18, 21, 23, 25, 27, 32 |
| 19 | 07, 14, 18, 24, 53, 55 |
| 20 | 01, 08, 21, 25, 31, 39 |
| 21 | 05, 11, 20, 25, 29, 32 |
| 22 | 05, 13, 16, 21, 38, 41 |
| 23 | 02, 07, 08, 26, 27, 32 |
| 24 | 01, 13, 24, 27, 41, 45 |
| 25 | 11, 13, 14, 23, 26, 39 |
| 26 | 02, 05, 08, 13, 22, 55 |
| 27 | 16, 21, 23, 29, 33, 55 |
| 28 | 05, 07, 23, 30, 31, 45 |
| 29 | 07, 09, 29, 33, 39, 41 |
| 30 | 02, 07, 20, 21, 38, 53 |

</details>


<details>
<summary>UnseenPortfolioEnsemble — 30 ticket combinations</summary>

| # | Predicted combination |
|---:|---|
| 1 | 01, 07, 11, 16, 18, 22 |
| 2 | 01, 07, 11, 13, 16, 25 |
| 3 | 05, 07, 08, 14, 21, 27 |
| 4 | 08, 11, 23, 24, 41, 53 |
| 5 | 05, 09, 16, 24, 32, 39 |
| 6 | 08, 09, 13, 18, 29, 38 |
| 7 | 02, 18, 23, 29, 39, 45 |
| 8 | 07, 09, 20, 31, 41, 55 |
| 9 | 11, 27, 30, 38, 39, 55 |
| 10 | 08, 16, 20, 26, 33, 45 |
| 11 | 07, 22, 24, 25, 26, 38 |
| 12 | 02, 05, 11, 18, 31, 33 |
| 13 | 16, 22, 27, 29, 31, 53 |
| 14 | 01, 05, 14, 20, 23, 38 |
| 15 | 07, 13, 23, 30, 32, 33 |
| 16 | 09, 11, 14, 21, 22, 45 |
| 17 | 02, 14, 16, 25, 30, 41 |
| 18 | 18, 21, 23, 25, 27, 32 |
| 19 | 07, 14, 18, 24, 53, 55 |
| 20 | 01, 08, 21, 25, 31, 39 |
| 21 | 05, 11, 20, 25, 29, 32 |
| 22 | 05, 13, 16, 21, 38, 41 |
| 23 | 02, 07, 08, 26, 27, 32 |
| 24 | 01, 13, 24, 27, 41, 45 |
| 25 | 11, 13, 14, 23, 26, 39 |
| 26 | 02, 05, 08, 13, 22, 55 |
| 27 | 16, 21, 23, 29, 33, 55 |
| 28 | 05, 07, 23, 30, 31, 45 |
| 29 | 07, 09, 29, 33, 39, 41 |
| 30 | 02, 07, 20, 21, 38, 53 |

</details>

### Realized forecast results

Completed forecasts: **8**; pending forecasts: **1**. A small historical sample does not establish predictive advantage.

| Strategy | Draws | Tickets | Tickets with ≥3 matches | ≥3-match rate | Payout (VND) | Net (VND) | ROI |
|---|---:|---:|---:|---:|---:|---:|---:|
| PortfolioEnsemble | 8 | 240 | 5 | 2.08% | 250,000 | -2,150,000 | -89.58% |
| UnseenPortfolioEnsemble | 8 | 240 | 5 | 2.08% | 250,000 | -2,150,000 | -89.58% |

Ticket cost is assumed to be 10,000 VND. Payouts use the configured prize values in the evaluator.

#### Rolling results — latest 10 evaluated draws

| Draw | Date | Actual main numbers | Special | Portfolio tickets ≥3 | Payout (VND) | Net (VND) |
|---:|---|---|---:|---:|---:|---:|
| 01412 | 2026-10-17 | 01, 10, 11, 12, 16, 37 | 48 | 0 | 0 | -300,000 |
| 01411 | 2026-10-15 | 07, 23, 25, 42, 45, 51 | 4 | 1 | 50,000 | -250,000 |
| 01410 | 2026-10-13 | 02, 14, 27, 40, 50, 53 | 26 | 0 | 0 | -300,000 |
| 01409 | 2026-10-10 | 14, 17, 21, 23, 24, 39 | 30 | 1 | 50,000 | -250,000 |
| 01408 | 2026-10-08 | 01, 07, 12, 27, 31, 52 | 6 | 0 | 0 | -300,000 |
| 01407 | 2026-10-06 | 06, 07, 18, 20, 24, 27 | 1 | 1 | 50,000 | -250,000 |
| 01406 | 2026-10-03 | 07, 11, 13, 16, 18, 54 | 41 | 2 | 100,000 | -200,000 |
| 01405 | 2026-10-01 | 04, 05, 13, 34, 52, 55 | 15 | 0 | 0 | -300,000 |

#### Forecast sequence and outcome for each evaluated draw

<details>
<summary>Draw #01412 — 2026-10-17 | actual: 01, 10, 11, 12, 16, 37 | ≥3-match tickets: 0 | payout: 0 VND</summary>

- Forecast generated (UTC): 2026-10-15T16:08:01.524033+00:00
- Actual main numbers: **01, 10, 11, 12, 16, 37**
- Actual special number: **48**

**Single-line model predictions and outcomes**

| Model | Forecast numbers | Main matches | Matched numbers | Payout (VND) | Prize |
|---|---|---:|---|---:|---|
| Bayesian | 07, 08, 11, 13, 16, 22 | 2/6 | 11, 16 | 0 | none |
| ExponentialDecay | 05, 07, 11, 18, 25, 27 | 1/6 | 11 | 0 | none |
| LogisticProbability | 07, 11, 13, 16, 22, 25 | 2/6 | 11, 16 | 0 | none |
| RankEnsemble | 05, 07, 11, 13, 16, 22 | 2/6 | 11, 16 | 0 | none |

**PortfolioEnsemble — 30 tickets**

| # | Predicted combination | Main matches | Matched main numbers | Special hit | Payout (VND) | Prize |
|---:|---|---:|---|---|---:|---|
| 1 | 07, 11, 13, 16, 18, 22 | 2/6 | 11, 16 | No | 0 | none |
| 2 | 05, 07, 11, 18, 25, 27 | 1/6 | 11 | No | 0 | none |
| 3 | 01, 08, 14, 21, 22, 24 | 1/6 | 01 | No | 0 | none |
| 4 | 08, 16, 23, 25, 41, 53 | 1/6 | 16 | No | 0 | none |
| 5 | 08, 09, 11, 32, 39, 45 | 1/6 | 11 | No | 0 | none |
| 6 | 02, 08, 22, 27, 29, 38 | 0/6 | — | No | 0 | none |
| 7 | 07, 09, 23, 26, 29, 55 | 0/6 | — | No | 0 | none |
| 8 | 07, 31, 33, 38, 39, 53 | 0/6 | — | No | 0 | none |
| 9 | 11, 14, 29, 30, 31, 41 | 1/6 | 11 | No | 0 | none |
| 10 | 05, 14, 16, 38, 45, 55 | 1/6 | 16 | No | 0 | none |
| 11 | 01, 02, 09, 13, 25, 33 | 1/6 | 01 | No | 0 | none |
| 12 | 02, 05, 07, 20, 32, 41 | 0/6 | — | No | 0 | none |
| 13 | 08, 18, 20, 26, 30, 33 | 0/6 | — | No | 0 | none |
| 14 | 01, 11, 20, 23, 24, 38 | 2/6 | 01, 11 | No | 0 | none |
| 15 | 01, 16, 21, 26, 27, 39 | 2/6 | 01, 16 | No | 0 | none |
| 16 | 13, 14, 20, 22, 25, 39 | 0/6 | — | No | 0 | none |
| 17 | 07, 22, 24, 30, 45, 53 | 0/6 | — | No | 0 | none |
| 18 | 14, 18, 23, 27, 32, 53 | 0/6 | — | No | 0 | none |
| 19 | 02, 11, 13, 21, 53, 55 | 1/6 | 11 | No | 0 | none |
| 20 | 05, 09, 16, 18, 24, 31 | 1/6 | 16 | No | 0 | none |
| 21 | 01, 08, 13, 16, 29, 32 | 2/6 | 01, 16 | No | 0 | none |
| 22 | 05, 11, 21, 22, 26, 33 | 1/6 | 11 | No | 0 | none |
| 23 | 07, 08, 21, 25, 31, 45 | 0/6 | — | No | 0 | none |
| 24 | 01, 18, 22, 41, 45, 55 | 1/6 | 01 | No | 0 | none |
| 25 | 11, 16, 25, 30, 32, 38 | 2/6 | 11, 16 | No | 0 | none |
| 26 | 05, 08, 13, 23, 27, 31 | 0/6 | — | No | 0 | none |
| 27 | 07, 08, 09, 14, 38, 41 | 0/6 | — | No | 0 | none |
| 28 | 02, 07, 23, 30, 39, 55 | 0/6 | — | No | 0 | none |
| 29 | 07, 16, 20, 24, 26, 27 | 1/6 | 16 | No | 0 | none |
| 30 | 01, 14, 18, 25, 29, 33 | 1/6 | 01 | No | 0 | none |

**UnseenPortfolioEnsemble — 30 tickets**

| # | Predicted combination | Main matches | Matched main numbers | Special hit | Payout (VND) | Prize |
|---:|---|---:|---|---|---:|---|
| 1 | 07, 11, 13, 16, 18, 22 | 2/6 | 11, 16 | No | 0 | none |
| 2 | 05, 07, 11, 18, 25, 27 | 1/6 | 11 | No | 0 | none |
| 3 | 01, 08, 14, 21, 22, 24 | 1/6 | 01 | No | 0 | none |
| 4 | 08, 16, 23, 25, 41, 53 | 1/6 | 16 | No | 0 | none |
| 5 | 08, 09, 11, 32, 39, 45 | 1/6 | 11 | No | 0 | none |
| 6 | 02, 08, 22, 27, 29, 38 | 0/6 | — | No | 0 | none |
| 7 | 07, 09, 23, 26, 29, 55 | 0/6 | — | No | 0 | none |
| 8 | 07, 31, 33, 38, 39, 53 | 0/6 | — | No | 0 | none |
| 9 | 11, 14, 29, 30, 31, 41 | 1/6 | 11 | No | 0 | none |
| 10 | 05, 14, 16, 38, 45, 55 | 1/6 | 16 | No | 0 | none |
| 11 | 01, 02, 09, 13, 25, 33 | 1/6 | 01 | No | 0 | none |
| 12 | 02, 05, 07, 20, 32, 41 | 0/6 | — | No | 0 | none |
| 13 | 08, 18, 20, 26, 30, 33 | 0/6 | — | No | 0 | none |
| 14 | 01, 11, 20, 23, 24, 38 | 2/6 | 01, 11 | No | 0 | none |
| 15 | 01, 16, 21, 26, 27, 39 | 2/6 | 01, 16 | No | 0 | none |
| 16 | 13, 14, 20, 22, 25, 39 | 0/6 | — | No | 0 | none |
| 17 | 07, 22, 24, 30, 45, 53 | 0/6 | — | No | 0 | none |
| 18 | 14, 18, 23, 27, 32, 53 | 0/6 | — | No | 0 | none |
| 19 | 02, 11, 13, 21, 53, 55 | 1/6 | 11 | No | 0 | none |
| 20 | 05, 09, 16, 18, 24, 31 | 1/6 | 16 | No | 0 | none |
| 21 | 01, 08, 13, 16, 29, 32 | 2/6 | 01, 16 | No | 0 | none |
| 22 | 05, 11, 21, 22, 26, 33 | 1/6 | 11 | No | 0 | none |
| 23 | 07, 08, 21, 25, 31, 45 | 0/6 | — | No | 0 | none |
| 24 | 01, 18, 22, 41, 45, 55 | 1/6 | 01 | No | 0 | none |
| 25 | 11, 16, 25, 30, 32, 38 | 2/6 | 11, 16 | No | 0 | none |
| 26 | 05, 08, 13, 23, 27, 31 | 0/6 | — | No | 0 | none |
| 27 | 07, 08, 09, 14, 38, 41 | 0/6 | — | No | 0 | none |
| 28 | 02, 07, 23, 30, 39, 55 | 0/6 | — | No | 0 | none |
| 29 | 07, 16, 20, 24, 26, 27 | 1/6 | 16 | No | 0 | none |
| 30 | 01, 14, 18, 25, 29, 33 | 1/6 | 01 | No | 0 | none |

</details>

<details>
<summary>Draw #01411 — 2026-10-15 | actual: 07, 23, 25, 42, 45, 51 | ≥3-match tickets: 1 | payout: 50,000 VND</summary>

- Forecast generated (UTC): 2026-10-14T18:07:46.490768+00:00
- Actual main numbers: **07, 23, 25, 42, 45, 51**
- Actual special number: **04**

**Single-line model predictions and outcomes**

| Model | Forecast numbers | Main matches | Matched numbers | Payout (VND) | Prize |
|---|---|---:|---|---:|---|
| Bayesian | 07, 08, 11, 13, 16, 22 | 1/6 | 07 | 0 | none |
| ExponentialDecay | 05, 07, 11, 13, 18, 27 | 1/6 | 07 | 0 | none |
| LogisticProbability | 13, 21, 22, 25, 27, 32 | 1/6 | 25 | 0 | none |
| RankEnsemble | 05, 07, 11, 13, 16, 22 | 1/6 | 07 | 0 | none |

**PortfolioEnsemble — 30 tickets**

| # | Predicted combination | Main matches | Matched main numbers | Special hit | Payout (VND) | Prize |
|---:|---|---:|---|---|---:|---|
| 1 | 07, 11, 13, 16, 22, 27 | 1/6 | 07 | No | 0 | none |
| 2 | 05, 07, 11, 13, 18, 27 | 1/6 | 07 | No | 0 | none |
| 3 | 01, 05, 08, 14, 16, 25 | 1/6 | 25 | No | 0 | none |
| 4 | 07, 08, 09, 21, 24, 32 | 1/6 | 07 | No | 0 | none |
| 5 | 08, 18, 22, 39, 41, 53 | 0/6 | — | No | 0 | none |
| 6 | 02, 11, 14, 24, 38, 39 | 0/6 | — | No | 0 | none |
| 7 | 07, 14, 26, 29, 41, 55 | 1/6 | 07 | No | 0 | none |
| 8 | 01, 07, 23, 31, 38, 53 | 2/6 | 07, 23 | No | 0 | none |
| 9 | 16, 18, 24, 30, 31, 55 | 0/6 | — | No | 0 | none |
| 10 | 08, 27, 29, 30, 38, 40 | 0/6 | — | No | 0 | none |
| 11 | 05, 22, 23, 24, 29, 33 | 1/6 | 23 | No | 0 | none |
| 12 | 02, 08, 13, 23, 45, 55 | 2/6 | 23, 45 | No | 0 | none |
| 13 | 08, 11, 25, 26, 31, 33 | 1/6 | 25 | No | 0 | none |
| 14 | 07, 21, 25, 30, 39, 45 | 3/6 | 07, 25, 45 | No | 50,000 | third |
| 15 | 13, 16, 32, 33, 38, 41 | 0/6 | — | No | 0 | none |
| 16 | 09, 14, 27, 33, 45, 53 | 1/6 | 45 | No | 0 | none |
| 17 | 13, 14, 21, 22, 31, 40 | 0/6 | — | No | 0 | none |
| 18 | 01, 09, 11, 22, 32, 55 | 0/6 | — | No | 0 | none |
| 19 | 02, 05, 07, 09, 16, 40 | 1/6 | 07 | No | 0 | none |
| 20 | 01, 02, 24, 25, 27, 41 | 1/6 | 25 | No | 0 | none |
| 21 | 11, 16, 18, 21, 29, 53 | 0/6 | — | No | 0 | none |
| 22 | 07, 18, 22, 25, 26, 38 | 2/6 | 07, 25 | No | 0 | none |
| 23 | 16, 23, 26, 27, 32, 39 | 1/6 | 23 | No | 0 | none |
| 24 | 01, 09, 13, 18, 29, 39 | 0/6 | — | No | 0 | none |
| 25 | 05, 09, 11, 23, 30, 41 | 1/6 | 23 | No | 0 | none |
| 26 | 07, 08, 14, 30, 32, 53 | 1/6 | 07 | No | 0 | none |
| 27 | 05, 21, 27, 38, 39, 55 | 0/6 | — | No | 0 | none |
| 28 | 01, 02, 21, 22, 26, 30 | 0/6 | — | No | 0 | none |
| 29 | 01, 07, 24, 33, 39, 40 | 1/6 | 07 | No | 0 | none |
| 30 | 02, 07, 29, 31, 41, 45 | 2/6 | 07, 45 | No | 0 | none |

**UnseenPortfolioEnsemble — 30 tickets**

| # | Predicted combination | Main matches | Matched main numbers | Special hit | Payout (VND) | Prize |
|---:|---|---:|---|---|---:|---|
| 1 | 07, 11, 13, 16, 22, 27 | 1/6 | 07 | No | 0 | none |
| 2 | 05, 07, 11, 13, 18, 27 | 1/6 | 07 | No | 0 | none |
| 3 | 01, 05, 08, 14, 16, 25 | 1/6 | 25 | No | 0 | none |
| 4 | 07, 08, 09, 21, 24, 32 | 1/6 | 07 | No | 0 | none |
| 5 | 08, 18, 22, 39, 41, 53 | 0/6 | — | No | 0 | none |
| 6 | 02, 11, 14, 24, 38, 39 | 0/6 | — | No | 0 | none |
| 7 | 07, 14, 26, 29, 41, 55 | 1/6 | 07 | No | 0 | none |
| 8 | 01, 07, 23, 31, 38, 53 | 2/6 | 07, 23 | No | 0 | none |
| 9 | 16, 18, 24, 30, 31, 55 | 0/6 | — | No | 0 | none |
| 10 | 08, 27, 29, 30, 38, 40 | 0/6 | — | No | 0 | none |
| 11 | 05, 22, 23, 24, 29, 33 | 1/6 | 23 | No | 0 | none |
| 12 | 02, 08, 13, 23, 45, 55 | 2/6 | 23, 45 | No | 0 | none |
| 13 | 08, 11, 25, 26, 31, 33 | 1/6 | 25 | No | 0 | none |
| 14 | 07, 21, 25, 30, 39, 45 | 3/6 | 07, 25, 45 | No | 50,000 | third |
| 15 | 13, 16, 32, 33, 38, 41 | 0/6 | — | No | 0 | none |
| 16 | 09, 14, 27, 33, 45, 53 | 1/6 | 45 | No | 0 | none |
| 17 | 13, 14, 21, 22, 31, 40 | 0/6 | — | No | 0 | none |
| 18 | 01, 09, 11, 22, 32, 55 | 0/6 | — | No | 0 | none |
| 19 | 02, 05, 07, 09, 16, 40 | 1/6 | 07 | No | 0 | none |
| 20 | 01, 02, 24, 25, 27, 41 | 1/6 | 25 | No | 0 | none |
| 21 | 11, 16, 18, 21, 29, 53 | 0/6 | — | No | 0 | none |
| 22 | 07, 18, 22, 25, 26, 38 | 2/6 | 07, 25 | No | 0 | none |
| 23 | 16, 23, 26, 27, 32, 39 | 1/6 | 23 | No | 0 | none |
| 24 | 01, 09, 13, 18, 29, 39 | 0/6 | — | No | 0 | none |
| 25 | 05, 09, 11, 23, 30, 41 | 1/6 | 23 | No | 0 | none |
| 26 | 07, 08, 14, 30, 32, 53 | 1/6 | 07 | No | 0 | none |
| 27 | 05, 21, 27, 38, 39, 55 | 0/6 | — | No | 0 | none |
| 28 | 01, 02, 21, 22, 26, 30 | 0/6 | — | No | 0 | none |
| 29 | 01, 07, 24, 33, 39, 40 | 1/6 | 07 | No | 0 | none |
| 30 | 02, 07, 29, 31, 41, 45 | 2/6 | 07, 45 | No | 0 | none |

</details>

<details>
<summary>Draw #01410 — 2026-10-13 | actual: 02, 14, 27, 40, 50, 53 | ≥3-match tickets: 0 | payout: 0 VND</summary>

- Forecast generated (UTC): 2026-10-12T21:51:13.731627+00:00
- Actual main numbers: **02, 14, 27, 40, 50, 53**
- Actual special number: **26**

**Single-line model predictions and outcomes**

| Model | Forecast numbers | Main matches | Matched numbers | Payout (VND) | Prize |
|---|---|---:|---|---:|---|
| Bayesian | 07, 08, 11, 13, 16, 22 | 0/6 | — | 0 | none |
| ExponentialDecay | 05, 07, 11, 13, 16, 18 | 0/6 | — | 0 | none |
| LogisticProbability | 07, 13, 16, 22, 25, 32 | 0/6 | — | 0 | none |
| RankEnsemble | 05, 07, 11, 13, 16, 22 | 0/6 | — | 0 | none |

**PortfolioEnsemble — 30 tickets**

| # | Predicted combination | Main matches | Matched main numbers | Special hit | Payout (VND) | Prize |
|---:|---|---:|---|---|---:|---|
| 1 | 07, 11, 13, 16, 18, 22 | 0/6 | — | No | 0 | none |
| 2 | 05, 07, 08, 11, 13, 16 | 0/6 | — | No | 0 | none |
| 3 | 01, 13, 24, 25, 27, 41 | 1/6 | 27 | No | 0 | none |
| 4 | 01, 08, 09, 14, 22, 39 | 1/6 | 14 | No | 0 | none |
| 5 | 11, 14, 21, 24, 32, 38 | 1/6 | 14 | No | 0 | none |
| 6 | 07, 27, 29, 31, 39, 55 | 1/6 | 27 | No | 0 | none |
| 7 | 07, 09, 23, 26, 38, 53 | 1/6 | 53 | Yes | 0 | none |
| 8 | 16, 26, 27, 32, 33, 39 | 1/6 | 27 | Yes | 0 | none |
| 9 | 01, 11, 23, 29, 30, 45 | 0/6 | — | No | 0 | none |
| 10 | 02, 07, 14, 30, 33, 43 | 2/6 | 02, 14 | No | 0 | none |
| 11 | 09, 13, 18, 24, 31, 45 | 0/6 | — | No | 0 | none |
| 12 | 05, 09, 16, 21, 25, 30 | 0/6 | — | No | 0 | none |
| 13 | 05, 18, 22, 27, 38, 55 | 1/6 | 27 | No | 0 | none |
| 14 | 11, 18, 25, 39, 43, 53 | 1/6 | 53 | No | 0 | none |
| 15 | 07, 08, 25, 32, 41, 45 | 0/6 | — | No | 0 | none |
| 16 | 01, 02, 13, 21, 26, 41 | 1/6 | 02 | Yes | 0 | none |
| 17 | 02, 16, 22, 24, 29, 53 | 2/6 | 02, 53 | No | 0 | none |
| 18 | 02, 08, 09, 11, 27, 31 | 2/6 | 02, 27 | No | 0 | none |
| 19 | 01, 05, 07, 18, 29, 32 | 0/6 | — | No | 0 | none |
| 20 | 13, 14, 23, 25, 27, 29 | 2/6 | 14, 27 | No | 0 | none |
| 21 | 01, 08, 16, 31, 38, 43 | 0/6 | — | No | 0 | none |
| 22 | 09, 11, 22, 33, 41, 55 | 0/6 | — | No | 0 | none |
| 23 | 07, 23, 24, 38, 39, 41 | 0/6 | — | No | 0 | none |
| 24 | 08, 13, 30, 32, 53, 55 | 1/6 | 53 | No | 0 | none |
| 25 | 14, 16, 18, 41, 45, 55 | 1/6 | 14 | No | 0 | none |
| 26 | 05, 11, 24, 26, 43, 55 | 0/6 | — | Yes | 0 | none |
| 27 | 07, 21, 27, 33, 45, 53 | 2/6 | 27, 53 | No | 0 | none |
| 28 | 07, 14, 26, 30, 31, 55 | 1/6 | 14 | Yes | 0 | none |
| 29 | 02, 05, 09, 13, 32, 43 | 1/6 | 02 | No | 0 | none |
| 30 | 01, 07, 21, 22, 24, 25 | 0/6 | — | No | 0 | none |

**UnseenPortfolioEnsemble — 30 tickets**

| # | Predicted combination | Main matches | Matched main numbers | Special hit | Payout (VND) | Prize |
|---:|---|---:|---|---|---:|---|
| 1 | 07, 11, 13, 16, 18, 22 | 0/6 | — | No | 0 | none |
| 2 | 05, 07, 08, 11, 13, 16 | 0/6 | — | No | 0 | none |
| 3 | 01, 13, 24, 25, 27, 41 | 1/6 | 27 | No | 0 | none |
| 4 | 01, 08, 09, 14, 22, 39 | 1/6 | 14 | No | 0 | none |
| 5 | 11, 14, 21, 24, 32, 38 | 1/6 | 14 | No | 0 | none |
| 6 | 07, 27, 29, 31, 39, 55 | 1/6 | 27 | No | 0 | none |
| 7 | 07, 09, 23, 26, 38, 53 | 1/6 | 53 | Yes | 0 | none |
| 8 | 16, 26, 27, 32, 33, 39 | 1/6 | 27 | Yes | 0 | none |
| 9 | 01, 11, 23, 29, 30, 45 | 0/6 | — | No | 0 | none |
| 10 | 02, 07, 14, 30, 33, 43 | 2/6 | 02, 14 | No | 0 | none |
| 11 | 09, 13, 18, 24, 31, 45 | 0/6 | — | No | 0 | none |
| 12 | 05, 09, 16, 21, 25, 30 | 0/6 | — | No | 0 | none |
| 13 | 05, 18, 22, 27, 38, 55 | 1/6 | 27 | No | 0 | none |
| 14 | 11, 18, 25, 39, 43, 53 | 1/6 | 53 | No | 0 | none |
| 15 | 07, 08, 25, 32, 41, 45 | 0/6 | — | No | 0 | none |
| 16 | 01, 02, 13, 21, 26, 41 | 1/6 | 02 | Yes | 0 | none |
| 17 | 02, 16, 22, 24, 29, 53 | 2/6 | 02, 53 | No | 0 | none |
| 18 | 02, 08, 09, 11, 27, 31 | 2/6 | 02, 27 | No | 0 | none |
| 19 | 01, 05, 07, 18, 29, 32 | 0/6 | — | No | 0 | none |
| 20 | 13, 14, 23, 25, 27, 29 | 2/6 | 14, 27 | No | 0 | none |
| 21 | 01, 08, 16, 31, 38, 43 | 0/6 | — | No | 0 | none |
| 22 | 09, 11, 22, 33, 41, 55 | 0/6 | — | No | 0 | none |
| 23 | 07, 23, 24, 38, 39, 41 | 0/6 | — | No | 0 | none |
| 24 | 08, 13, 30, 32, 53, 55 | 1/6 | 53 | No | 0 | none |
| 25 | 14, 16, 18, 41, 45, 55 | 1/6 | 14 | No | 0 | none |
| 26 | 05, 11, 24, 26, 43, 55 | 0/6 | — | Yes | 0 | none |
| 27 | 07, 21, 27, 33, 45, 53 | 2/6 | 27, 53 | No | 0 | none |
| 28 | 07, 14, 26, 30, 31, 55 | 1/6 | 14 | Yes | 0 | none |
| 29 | 02, 05, 09, 13, 32, 43 | 1/6 | 02 | No | 0 | none |
| 30 | 01, 07, 21, 22, 24, 25 | 0/6 | — | No | 0 | none |

</details>

<details>
<summary>Draw #01409 — 2026-10-10 | actual: 14, 17, 21, 23, 24, 39 | ≥3-match tickets: 1 | payout: 50,000 VND</summary>

- Forecast generated (UTC): 2026-10-09T18:57:00.685976+00:00
- Actual main numbers: **14, 17, 21, 23, 24, 39**
- Actual special number: **30**

**Single-line model predictions and outcomes**

| Model | Forecast numbers | Main matches | Matched numbers | Payout (VND) | Prize |
|---|---|---:|---|---:|---|
| Bayesian | 07, 08, 11, 13, 16, 22 | 0/6 | — | 0 | none |
| ExponentialDecay | 05, 07, 11, 13, 16, 18 | 0/6 | — | 0 | none |
| LogisticProbability | 07, 11, 16, 22, 25, 32 | 0/6 | — | 0 | none |
| RankEnsemble | 05, 07, 11, 13, 16, 22 | 0/6 | — | 0 | none |

**PortfolioEnsemble — 30 tickets**

| # | Predicted combination | Main matches | Matched main numbers | Special hit | Payout (VND) | Prize |
|---:|---|---:|---|---|---:|---|
| 1 | 07, 11, 13, 16, 18, 22 | 0/6 | — | No | 0 | none |
| 2 | 07, 11, 16, 22, 25, 32 | 0/6 | — | No | 0 | none |
| 3 | 01, 05, 07, 08, 27, 41 | 0/6 | — | No | 0 | none |
| 4 | 05, 09, 13, 24, 25, 38 | 1/6 | 24 | No | 0 | none |
| 5 | 08, 11, 31, 38, 39, 55 | 1/6 | 39 | No | 0 | none |
| 6 | 07, 21, 24, 29, 31, 53 | 2/6 | 21, 24 | No | 0 | none |
| 7 | 07, 09, 14, 26, 28, 55 | 1/6 | 14 | No | 0 | none |
| 8 | 05, 14, 16, 21, 33, 39 | 3/6 | 14, 21, 39 | No | 50,000 | third |
| 9 | 02, 05, 11, 26, 29, 45 | 0/6 | — | No | 0 | none |
| 10 | 07, 20, 30, 33, 38, 45 | 0/6 | — | Yes | 0 | none |
| 11 | 02, 08, 14, 22, 24, 30 | 2/6 | 14, 24 | Yes | 0 | none |
| 12 | 08, 18, 25, 28, 33, 53 | 0/6 | — | No | 0 | none |
| 13 | 01, 09, 16, 18, 31, 45 | 0/6 | — | No | 0 | none |
| 14 | 08, 13, 20, 21, 26, 32 | 1/6 | 21 | No | 0 | none |
| 15 | 01, 11, 20, 24, 27, 28 | 1/6 | 24 | No | 0 | none |
| 16 | 02, 07, 13, 27, 39, 53 | 1/6 | 39 | No | 0 | none |
| 17 | 01, 05, 22, 32, 53, 55 | 0/6 | — | No | 0 | none |
| 18 | 08, 16, 27, 29, 38, 41 | 0/6 | — | No | 0 | none |
| 19 | 09, 11, 18, 21, 30, 41 | 1/6 | 21 | Yes | 0 | none |
| 20 | 05, 07, 14, 18, 32, 38 | 1/6 | 14 | No | 0 | none |
| 21 | 22, 25, 26, 27, 31, 33 | 0/6 | — | No | 0 | none |
| 22 | 13, 16, 24, 41, 45, 55 | 1/6 | 24 | No | 0 | none |
| 23 | 11, 14, 20, 25, 41, 53 | 1/6 | 14 | No | 0 | none |
| 24 | 01, 07, 08, 09, 29, 39 | 1/6 | 39 | No | 0 | none |
| 25 | 21, 22, 28, 39, 41, 45 | 2/6 | 21, 39 | No | 0 | none |
| 26 | 01, 16, 26, 30, 38, 53 | 0/6 | — | Yes | 0 | none |
| 27 | 01, 13, 14, 25, 29, 31 | 1/6 | 14 | No | 0 | none |
| 28 | 01, 02, 11, 13, 32, 33 | 0/6 | — | No | 0 | none |
| 29 | 02, 07, 21, 25, 30, 55 | 1/6 | 21 | Yes | 0 | none |
| 30 | 07, 24, 26, 28, 31, 41 | 1/6 | 24 | No | 0 | none |

**UnseenPortfolioEnsemble — 30 tickets**

| # | Predicted combination | Main matches | Matched main numbers | Special hit | Payout (VND) | Prize |
|---:|---|---:|---|---|---:|---|
| 1 | 07, 11, 13, 16, 18, 22 | 0/6 | — | No | 0 | none |
| 2 | 07, 11, 16, 22, 25, 32 | 0/6 | — | No | 0 | none |
| 3 | 01, 05, 07, 08, 27, 41 | 0/6 | — | No | 0 | none |
| 4 | 05, 09, 13, 24, 25, 38 | 1/6 | 24 | No | 0 | none |
| 5 | 08, 11, 31, 38, 39, 55 | 1/6 | 39 | No | 0 | none |
| 6 | 07, 21, 24, 29, 31, 53 | 2/6 | 21, 24 | No | 0 | none |
| 7 | 07, 09, 14, 26, 28, 55 | 1/6 | 14 | No | 0 | none |
| 8 | 05, 14, 16, 21, 33, 39 | 3/6 | 14, 21, 39 | No | 50,000 | third |
| 9 | 02, 05, 11, 26, 29, 45 | 0/6 | — | No | 0 | none |
| 10 | 07, 20, 30, 33, 38, 45 | 0/6 | — | Yes | 0 | none |
| 11 | 02, 08, 14, 22, 24, 30 | 2/6 | 14, 24 | Yes | 0 | none |
| 12 | 08, 18, 25, 28, 33, 53 | 0/6 | — | No | 0 | none |
| 13 | 01, 09, 16, 18, 31, 45 | 0/6 | — | No | 0 | none |
| 14 | 08, 13, 20, 21, 26, 32 | 1/6 | 21 | No | 0 | none |
| 15 | 01, 11, 20, 24, 27, 28 | 1/6 | 24 | No | 0 | none |
| 16 | 02, 07, 13, 27, 39, 53 | 1/6 | 39 | No | 0 | none |
| 17 | 01, 05, 22, 32, 53, 55 | 0/6 | — | No | 0 | none |
| 18 | 08, 16, 27, 29, 38, 41 | 0/6 | — | No | 0 | none |
| 19 | 09, 11, 18, 21, 30, 41 | 1/6 | 21 | Yes | 0 | none |
| 20 | 05, 07, 14, 18, 32, 38 | 1/6 | 14 | No | 0 | none |
| 21 | 22, 25, 26, 27, 31, 33 | 0/6 | — | No | 0 | none |
| 22 | 13, 16, 24, 41, 45, 55 | 1/6 | 24 | No | 0 | none |
| 23 | 11, 14, 20, 25, 41, 53 | 1/6 | 14 | No | 0 | none |
| 24 | 01, 07, 08, 09, 29, 39 | 1/6 | 39 | No | 0 | none |
| 25 | 21, 22, 28, 39, 41, 45 | 2/6 | 21, 39 | No | 0 | none |
| 26 | 01, 16, 26, 30, 38, 53 | 0/6 | — | Yes | 0 | none |
| 27 | 01, 13, 14, 25, 29, 31 | 1/6 | 14 | No | 0 | none |
| 28 | 01, 02, 11, 13, 32, 33 | 0/6 | — | No | 0 | none |
| 29 | 02, 07, 21, 25, 30, 55 | 1/6 | 21 | Yes | 0 | none |
| 30 | 07, 24, 26, 28, 31, 41 | 1/6 | 24 | No | 0 | none |

</details>

<details>
<summary>Draw #01408 — 2026-10-08 | actual: 01, 07, 12, 27, 31, 52 | ≥3-match tickets: 0 | payout: 0 VND</summary>

- Forecast generated (UTC): 2026-10-07T19:27:57.366966+00:00
- Actual main numbers: **01, 07, 12, 27, 31, 52**
- Actual special number: **06**

**Single-line model predictions and outcomes**

| Model | Forecast numbers | Main matches | Matched numbers | Payout (VND) | Prize |
|---|---|---:|---|---:|---|
| Bayesian | 07, 08, 11, 13, 16, 22 | 1/6 | 07 | 0 | none |
| ExponentialDecay | 05, 07, 11, 13, 16, 18 | 1/6 | 07 | 0 | none |
| LogisticProbability | 07, 11, 16, 22, 25, 32 | 1/6 | 07 | 0 | none |
| RankEnsemble | 05, 07, 08, 11, 16, 22 | 1/6 | 07 | 0 | none |

**PortfolioEnsemble — 30 tickets**

| # | Predicted combination | Main matches | Matched main numbers | Special hit | Payout (VND) | Prize |
|---:|---|---:|---|---|---:|---|
| 1 | 07, 08, 11, 13, 16, 22 | 1/6 | 07 | No | 0 | none |
| 2 | 05, 07, 11, 13, 16, 18 | 1/6 | 07 | No | 0 | none |
| 3 | 01, 05, 22, 24, 25, 41 | 1/6 | 01 | No | 0 | none |
| 4 | 09, 11, 25, 27, 32, 55 | 1/6 | 27 | No | 0 | none |
| 5 | 07, 25, 29, 38, 39, 53 | 1/6 | 07 | No | 0 | none |
| 6 | 05, 08, 09, 14, 26, 38 | 0/6 | — | No | 0 | none |
| 7 | 11, 21, 24, 28, 38, 45 | 0/6 | — | No | 0 | none |
| 8 | 14, 16, 21, 25, 33, 43 | 0/6 | — | No | 0 | none |
| 9 | 07, 26, 28, 31, 41, 55 | 2/6 | 07, 31 | No | 0 | none |
| 10 | 14, 18, 22, 32, 39, 45 | 0/6 | — | No | 0 | none |
| 11 | 01, 02, 11, 26, 29, 33 | 1/6 | 01 | No | 0 | none |
| 12 | 16, 20, 24, 27, 31, 53 | 2/6 | 27, 31 | No | 0 | none |
| 13 | 01, 07, 09, 18, 20, 21 | 2/6 | 01, 07 | No | 0 | none |
| 14 | 02, 13, 22, 38, 43, 55 | 0/6 | — | No | 0 | none |
| 15 | 08, 11, 20, 39, 41, 43 | 0/6 | — | No | 0 | none |
| 16 | 09, 16, 28, 29, 32, 41 | 0/6 | — | No | 0 | none |
| 17 | 02, 07, 08, 24, 32, 33 | 1/6 | 07 | No | 0 | none |
| 18 | 05, 08, 21, 22, 27, 29 | 1/6 | 27 | No | 0 | none |
| 19 | 01, 05, 11, 14, 53, 55 | 1/6 | 01 | No | 0 | none |
| 20 | 13, 20, 25, 26, 27, 45 | 1/6 | 27 | No | 0 | none |
| 21 | 01, 08, 16, 31, 32, 38 | 2/6 | 01, 31 | No | 0 | none |
| 22 | 02, 07, 14, 27, 41, 45 | 2/6 | 07, 27 | No | 0 | none |
| 23 | 09, 18, 22, 28, 33, 53 | 0/6 | — | No | 0 | none |
| 24 | 09, 11, 22, 25, 31, 39 | 1/6 | 31 | No | 0 | none |
| 25 | 01, 09, 13, 24, 39, 55 | 1/6 | 01 | No | 0 | none |
| 26 | 16, 18, 24, 29, 45, 55 | 0/6 | — | No | 0 | none |
| 27 | 05, 07, 26, 32, 43, 53 | 1/6 | 07 | No | 0 | none |
| 28 | 11, 18, 27, 33, 38, 41 | 1/6 | 27 | No | 0 | none |
| 29 | 08, 13, 21, 25, 41, 53 | 0/6 | — | No | 0 | none |
| 30 | 02, 16, 21, 26, 28, 39 | 0/6 | — | No | 0 | none |

**UnseenPortfolioEnsemble — 30 tickets**

| # | Predicted combination | Main matches | Matched main numbers | Special hit | Payout (VND) | Prize |
|---:|---|---:|---|---|---:|---|
| 1 | 07, 08, 11, 13, 16, 22 | 1/6 | 07 | No | 0 | none |
| 2 | 05, 07, 11, 13, 16, 18 | 1/6 | 07 | No | 0 | none |
| 3 | 01, 05, 22, 24, 25, 41 | 1/6 | 01 | No | 0 | none |
| 4 | 09, 11, 25, 27, 32, 55 | 1/6 | 27 | No | 0 | none |
| 5 | 07, 25, 29, 38, 39, 53 | 1/6 | 07 | No | 0 | none |
| 6 | 05, 08, 09, 14, 26, 38 | 0/6 | — | No | 0 | none |
| 7 | 11, 21, 24, 28, 38, 45 | 0/6 | — | No | 0 | none |
| 8 | 14, 16, 21, 25, 33, 43 | 0/6 | — | No | 0 | none |
| 9 | 07, 26, 28, 31, 41, 55 | 2/6 | 07, 31 | No | 0 | none |
| 10 | 14, 18, 22, 32, 39, 45 | 0/6 | — | No | 0 | none |
| 11 | 01, 02, 11, 26, 29, 33 | 1/6 | 01 | No | 0 | none |
| 12 | 16, 20, 24, 27, 31, 53 | 2/6 | 27, 31 | No | 0 | none |
| 13 | 01, 07, 09, 18, 20, 21 | 2/6 | 01, 07 | No | 0 | none |
| 14 | 02, 13, 22, 38, 43, 55 | 0/6 | — | No | 0 | none |
| 15 | 08, 11, 20, 39, 41, 43 | 0/6 | — | No | 0 | none |
| 16 | 09, 16, 28, 29, 32, 41 | 0/6 | — | No | 0 | none |
| 17 | 02, 07, 08, 24, 32, 33 | 1/6 | 07 | No | 0 | none |
| 18 | 05, 08, 21, 22, 27, 29 | 1/6 | 27 | No | 0 | none |
| 19 | 01, 05, 11, 14, 53, 55 | 1/6 | 01 | No | 0 | none |
| 20 | 13, 20, 25, 26, 27, 45 | 1/6 | 27 | No | 0 | none |
| 21 | 01, 08, 16, 31, 32, 38 | 2/6 | 01, 31 | No | 0 | none |
| 22 | 02, 07, 14, 27, 41, 45 | 2/6 | 07, 27 | No | 0 | none |
| 23 | 09, 18, 22, 28, 33, 53 | 0/6 | — | No | 0 | none |
| 24 | 09, 11, 22, 25, 31, 39 | 1/6 | 31 | No | 0 | none |
| 25 | 01, 09, 13, 24, 39, 55 | 1/6 | 01 | No | 0 | none |
| 26 | 16, 18, 24, 29, 45, 55 | 0/6 | — | No | 0 | none |
| 27 | 05, 07, 26, 32, 43, 53 | 1/6 | 07 | No | 0 | none |
| 28 | 11, 18, 27, 33, 38, 41 | 1/6 | 27 | No | 0 | none |
| 29 | 08, 13, 21, 25, 41, 53 | 0/6 | — | No | 0 | none |
| 30 | 02, 16, 21, 26, 28, 39 | 0/6 | — | No | 0 | none |

</details>

<details>
<summary>Draw #01407 — 2026-10-06 | actual: 06, 07, 18, 20, 24, 27 | ≥3-match tickets: 1 | payout: 50,000 VND</summary>

- Forecast generated (UTC): 2026-10-05T21:22:46.413434+00:00
- Actual main numbers: **06, 07, 18, 20, 24, 27**
- Actual special number: **01**

**Single-line model predictions and outcomes**

| Model | Forecast numbers | Main matches | Matched numbers | Payout (VND) | Prize |
|---|---|---:|---|---:|---|
| Bayesian | 05, 08, 11, 13, 16, 22 | 0/6 | — | 0 | none |
| ExponentialDecay | 05, 07, 08, 11, 13, 16 | 1/6 | 07 | 0 | none |
| LogisticProbability | 07, 11, 16, 22, 25, 32 | 1/6 | 07 | 0 | none |
| RankEnsemble | 05, 07, 08, 11, 16, 22 | 1/6 | 07 | 0 | none |

**PortfolioEnsemble — 30 tickets**

| # | Predicted combination | Main matches | Matched main numbers | Special hit | Payout (VND) | Prize |
|---:|---|---:|---|---|---:|---|
| 1 | 05, 08, 11, 13, 16, 22 | 0/6 | — | No | 0 | none |
| 2 | 07, 11, 16, 22, 25, 32 | 1/6 | 07 | No | 0 | none |
| 3 | 01, 09, 11, 18, 38, 41 | 1/6 | 18 | Yes | 0 | none |
| 4 | 07, 13, 18, 29, 39, 55 | 2/6 | 07, 18 | No | 0 | none |
| 5 | 05, 07, 14, 21, 41, 53 | 1/6 | 07 | No | 0 | none |
| 6 | 08, 09, 14, 25, 31, 55 | 0/6 | — | No | 0 | none |
| 7 | 11, 24, 31, 33, 39, 53 | 1/6 | 24 | No | 0 | none |
| 8 | 16, 21, 24, 38, 45, 55 | 1/6 | 24 | No | 0 | none |
| 9 | 14, 18, 22, 26, 33, 45 | 1/6 | 18 | No | 0 | none |
| 10 | 02, 11, 14, 27, 29, 47 | 1/6 | 27 | No | 0 | none |
| 11 | 02, 16, 26, 39, 41, 43 | 0/6 | — | No | 0 | none |
| 12 | 01, 13, 25, 28, 45, 53 | 0/6 | — | Yes | 0 | none |
| 13 | 05, 25, 29, 33, 38, 43 | 0/6 | — | No | 0 | none |
| 14 | 01, 07, 08, 24, 26, 27 | 3/6 | 07, 24, 27 | Yes | 50,000 | third |
| 15 | 09, 21, 22, 28, 39, 47 | 0/6 | — | No | 0 | none |
| 16 | 05, 11, 26, 28, 32, 55 | 0/6 | — | No | 0 | none |
| 17 | 09, 16, 18, 27, 32, 53 | 2/6 | 18, 27 | No | 0 | none |
| 18 | 13, 31, 32, 38, 41, 47 | 0/6 | — | No | 0 | none |
| 19 | 02, 08, 13, 18, 21, 25 | 1/6 | 18 | No | 0 | none |
| 20 | 01, 22, 27, 33, 41, 55 | 1/6 | 27 | Yes | 0 | none |
| 21 | 01, 07, 11, 21, 31, 43 | 1/6 | 07 | Yes | 0 | none |
| 22 | 01, 05, 16, 29, 31, 45 | 0/6 | — | Yes | 0 | none |
| 23 | 01, 08, 14, 32, 38, 39 | 0/6 | — | Yes | 0 | none |
| 24 | 02, 07, 09, 22, 38, 53 | 1/6 | 07 | No | 0 | none |
| 25 | 08, 09, 11, 29, 41, 45 | 0/6 | — | No | 0 | none |
| 26 | 13, 14, 16, 24, 28, 43 | 1/6 | 24 | No | 0 | none |
| 27 | 05, 18, 22, 24, 25, 47 | 2/6 | 18, 24 | No | 0 | none |
| 28 | 11, 13, 21, 26, 33, 38 | 0/6 | — | No | 0 | none |
| 29 | 07, 08, 16, 28, 33, 47 | 1/6 | 07 | No | 0 | none |
| 30 | 05, 07, 09, 13, 27, 39 | 2/6 | 07, 27 | No | 0 | none |

**UnseenPortfolioEnsemble — 30 tickets**

| # | Predicted combination | Main matches | Matched main numbers | Special hit | Payout (VND) | Prize |
|---:|---|---:|---|---|---:|---|
| 1 | 05, 08, 11, 13, 16, 22 | 0/6 | — | No | 0 | none |
| 2 | 07, 11, 16, 22, 25, 32 | 1/6 | 07 | No | 0 | none |
| 3 | 01, 09, 11, 18, 38, 41 | 1/6 | 18 | Yes | 0 | none |
| 4 | 07, 13, 18, 29, 39, 55 | 2/6 | 07, 18 | No | 0 | none |
| 5 | 05, 07, 14, 21, 41, 53 | 1/6 | 07 | No | 0 | none |
| 6 | 08, 09, 14, 25, 31, 55 | 0/6 | — | No | 0 | none |
| 7 | 11, 24, 31, 33, 39, 53 | 1/6 | 24 | No | 0 | none |
| 8 | 16, 21, 24, 38, 45, 55 | 1/6 | 24 | No | 0 | none |
| 9 | 14, 18, 22, 26, 33, 45 | 1/6 | 18 | No | 0 | none |
| 10 | 02, 11, 14, 27, 29, 47 | 1/6 | 27 | No | 0 | none |
| 11 | 02, 16, 26, 39, 41, 43 | 0/6 | — | No | 0 | none |
| 12 | 01, 13, 25, 28, 45, 53 | 0/6 | — | Yes | 0 | none |
| 13 | 05, 25, 29, 33, 38, 43 | 0/6 | — | No | 0 | none |
| 14 | 01, 07, 08, 24, 26, 27 | 3/6 | 07, 24, 27 | Yes | 50,000 | third |
| 15 | 09, 21, 22, 28, 39, 47 | 0/6 | — | No | 0 | none |
| 16 | 05, 11, 26, 28, 32, 55 | 0/6 | — | No | 0 | none |
| 17 | 09, 16, 18, 27, 32, 53 | 2/6 | 18, 27 | No | 0 | none |
| 18 | 13, 31, 32, 38, 41, 47 | 0/6 | — | No | 0 | none |
| 19 | 02, 08, 13, 18, 21, 25 | 1/6 | 18 | No | 0 | none |
| 20 | 01, 22, 27, 33, 41, 55 | 1/6 | 27 | Yes | 0 | none |
| 21 | 01, 07, 11, 21, 31, 43 | 1/6 | 07 | Yes | 0 | none |
| 22 | 01, 05, 16, 29, 31, 45 | 0/6 | — | Yes | 0 | none |
| 23 | 01, 08, 14, 32, 38, 39 | 0/6 | — | Yes | 0 | none |
| 24 | 02, 07, 09, 22, 38, 53 | 1/6 | 07 | No | 0 | none |
| 25 | 08, 09, 11, 29, 41, 45 | 0/6 | — | No | 0 | none |
| 26 | 13, 14, 16, 24, 28, 43 | 1/6 | 24 | No | 0 | none |
| 27 | 05, 18, 22, 24, 25, 47 | 2/6 | 18, 24 | No | 0 | none |
| 28 | 11, 13, 21, 26, 33, 38 | 0/6 | — | No | 0 | none |
| 29 | 07, 08, 16, 28, 33, 47 | 1/6 | 07 | No | 0 | none |
| 30 | 05, 07, 09, 13, 27, 39 | 2/6 | 07, 27 | No | 0 | none |

</details>

<details>
<summary>Draw #01406 — 2026-10-03 | actual: 07, 11, 13, 16, 18, 54 | ≥3-match tickets: 2 | payout: 100,000 VND</summary>

- Forecast generated (UTC): 2026-10-02T18:36:33.757623+00:00
- Actual main numbers: **07, 11, 13, 16, 18, 54**
- Actual special number: **41**

**Single-line model predictions and outcomes**

| Model | Forecast numbers | Main matches | Matched numbers | Payout (VND) | Prize |
|---|---|---:|---|---:|---|
| Bayesian | 05, 08, 11, 13, 16, 22 | 3/6 | 11, 13, 16 | 50,000 | third |
| ExponentialDecay | 05, 08, 09, 11, 22, 25 | 1/6 | 11 | 0 | none |
| LogisticProbability | 07, 08, 11, 16, 22, 32 | 3/6 | 07, 11, 16 | 50,000 | third |
| RankEnsemble | 05, 08, 09, 11, 16, 22 | 2/6 | 11, 16 | 0 | none |

**PortfolioEnsemble — 30 tickets**

| # | Predicted combination | Main matches | Matched main numbers | Special hit | Payout (VND) | Prize |
|---:|---|---:|---|---|---:|---|
| 1 | 05, 08, 11, 16, 22, 25 | 2/6 | 11, 16 | No | 0 | none |
| 2 | 07, 08, 11, 16, 22, 32 | 3/6 | 07, 11, 16 | No | 50,000 | third |
| 3 | 05, 07, 09, 13, 38, 41 | 2/6 | 07, 13 | Yes | 0 | none |
| 4 | 01, 08, 13, 29, 39, 55 | 1/6 | 13 | No | 0 | none |
| 5 | 01, 09, 14, 18, 22, 53 | 1/6 | 18 | No | 0 | none |
| 6 | 11, 13, 14, 21, 24, 47 | 2/6 | 11, 13 | No | 0 | none |
| 7 | 08, 09, 21, 31, 33, 45 | 0/6 | — | No | 0 | none |
| 8 | 01, 02, 05, 24, 31, 32 | 0/6 | — | No | 0 | none |
| 9 | 02, 13, 22, 26, 27, 33 | 1/6 | 13 | No | 0 | none |
| 10 | 11, 26, 38, 45, 53, 55 | 1/6 | 11 | No | 0 | none |
| 11 | 02, 08, 18, 30, 41, 47 | 1/6 | 18 | Yes | 0 | none |
| 12 | 09, 16, 24, 27, 43, 55 | 1/6 | 16 | No | 0 | none |
| 13 | 05, 14, 30, 33, 39, 43 | 0/6 | — | No | 0 | none |
| 14 | 21, 22, 25, 29, 30, 38 | 0/6 | — | No | 0 | none |
| 15 | 02, 07, 09, 11, 25, 39 | 2/6 | 07, 11 | No | 0 | none |
| 16 | 08, 14, 25, 27, 32, 38 | 0/6 | — | No | 0 | none |
| 17 | 13, 16, 25, 31, 41, 53 | 2/6 | 13, 16 | Yes | 0 | none |
| 18 | 05, 07, 18, 21, 26, 55 | 2/6 | 07, 18 | No | 0 | none |
| 19 | 22, 32, 39, 41, 47, 55 | 0/6 | — | Yes | 0 | none |
| 20 | 01, 11, 27, 29, 33, 41 | 1/6 | 11 | Yes | 0 | none |
| 21 | 07, 08, 24, 29, 43, 53 | 1/6 | 07 | No | 0 | none |
| 22 | 01, 07, 16, 38, 45, 47 | 2/6 | 07, 16 | No | 0 | none |
| 23 | 05, 09, 26, 29, 32, 47 | 0/6 | — | No | 0 | none |
| 24 | 18, 22, 31, 38, 39, 43 | 1/6 | 18 | No | 0 | none |
| 25 | 11, 13, 18, 30, 32, 45 | 3/6 | 11, 13, 18 | No | 50,000 | third |
| 26 | 08, 14, 24, 26, 41, 45 | 0/6 | — | Yes | 0 | none |
| 27 | 02, 05, 16, 21, 39, 53 | 1/6 | 16 | No | 0 | none |
| 28 | 05, 13, 22, 24, 27, 45 | 1/6 | 13 | No | 0 | none |
| 29 | 02, 11, 14, 29, 31, 55 | 1/6 | 11 | No | 0 | none |
| 30 | 05, 08, 33, 38, 53, 55 | 0/6 | — | No | 0 | none |

**UnseenPortfolioEnsemble — 30 tickets**

| # | Predicted combination | Main matches | Matched main numbers | Special hit | Payout (VND) | Prize |
|---:|---|---:|---|---|---:|---|
| 1 | 05, 08, 11, 16, 22, 25 | 2/6 | 11, 16 | No | 0 | none |
| 2 | 07, 08, 11, 16, 22, 32 | 3/6 | 07, 11, 16 | No | 50,000 | third |
| 3 | 05, 07, 09, 13, 38, 41 | 2/6 | 07, 13 | Yes | 0 | none |
| 4 | 01, 08, 13, 29, 39, 55 | 1/6 | 13 | No | 0 | none |
| 5 | 01, 09, 14, 18, 22, 53 | 1/6 | 18 | No | 0 | none |
| 6 | 11, 13, 14, 21, 24, 47 | 2/6 | 11, 13 | No | 0 | none |
| 7 | 08, 09, 21, 31, 33, 45 | 0/6 | — | No | 0 | none |
| 8 | 01, 02, 05, 24, 31, 32 | 0/6 | — | No | 0 | none |
| 9 | 02, 13, 22, 26, 27, 33 | 1/6 | 13 | No | 0 | none |
| 10 | 11, 26, 38, 45, 53, 55 | 1/6 | 11 | No | 0 | none |
| 11 | 02, 08, 18, 30, 41, 47 | 1/6 | 18 | Yes | 0 | none |
| 12 | 09, 16, 24, 27, 43, 55 | 1/6 | 16 | No | 0 | none |
| 13 | 05, 14, 30, 33, 39, 43 | 0/6 | — | No | 0 | none |
| 14 | 21, 22, 25, 29, 30, 38 | 0/6 | — | No | 0 | none |
| 15 | 02, 07, 09, 11, 25, 39 | 2/6 | 07, 11 | No | 0 | none |
| 16 | 08, 14, 25, 27, 32, 38 | 0/6 | — | No | 0 | none |
| 17 | 13, 16, 25, 31, 41, 53 | 2/6 | 13, 16 | Yes | 0 | none |
| 18 | 05, 07, 18, 21, 26, 55 | 2/6 | 07, 18 | No | 0 | none |
| 19 | 22, 32, 39, 41, 47, 55 | 0/6 | — | Yes | 0 | none |
| 20 | 01, 11, 27, 29, 33, 41 | 1/6 | 11 | Yes | 0 | none |
| 21 | 07, 08, 24, 29, 43, 53 | 1/6 | 07 | No | 0 | none |
| 22 | 01, 07, 16, 38, 45, 47 | 2/6 | 07, 16 | No | 0 | none |
| 23 | 05, 09, 26, 29, 32, 47 | 0/6 | — | No | 0 | none |
| 24 | 18, 22, 31, 38, 39, 43 | 1/6 | 18 | No | 0 | none |
| 25 | 11, 13, 18, 30, 32, 45 | 3/6 | 11, 13, 18 | No | 50,000 | third |
| 26 | 08, 14, 24, 26, 41, 45 | 0/6 | — | Yes | 0 | none |
| 27 | 02, 05, 16, 21, 39, 53 | 1/6 | 16 | No | 0 | none |
| 28 | 05, 13, 22, 24, 27, 45 | 1/6 | 13 | No | 0 | none |
| 29 | 02, 11, 14, 29, 31, 55 | 1/6 | 11 | No | 0 | none |
| 30 | 05, 08, 33, 38, 53, 55 | 0/6 | — | No | 0 | none |

</details>

<details>
<summary>Draw #01405 — 2026-10-01 | actual: 04, 05, 13, 34, 52, 55 | ≥3-match tickets: 0 | payout: 0 VND</summary>

- Forecast generated (UTC): 2026-10-01T02:21:22.281174+00:00
- Actual main numbers: **04, 05, 13, 34, 52, 55**
- Actual special number: **15**

**Single-line model predictions and outcomes**

| Model | Forecast numbers | Main matches | Matched numbers | Payout (VND) | Prize |
|---|---|---:|---|---:|---|
| Bayesian | 05, 08, 11, 16, 22, 41 | 1/6 | 05 | 0 | none |
| ExponentialDecay | 05, 08, 09, 11, 22, 25 | 1/6 | 05 | 0 | none |
| LogisticProbability | 08, 16, 22, 32, 47, 53 | 0/6 | — | 0 | none |
| RankEnsemble | 05, 08, 09, 11, 16, 22 | 1/6 | 05 | 0 | none |

**PortfolioEnsemble — 30 tickets**

| # | Predicted combination | Main matches | Matched main numbers | Special hit | Payout (VND) | Prize |
|---:|---|---:|---|---|---:|---|
| 1 | 05, 08, 11, 16, 22, 25 | 1/6 | 05 | No | 0 | none |
| 2 | 08, 16, 22, 32, 47, 53 | 0/6 | — | No | 0 | none |
| 3 | 01, 07, 09, 11, 38, 41 | 0/6 | — | No | 0 | none |
| 4 | 08, 09, 13, 29, 39, 55 | 2/6 | 13, 55 | No | 0 | none |
| 5 | 07, 13, 14, 18, 22, 24 | 1/6 | 13 | No | 0 | none |
| 6 | 11, 13, 26, 31, 32, 33 | 1/6 | 13 | No | 0 | none |
| 7 | 02, 08, 14, 31, 38, 45 | 0/6 | — | No | 0 | none |
| 8 | 01, 05, 18, 27, 33, 55 | 2/6 | 05, 55 | No | 0 | none |
| 9 | 22, 26, 30, 39, 41, 45 | 0/6 | — | No | 0 | none |
| 10 | 11, 14, 29, 30, 53, 55 | 1/6 | 55 | No | 0 | none |
| 11 | 09, 16, 24, 27, 28, 31 | 0/6 | — | No | 0 | none |
| 12 | 07, 08, 18, 26, 28, 29 | 0/6 | — | No | 0 | none |
| 13 | 21, 22, 25, 33, 38, 53 | 0/6 | — | No | 0 | none |
| 14 | 02, 05, 11, 18, 39, 47 | 1/6 | 05 | No | 0 | none |
| 15 | 01, 13, 16, 25, 45, 47 | 1/6 | 13 | No | 0 | none |
| 16 | 05, 08, 21, 24, 27, 41 | 1/6 | 05 | No | 0 | none |
| 17 | 02, 07, 09, 22, 32, 55 | 1/6 | 55 | No | 0 | none |
| 18 | 07, 11, 21, 27, 45, 53 | 0/6 | — | No | 0 | none |
| 19 | 16, 24, 26, 38, 39, 55 | 1/6 | 55 | No | 0 | none |
| 20 | 01, 07, 08, 30, 31, 39 | 0/6 | — | No | 0 | none |
| 21 | 01, 05, 22, 29, 31, 41 | 1/6 | 05 | No | 0 | none |
| 22 | 02, 11, 24, 25, 33, 41 | 0/6 | — | No | 0 | none |
| 23 | 14, 16, 18, 21, 28, 41 | 0/6 | — | No | 0 | none |
| 24 | 08, 09, 14, 26, 33, 47 | 0/6 | — | No | 0 | none |
| 25 | 13, 22, 27, 28, 30, 38 | 1/6 | 13 | No | 0 | none |
| 26 | 05, 07, 16, 29, 30, 33 | 1/6 | 05 | No | 0 | none |
| 27 | 08, 13, 18, 38, 41, 53 | 1/6 | 13 | No | 0 | none |
| 28 | 08, 24, 28, 33, 45, 55 | 1/6 | 55 | No | 0 | none |
| 29 | 02, 08, 25, 27, 30, 32 | 0/6 | — | No | 0 | none |
| 30 | 01, 08, 11, 16, 21, 22 | 0/6 | — | No | 0 | none |

**UnseenPortfolioEnsemble — 30 tickets**

| # | Predicted combination | Main matches | Matched main numbers | Special hit | Payout (VND) | Prize |
|---:|---|---:|---|---|---:|---|
| 1 | 05, 08, 11, 16, 22, 25 | 1/6 | 05 | No | 0 | none |
| 2 | 08, 16, 22, 32, 47, 53 | 0/6 | — | No | 0 | none |
| 3 | 01, 07, 09, 11, 38, 41 | 0/6 | — | No | 0 | none |
| 4 | 08, 09, 13, 29, 39, 55 | 2/6 | 13, 55 | No | 0 | none |
| 5 | 07, 13, 14, 18, 22, 24 | 1/6 | 13 | No | 0 | none |
| 6 | 11, 13, 26, 31, 32, 33 | 1/6 | 13 | No | 0 | none |
| 7 | 02, 08, 14, 31, 38, 45 | 0/6 | — | No | 0 | none |
| 8 | 01, 05, 18, 27, 33, 55 | 2/6 | 05, 55 | No | 0 | none |
| 9 | 22, 26, 30, 39, 41, 45 | 0/6 | — | No | 0 | none |
| 10 | 11, 14, 29, 30, 53, 55 | 1/6 | 55 | No | 0 | none |
| 11 | 09, 16, 24, 27, 28, 31 | 0/6 | — | No | 0 | none |
| 12 | 07, 08, 18, 26, 28, 29 | 0/6 | — | No | 0 | none |
| 13 | 21, 22, 25, 33, 38, 53 | 0/6 | — | No | 0 | none |
| 14 | 02, 05, 11, 18, 39, 47 | 1/6 | 05 | No | 0 | none |
| 15 | 01, 13, 16, 25, 45, 47 | 1/6 | 13 | No | 0 | none |
| 16 | 05, 08, 21, 24, 27, 41 | 1/6 | 05 | No | 0 | none |
| 17 | 02, 07, 09, 22, 32, 55 | 1/6 | 55 | No | 0 | none |
| 18 | 07, 11, 21, 27, 45, 53 | 0/6 | — | No | 0 | none |
| 19 | 16, 24, 26, 38, 39, 55 | 1/6 | 55 | No | 0 | none |
| 20 | 01, 07, 08, 30, 31, 39 | 0/6 | — | No | 0 | none |
| 21 | 01, 05, 22, 29, 31, 41 | 1/6 | 05 | No | 0 | none |
| 22 | 02, 11, 24, 25, 33, 41 | 0/6 | — | No | 0 | none |
| 23 | 14, 16, 18, 21, 28, 41 | 0/6 | — | No | 0 | none |
| 24 | 08, 09, 14, 26, 33, 47 | 0/6 | — | No | 0 | none |
| 25 | 13, 22, 27, 28, 30, 38 | 1/6 | 13 | No | 0 | none |
| 26 | 05, 07, 16, 29, 30, 33 | 1/6 | 05 | No | 0 | none |
| 27 | 08, 13, 18, 38, 41, 53 | 1/6 | 13 | No | 0 | none |
| 28 | 08, 24, 28, 33, 45, 55 | 1/6 | 55 | No | 0 | none |
| 29 | 02, 08, 25, 27, 30, 32 | 0/6 | — | No | 0 | none |
| 30 | 01, 08, 11, 16, 21, 22 | 0/6 | — | No | 0 | none |

</details>

**Machine-readable and full reports:** [Evaluation JSON](./artifacts/forecast/results/forecast_results.json) · [Evaluation Markdown](./artifacts/forecast/results/forecast_results.md) · [Latest forecast JSON](./artifacts/forecast/next_power655.json)


## 📊 Data Statistics

| Product | Total Draws | Start Date | End Date | Total Records | First ID | Latest ID |
| --- | --- | --- | --- | --- | --- | --- |
| Power 655 | 1412 | 2017-08-01 | 2026-10-17 | 1412 | 00001 | 01412 |
| Power 645 | 1349 | 2017-10-25 | 2026-09-05 | 1349 | 00198 | 01546 |
| Power 535 | 369 | 2025-06-29 | 2026-08-08 | 736 | 00001 | 00812 |
| Keno | 639 | 2022-12-04 | 2026-08-08 | 80278 | #0110271 | #0291333 |
| 3D | 1112 | 2019-04-22 | 2026-08-07 | 1112 | 00001 | 01116 |
| 3D Pro | 759 | 2021-09-14 | 2026-08-08 | 759 | 00001 | 00763 |
| Bingo18 | 612 | 2024-12-03 | 2026-08-08 | 84709 | 0083123 | 0180633 |

## 📈 Power 6/55 Analysis

### 📅 Recent Results (Last 10 draws)
| date | id | result | process_time | source |
| --- | --- | --- | --- | --- |
| 2026-10-17 | 01412 | [1, 10, 11, 12, 16, 37, 48] | 2026-10-17T15:34:59.050994 | baomoi.com |
| 2026-10-15 | 01411 | [7, 23, 25, 42, 45, 51, 4] | 2026-10-15T15:52:49.428277 | baomoi.com |
| 2026-10-13 | 01410 | [2, 14, 27, 40, 50, 53, 26] | 2026-10-14T01:22:56.824473 | baomoi.com |
| 2026-10-10 | 01409 | [14, 17, 21, 23, 24, 39, 30] | 2026-10-11T01:14:18.654267 | baomoi.com |
| 2026-10-08 | 01408 | [1, 7, 12, 27, 31, 52, 6] | 2026-10-09T18:53:51.307533 |  |
| 2026-10-06 | 01407 | [6, 7, 18, 20, 24, 27, 1] | 2026-10-07T19:25:51.351855 |  |
| 2026-10-03 | 01406 | [7, 11, 13, 16, 18, 54, 41] | 2026-10-05T21:20:39.061088 |  |
| 2026-10-01 | 01405 | [4, 5, 13, 34, 52, 55, 15] | 2026-10-02T18:34:26.030763 |  |
| 2026-09-29 | 01404 | [2, 4, 13, 17, 35, 36, 11] | 2026-10-01T02:18:11.319053 |  |
| 2026-09-26 | 01403 | [14, 18, 21, 38, 48, 52, 49] | 2026-10-01T02:18:09.794263 |  |

### 🎲 Number Frequency (All Time)
| result | count | % | -1 | 1result | 1count | 1% | -2 | 2result | 2count | 2% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 162 | 1.91 |  | 21 | 153 | 1.81 |  | 41 | 177 | 2.09 |
| 2 | 139 | 1.64 |  | 22 | 179 | 2.11 |  | 42 | 159 | 1.88 |
| 3 | 162 | 1.91 |  | 23 | 165 | 1.95 |  | 43 | 166 | 1.96 |
| 4 | 126 | 1.49 |  | 24 | 161 | 1.9 |  | 44 | 160 | 1.89 |
| 5 | 157 | 1.85 |  | 25 | 145 | 1.71 |  | 45 | 149 | 1.76 |
| 6 | 133 | 1.57 |  | 26 | 148 | 1.75 |  | 46 | 155 | 1.83 |
| 7 | 142 | 1.68 |  | 27 | 145 | 1.71 |  | 47 | 161 | 1.9 |
| 8 | 170 | 2.01 |  | 28 | 129 | 1.52 |  | 48 | 162 | 1.91 |
| 9 | 163 | 1.92 |  | 29 | 170 | 2.01 |  | 49 | 151 | 1.78 |
| 10 | 145 | 1.71 |  | 30 | 145 | 1.71 |  | 50 | 143 | 1.69 |
| 11 | 167 | 1.97 |  | 31 | 154 | 1.82 |  | 51 | 173 | 2.04 |
| 12 | 158 | 1.86 |  | 32 | 169 | 1.99 |  | 52 | 152 | 1.79 |
| 13 | 156 | 1.84 |  | 33 | 161 | 1.9 |  | 53 | 164 | 1.94 |
| 14 | 148 | 1.75 |  | 34 | 170 | 2.01 |  | 54 | 143 | 1.69 |
| 15 | 134 | 1.58 |  | 35 | 141 | 1.66 |  | 55 | 157 | 1.85 |
| 16 | 150 | 1.77 |  | 36 | 143 | 1.69 |  |  |  |  |
| 17 | 144 | 1.7 |  | 37 | 133 | 1.57 |  |  |  |  |
| 18 | 162 | 1.91 |  | 38 | 152 | 1.79 |  |  |  |  |
| 19 | 148 | 1.75 |  | 39 | 154 | 1.82 |  |  |  |  |
| 20 | 157 | 1.85 |  | 40 | 160 | 1.89 |  |  |  |  |

### 📊 Frequency Analysis by Period

#### Last 30 Days
| result | count | % | -1 | 1result | 1count | 1% | -2 | 2result | 2count | 2% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 4 | 5.56 |  | 25 | 2 | 2.78 |  | 53 | 1 | 1.39 |
| 2 | 2 | 2.78 |  | 26 | 1 | 1.39 |  | 54 | 1 | 1.39 |
| 3 | 1 | 1.39 |  | 27 | 3 | 4.17 |  | 55 | 1 | 1.39 |
| 4 | 2 | 2.78 |  | 28 | 1 | 1.39 |  |  |  |  |
| 5 | 1 | 1.39 |  | 31 | 1 | 1.39 |  |  |  |  |
| 6 | 1 | 1.39 |  | 34 | 1 | 1.39 |  |  |  |  |
| 7 | 4 | 5.56 |  | 35 | 1 | 1.39 |  |  |  |  |
| 9 | 1 | 1.39 |  | 36 | 1 | 1.39 |  |  |  |  |
| 10 | 1 | 1.39 |  | 37 | 1 | 1.39 |  |  |  |  |
| 11 | 3 | 4.17 |  | 38 | 1 | 1.39 |  |  |  |  |
| 12 | 2 | 2.78 |  | 39 | 1 | 1.39 |  |  |  |  |
| 13 | 4 | 5.56 |  | 40 | 1 | 1.39 |  |  |  |  |
| 14 | 3 | 4.17 |  | 41 | 1 | 1.39 |  |  |  |  |
| 16 | 2 | 2.78 |  | 42 | 1 | 1.39 |  |  |  |  |
| 17 | 2 | 2.78 |  | 45 | 1 | 1.39 |  |  |  |  |
| 18 | 3 | 4.17 |  | 46 | 1 | 1.39 |  |  |  |  |
| 20 | 1 | 1.39 |  | 48 | 1 | 1.39 |  |  |  |  |
| 21 | 2 | 2.78 |  | 50 | 1 | 1.39 |  |  |  |  |
| 23 | 3 | 4.17 |  | 51 | 1 | 1.39 |  |  |  |  |
| 24 | 2 | 2.78 |  | 52 | 3 | 4.17 |  |  |  |  |

#### Last 60 Days
| result | count | % | -1 | 1result | 1count | 1% | -2 | 2result | 2count | 2% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 6 | 4.0 |  | 21 | 4 | 2.67 |  | 42 | 2 | 1.33 |
| 2 | 3 | 2.0 |  | 22 | 1 | 0.67 |  | 43 | 1 | 0.67 |
| 3 | 2 | 1.33 |  | 23 | 4 | 2.67 |  | 44 | 2 | 1.33 |
| 4 | 3 | 2.0 |  | 24 | 5 | 3.33 |  | 45 | 3 | 2.0 |
| 5 | 4 | 2.67 |  | 25 | 6 | 4.0 |  | 46 | 2 | 1.33 |
| 6 | 2 | 1.33 |  | 26 | 2 | 1.33 |  | 47 | 4 | 2.67 |
| 7 | 7 | 4.67 |  | 27 | 5 | 3.33 |  | 48 | 1 | 0.67 |
| 8 | 2 | 1.33 |  | 28 | 2 | 1.33 |  | 49 | 1 | 0.67 |
| 9 | 4 | 2.67 |  | 29 | 1 | 0.67 |  | 50 | 1 | 0.67 |
| 10 | 2 | 1.33 |  | 31 | 4 | 2.67 |  | 51 | 2 | 1.33 |
| 11 | 8 | 5.33 |  | 32 | 2 | 1.33 |  | 52 | 3 | 2.0 |
| 12 | 2 | 1.33 |  | 33 | 1 | 0.67 |  | 53 | 2 | 1.33 |
| 13 | 5 | 3.33 |  | 34 | 2 | 1.33 |  | 54 | 3 | 2.0 |
| 14 | 4 | 2.67 |  | 35 | 1 | 0.67 |  | 55 | 2 | 1.33 |
| 15 | 1 | 0.67 |  | 36 | 3 | 2.0 |  |  |  |  |
| 16 | 3 | 2.0 |  | 37 | 2 | 1.33 |  |  |  |  |
| 17 | 3 | 2.0 |  | 38 | 2 | 1.33 |  |  |  |  |
| 18 | 6 | 4.0 |  | 39 | 1 | 0.67 |  |  |  |  |
| 19 | 1 | 0.67 |  | 40 | 2 | 1.33 |  |  |  |  |
| 20 | 1 | 0.67 |  | 41 | 2 | 1.33 |  |  |  |  |

#### Last 90 Days
| result | count | % | -1 | 1result | 1count | 1% | -2 | 2result | 2count | 2% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 7 | 3.07 |  | 21 | 4 | 1.75 |  | 41 | 4 | 1.75 |
| 2 | 6 | 2.63 |  | 22 | 2 | 0.88 |  | 42 | 3 | 1.32 |
| 3 | 4 | 1.75 |  | 23 | 6 | 2.63 |  | 43 | 2 | 0.88 |
| 4 | 3 | 1.32 |  | 24 | 6 | 2.63 |  | 44 | 4 | 1.75 |
| 5 | 7 | 3.07 |  | 25 | 7 | 3.07 |  | 45 | 5 | 2.19 |
| 6 | 2 | 0.88 |  | 26 | 2 | 0.88 |  | 46 | 3 | 1.32 |
| 7 | 9 | 3.95 |  | 27 | 9 | 3.95 |  | 47 | 5 | 2.19 |
| 8 | 4 | 1.75 |  | 28 | 3 | 1.32 |  | 48 | 2 | 0.88 |
| 9 | 6 | 2.63 |  | 29 | 4 | 1.75 |  | 49 | 3 | 1.32 |
| 10 | 2 | 0.88 |  | 30 | 1 | 0.44 |  | 50 | 4 | 1.75 |
| 11 | 9 | 3.95 |  | 31 | 4 | 1.75 |  | 51 | 4 | 1.75 |
| 12 | 3 | 1.32 |  | 32 | 2 | 0.88 |  | 52 | 3 | 1.32 |
| 13 | 5 | 2.19 |  | 33 | 3 | 1.32 |  | 53 | 2 | 0.88 |
| 14 | 7 | 3.07 |  | 34 | 2 | 0.88 |  | 54 | 4 | 1.75 |
| 15 | 2 | 0.88 |  | 35 | 2 | 0.88 |  | 55 | 5 | 2.19 |
| 16 | 5 | 2.19 |  | 36 | 3 | 1.32 |  |  |  |  |
| 17 | 3 | 1.32 |  | 37 | 3 | 1.32 |  |  |  |  |
| 18 | 8 | 3.51 |  | 38 | 6 | 2.63 |  |  |  |  |
| 19 | 2 | 0.88 |  | 39 | 4 | 1.75 |  |  |  |  |
| 20 | 3 | 1.32 |  | 40 | 5 | 2.19 |  |  |  |  |

### ⏳ Top 10 số lâu chưa xuất hiện (Top 10 Numbers by Days Since Last Appearance)
| result | last_date | days_since |
| --- | --- | --- |
| 30 | 2026-08-15 | 63 |
| 19 | 2026-08-22 | 56 |
| 15 | 2026-08-29 | 49 |
| 29 | 2026-08-29 | 49 |
| 49 | 2026-09-01 | 46 |
| 44 | 2026-09-01 | 46 |
| 33 | 2026-09-05 | 42 |
| 8 | 2026-09-08 | 39 |
| 43 | 2026-09-12 | 35 |
| 32 | 2026-09-15 | 32 |

### 📆 Số ngày từ lần xuất hiện cuối cùng (Days Since Last Appearance - All Numbers)
| result | last_date | days_since |
| --- | --- | --- |
| 1 | 2026-10-17 | 0 |
| 2 | 2026-10-13 | 4 |
| 3 | 2026-09-22 | 25 |
| 4 | 2026-10-01 | 16 |
| 5 | 2026-10-01 | 16 |
| 6 | 2026-10-06 | 11 |
| 7 | 2026-10-15 | 2 |
| 8 | 2026-09-08 | 39 |
| 9 | 2026-09-22 | 25 |
| 10 | 2026-10-17 | 0 |
| 11 | 2026-10-17 | 0 |
| 12 | 2026-10-17 | 0 |
| 13 | 2026-10-03 | 14 |
| 14 | 2026-10-13 | 4 |
| 15 | 2026-08-29 | 49 |
| 16 | 2026-10-17 | 0 |
| 17 | 2026-10-10 | 7 |
| 18 | 2026-10-06 | 11 |
| 19 | 2026-08-22 | 56 |
| 20 | 2026-10-06 | 11 |
| 21 | 2026-10-10 | 7 |
| 22 | 2026-09-19 | 28 |
| 23 | 2026-10-15 | 2 |
| 24 | 2026-10-10 | 7 |
| 25 | 2026-10-15 | 2 |
| 26 | 2026-09-24 | 23 |
| 27 | 2026-10-13 | 4 |
| 28 | 2026-09-24 | 23 |
| 29 | 2026-08-29 | 49 |
| 30 | 2026-08-15 | 63 |
| 31 | 2026-10-08 | 9 |
| 32 | 2026-09-15 | 32 |
| 33 | 2026-09-05 | 42 |
| 34 | 2026-10-01 | 16 |
| 35 | 2026-09-29 | 18 |
| 36 | 2026-09-29 | 18 |
| 37 | 2026-10-17 | 0 |
| 38 | 2026-09-26 | 21 |
| 39 | 2026-10-10 | 7 |
| 40 | 2026-10-13 | 4 |
| 41 | 2026-09-22 | 25 |
| 42 | 2026-10-15 | 2 |
| 43 | 2026-09-12 | 35 |
| 44 | 2026-09-01 | 46 |
| 45 | 2026-10-15 | 2 |
| 46 | 2026-09-22 | 25 |
| 47 | 2026-09-15 | 32 |
| 48 | 2026-09-26 | 21 |
| 49 | 2026-09-01 | 46 |
| 50 | 2026-10-13 | 4 |
| 51 | 2026-10-15 | 2 |
| 52 | 2026-10-08 | 9 |
| 53 | 2026-10-13 | 4 |
| 54 | 2026-10-03 | 14 |
| 55 | 2026-10-01 | 16 |



## ⚙️ How It Works

### 🤖 Automated Data Collection

This project runs completely automatically using **GitHub Actions** - no server required!

- **⏰ Schedule**: Runs daily via [GitHub Actions workflow](.github/workflows/crawl.yml)
- **🔄 Process**: Fetches latest results → Processes data → Commits to repository
- **📊 Analysis**: Generates statistics and updates README automatically

### 🕵️ Data Crawling Method

The data collection works by:
1. **🔍 Network Analysis**: Inspecting browser-server communication
2. **🐍 Python Replication**: Recreating the data fetch logic in Python
3. **📋 Structured Storage**: Saving results in JSONL format for easy analysis
4. **🔄 Continuous Updates**: Daily automated runs ensure fresh data

> **Note**: This is purely for educational and research purposes. No gambling advice is provided.


## 🚀 Installation & Usage

### 📦 Install via pip

```bash
pip install vietlott-data
```

### 💻 Command Line Interface

#### 🔍 Crawl Data

```bash
vietlott-crawl [OPTIONS] PRODUCT

# Options:
#   --run-date TEXT       Specific date to crawl (default: current date)
#   --index-from INTEGER  Starting page index (default: 0)
#   --index-to INTEGER    Ending page index (default: None)
#   --help               Show help message
```

#### 🔧 Backfill Missing Data

```bash
vietlott-missing [OPTIONS] PRODUCT

# Options:
#   --limit INTEGER  Number of pages to process (default: 20)
#   --help          Show help message
```

> **Available Products**: power_655, power_645, power_535, keno, 3d, 3d_pro, bingo18

### 🛠️ Development Setup

```bash
# Clone the repository
git clone https://github.com/mr2along/vietlott-data.git ; cd vietlott-data

# Install dependencies (recommend using uv and virtual environment)
uv sync --dev

# Run tests
uv run pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <strong>⭐ If you find this project useful, please consider giving it a star!</strong>
</div>

