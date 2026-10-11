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
- [Predictions](#predictions)
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

Forecasts are produced for research and retrospective evaluation only. Lottery draws are random; model outputs are not guarantees of future results.

### Latest evaluated forecast

| Field | Result |
|---|---|
| Target draw | **#01409 — 2026-10-10** |
| Forecast generated (UTC) | 2026-10-09 18:57:00 |
| Data available to the model | Through draw **#01408** (1,408 rows) |
| Actual main numbers | **14, 17, 21, 23, 24, 39** |
| Actual special number | **30** (reported separately; not used as a model feature) |

The four single-line model predictions each matched **0 of 6** main numbers:

| Model | Predicted numbers | Main matches |
|---|---|---:|
| Bayesian | 7, 8, 11, 13, 16, 22 | 0/6 |
| ExponentialDecay | 5, 7, 11, 13, 16, 18 | 0/6 |
| LogisticProbability | 7, 11, 16, 22, 25, 32 | 0/6 |
| RankEnsemble | 5, 7, 11, 13, 16, 22 | 0/6 |

For the 30-ticket portfolio, one ticket matched three main numbers: **[5, 14, 16, 21, 33, 39]** matched **14, 21, 39** and recorded a payout of **50,000 VND**. With an assumed ticket price of 10,000 VND, that draw's portfolio cost was 300,000 VND, net result **−250,000 VND** and ROI **−83.33%**.

### Rolling realized results — latest 5 evaluated draws

| Draw | Date | Actual main numbers | Special | Tickets with ≥3 main matches | Recorded payout (VND) |
|---:|---|---|---:|---:|---:|
| 01405 | 2026-10-01 | 4, 5, 13, 34, 52, 55 | 15 | 0 | 0 |
| 01406 | 2026-10-03 | 7, 11, 13, 16, 18, 54 | 41 | 2 | 100,000 |
| 01407 | 2026-10-06 | 6, 7, 18, 20, 24, 27 | 1 | 1 | 50,000 |
| 01408 | 2026-10-08 | 1, 7, 12, 27, 31, 52 | 6 | 0 | 0 |
| 01409 | 2026-10-10 | 14, 17, 21, 23, 24, 39 | 30 | 1 | 50,000 |

### Aggregate portfolio performance

The evaluation report currently contains **5 completed draws** and **0 pending forecasts**. Each strategy evaluates 30 tickets per draw (150 tickets total per strategy).

| Strategy | Draws | Tickets | Tickets with ≥3 matches | ≥3-match rate | Recorded payout | Cost* | Net* | ROI* |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| PortfolioEnsemble | 5 | 150 | 4 | 2.67% | 200,000 VND | 1,500,000 VND | −1,300,000 VND | −86.67% |
| UnseenPortfolioEnsemble | 5 | 150 | 4 | 2.67% | 200,000 VND | 1,500,000 VND | −1,300,000 VND | −86.67% |

\*Cost/net/ROI are calculated using 10,000 VND per ticket and the payout values in the evaluation artifact. The observed sample is small and does **not** establish a predictive advantage.

**Reports and artifacts:** [Full ticket-level evaluation report](./artifacts/forecast/results/forecast_results.md) · [Machine-readable results](./artifacts/forecast/results/forecast_results.json) · [Forecast JSON for draw #01409](./artifacts/forecast/next_power655.json)

## 📊 Data Statistics

| Product | Total Draws | Start Date | End Date | Total Records | First ID | Latest ID |
| --- | --- | --- | --- | --- | --- | --- |
| Power 655 | 1409 | 2017-08-01 | 2026-10-10 | 1409 | 00001 | 01409 |
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
| 2026-10-10 | 01409 | [14, 17, 21, 23, 24, 39, 30] | 2026-10-11T01:14:18.654267 | baomoi.com |
| 2026-10-08 | 01408 | [1, 7, 12, 27, 31, 52, 6] | 2026-10-09T18:53:51.307533 |  |
| 2026-10-06 | 01407 | [6, 7, 18, 20, 24, 27, 1] | 2026-10-07T19:25:51.351855 |  |
| 2026-10-03 | 01406 | [7, 11, 13, 16, 18, 54, 41] | 2026-10-05T21:20:39.061088 |  |
| 2026-10-01 | 01405 | [4, 5, 13, 34, 52, 55, 15] | 2026-10-02T18:34:26.030763 |  |
| 2026-09-29 | 01404 | [2, 4, 13, 17, 35, 36, 11] | 2026-10-01T02:18:11.319053 |  |
| 2026-09-26 | 01403 | [14, 18, 21, 38, 48, 52, 49] | 2026-10-01T02:18:09.794263 |  |
| 2026-09-24 | 01402 | [1, 13, 23, 25, 26, 28, 27] | 2026-10-01T02:18:08.286342 |  |
| 2026-09-22 | 01401 | [1, 3, 9, 11, 41, 46, 10] | 2026-10-01T02:18:06.812471 |  |
| 2026-09-19 | 01400 | [4, 7, 11, 18, 22, 25, 50] | 2026-10-01T02:18:05.308248 |  |

### 🎲 Number Frequency (All Time)
| result | count | % | -1 | 1result | 1count | 1% | -2 | 2result | 2count | 2% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 161 | 1.9 |  | 21 | 153 | 1.81 |  | 41 | 177 | 2.09 |
| 2 | 138 | 1.63 |  | 22 | 179 | 2.12 |  | 42 | 158 | 1.87 |
| 3 | 162 | 1.92 |  | 23 | 164 | 1.94 |  | 43 | 166 | 1.96 |
| 4 | 126 | 1.49 |  | 24 | 161 | 1.9 |  | 44 | 160 | 1.89 |
| 5 | 157 | 1.86 |  | 25 | 144 | 1.7 |  | 45 | 148 | 1.75 |
| 6 | 133 | 1.57 |  | 26 | 148 | 1.75 |  | 46 | 155 | 1.83 |
| 7 | 141 | 1.67 |  | 27 | 144 | 1.7 |  | 47 | 161 | 1.9 |
| 8 | 170 | 2.01 |  | 28 | 129 | 1.53 |  | 48 | 162 | 1.92 |
| 9 | 163 | 1.93 |  | 29 | 170 | 2.01 |  | 49 | 151 | 1.79 |
| 10 | 144 | 1.7 |  | 30 | 145 | 1.72 |  | 50 | 142 | 1.68 |
| 11 | 166 | 1.96 |  | 31 | 154 | 1.82 |  | 51 | 172 | 2.03 |
| 12 | 157 | 1.86 |  | 32 | 169 | 2.0 |  | 52 | 152 | 1.8 |
| 13 | 156 | 1.85 |  | 33 | 161 | 1.9 |  | 53 | 163 | 1.93 |
| 14 | 147 | 1.74 |  | 34 | 170 | 2.01 |  | 54 | 143 | 1.69 |
| 15 | 134 | 1.59 |  | 35 | 141 | 1.67 |  | 55 | 157 | 1.86 |
| 16 | 149 | 1.76 |  | 36 | 143 | 1.69 |  |  |  |  |
| 17 | 144 | 1.7 |  | 37 | 132 | 1.56 |  |  |  |  |
| 18 | 162 | 1.92 |  | 38 | 152 | 1.8 |  |  |  |  |
| 19 | 148 | 1.75 |  | 39 | 154 | 1.82 |  |  |  |  |
| 20 | 157 | 1.86 |  | 40 | 159 | 1.88 |  |  |  |  |

### 📊 Frequency Analysis by Period

#### Last 30 Days
| result | count | % | -1 | 1result | 1count | 1% | -2 | 2result | 2count | 2% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 3 | 3.85 |  | 25 | 3 | 3.85 |  | 55 | 1 | 1.28 |
| 2 | 1 | 1.28 |  | 26 | 1 | 1.28 |  |  |  |  |
| 3 | 1 | 1.28 |  | 27 | 4 | 5.13 |  |  |  |  |
| 4 | 3 | 3.85 |  | 28 | 1 | 1.28 |  |  |  |  |
| 5 | 1 | 1.28 |  | 31 | 2 | 2.56 |  |  |  |  |
| 6 | 2 | 2.56 |  | 32 | 1 | 1.28 |  |  |  |  |
| 7 | 5 | 6.41 |  | 34 | 1 | 1.28 |  |  |  |  |
| 9 | 1 | 1.28 |  | 35 | 1 | 1.28 |  |  |  |  |
| 11 | 4 | 5.13 |  | 36 | 2 | 2.56 |  |  |  |  |
| 12 | 1 | 1.28 |  | 37 | 1 | 1.28 |  |  |  |  |
| 13 | 4 | 5.13 |  | 38 | 2 | 2.56 |  |  |  |  |
| 14 | 2 | 2.56 |  | 39 | 1 | 1.28 |  |  |  |  |
| 16 | 1 | 1.28 |  | 41 | 1 | 1.28 |  |  |  |  |
| 17 | 2 | 2.56 |  | 43 | 1 | 1.28 |  |  |  |  |
| 18 | 4 | 5.13 |  | 45 | 1 | 1.28 |  |  |  |  |
| 20 | 1 | 1.28 |  | 46 | 1 | 1.28 |  |  |  |  |
| 21 | 2 | 2.56 |  | 47 | 2 | 2.56 |  |  |  |  |
| 22 | 1 | 1.28 |  | 48 | 1 | 1.28 |  |  |  |  |
| 23 | 2 | 2.56 |  | 52 | 3 | 3.85 |  |  |  |  |
| 24 | 4 | 5.13 |  | 54 | 2 | 2.56 |  |  |  |  |

#### Last 60 Days
| result | count | % | -1 | 1result | 1count | 1% | -2 | 2result | 2count | 2% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 5 | 3.21 |  | 21 | 4 | 2.56 |  | 41 | 3 | 1.92 |
| 2 | 3 | 1.92 |  | 22 | 1 | 0.64 |  | 42 | 1 | 0.64 |
| 3 | 3 | 1.92 |  | 23 | 3 | 1.92 |  | 43 | 1 | 0.64 |
| 4 | 3 | 1.92 |  | 24 | 5 | 3.21 |  | 44 | 2 | 1.28 |
| 5 | 5 | 3.21 |  | 25 | 6 | 3.85 |  | 45 | 3 | 1.92 |
| 6 | 2 | 1.28 |  | 26 | 2 | 1.28 |  | 46 | 3 | 1.92 |
| 7 | 6 | 3.85 |  | 27 | 6 | 3.85 |  | 47 | 4 | 2.56 |
| 8 | 3 | 1.92 |  | 28 | 2 | 1.28 |  | 48 | 2 | 1.28 |
| 9 | 5 | 3.21 |  | 29 | 3 | 1.92 |  | 49 | 1 | 0.64 |
| 10 | 1 | 0.64 |  | 30 | 1 | 0.64 |  | 50 | 1 | 0.64 |
| 11 | 7 | 4.49 |  | 31 | 4 | 2.56 |  | 51 | 2 | 1.28 |
| 12 | 1 | 0.64 |  | 32 | 2 | 1.28 |  | 52 | 3 | 1.92 |
| 13 | 5 | 3.21 |  | 33 | 1 | 0.64 |  | 53 | 1 | 0.64 |
| 14 | 3 | 1.92 |  | 34 | 2 | 1.28 |  | 54 | 3 | 1.92 |
| 15 | 2 | 1.28 |  | 35 | 1 | 0.64 |  | 55 | 2 | 1.28 |
| 16 | 3 | 1.92 |  | 36 | 3 | 1.92 |  |  |  |  |
| 17 | 3 | 1.92 |  | 37 | 1 | 0.64 |  |  |  |  |
| 18 | 7 | 4.49 |  | 38 | 4 | 2.56 |  |  |  |  |
| 19 | 1 | 0.64 |  | 39 | 2 | 1.28 |  |  |  |  |
| 20 | 2 | 1.28 |  | 40 | 1 | 0.64 |  |  |  |  |

#### Last 90 Days
| result | count | % | -1 | 1result | 1count | 1% | -2 | 2result | 2count | 2% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 6 | 2.56 |  | 21 | 4 | 1.71 |  | 41 | 5 | 2.14 |
| 2 | 5 | 2.14 |  | 22 | 4 | 1.71 |  | 42 | 2 | 0.85 |
| 3 | 4 | 1.71 |  | 23 | 5 | 2.14 |  | 43 | 2 | 0.85 |
| 4 | 3 | 1.28 |  | 24 | 8 | 3.42 |  | 44 | 4 | 1.71 |
| 5 | 7 | 2.99 |  | 25 | 6 | 2.56 |  | 45 | 7 | 2.99 |
| 6 | 2 | 0.85 |  | 26 | 2 | 0.85 |  | 46 | 3 | 1.28 |
| 7 | 8 | 3.42 |  | 27 | 8 | 3.42 |  | 47 | 5 | 2.14 |
| 8 | 5 | 2.14 |  | 28 | 3 | 1.28 |  | 48 | 4 | 1.71 |
| 9 | 6 | 2.56 |  | 29 | 4 | 1.71 |  | 49 | 3 | 1.28 |
| 10 | 2 | 0.85 |  | 30 | 2 | 0.85 |  | 50 | 3 | 1.28 |
| 11 | 9 | 3.85 |  | 31 | 4 | 1.71 |  | 51 | 4 | 1.71 |
| 12 | 2 | 0.85 |  | 32 | 3 | 1.28 |  | 52 | 3 | 1.28 |
| 13 | 5 | 2.14 |  | 33 | 4 | 1.71 |  | 53 | 2 | 0.85 |
| 14 | 6 | 2.56 |  | 34 | 2 | 0.85 |  | 54 | 5 | 2.14 |
| 15 | 2 | 0.85 |  | 35 | 3 | 1.28 |  | 55 | 6 | 2.56 |
| 16 | 4 | 1.71 |  | 36 | 3 | 1.28 |  |  |  |  |
| 17 | 3 | 1.28 |  | 37 | 2 | 0.85 |  |  |  |  |
| 18 | 8 | 3.42 |  | 38 | 6 | 2.56 |  |  |  |  |
| 19 | 3 | 1.28 |  | 39 | 5 | 2.14 |  |  |  |  |
| 20 | 4 | 1.71 |  | 40 | 4 | 1.71 |  |  |  |  |

### ⏳ Top 10 số lâu chưa xuất hiện (Top 10 Numbers by Days Since Last Appearance)
| result | last_date | days_since |
| --- | --- | --- |
| 30 | 2026-08-15 | 56 |
| 50 | 2026-08-15 | 56 |
| 19 | 2026-08-22 | 49 |
| 40 | 2026-08-25 | 46 |
| 15 | 2026-08-29 | 42 |
| 10 | 2026-08-29 | 42 |
| 29 | 2026-08-29 | 42 |
| 49 | 2026-09-01 | 39 |
| 44 | 2026-09-01 | 39 |
| 42 | 2026-09-03 | 37 |

### 📆 Số ngày từ lần xuất hiện cuối cùng (Days Since Last Appearance - All Numbers)
| result | last_date | days_since |
| --- | --- | --- |
| 1 | 2026-10-08 | 2 |
| 2 | 2026-09-29 | 11 |
| 3 | 2026-09-22 | 18 |
| 4 | 2026-10-01 | 9 |
| 5 | 2026-10-01 | 9 |
| 6 | 2026-10-06 | 4 |
| 7 | 2026-10-08 | 2 |
| 8 | 2026-09-08 | 32 |
| 9 | 2026-09-22 | 18 |
| 10 | 2026-08-29 | 42 |
| 11 | 2026-10-03 | 7 |
| 12 | 2026-10-08 | 2 |
| 13 | 2026-10-03 | 7 |
| 14 | 2026-10-10 | 0 |
| 15 | 2026-08-29 | 42 |
| 16 | 2026-10-03 | 7 |
| 17 | 2026-10-10 | 0 |
| 18 | 2026-10-06 | 4 |
| 19 | 2026-08-22 | 49 |
| 20 | 2026-10-06 | 4 |
| 21 | 2026-10-10 | 0 |
| 22 | 2026-09-19 | 21 |
| 23 | 2026-10-10 | 0 |
| 24 | 2026-10-10 | 0 |
| 25 | 2026-09-24 | 16 |
| 26 | 2026-09-24 | 16 |
| 27 | 2026-10-08 | 2 |
| 28 | 2026-09-24 | 16 |
| 29 | 2026-08-29 | 42 |
| 30 | 2026-08-15 | 56 |
| 31 | 2026-10-08 | 2 |
| 32 | 2026-09-15 | 25 |
| 33 | 2026-09-05 | 35 |
| 34 | 2026-10-01 | 9 |
| 35 | 2026-09-29 | 11 |
| 36 | 2026-09-29 | 11 |
| 37 | 2026-09-17 | 23 |
| 38 | 2026-09-26 | 14 |
| 39 | 2026-10-10 | 0 |
| 40 | 2026-08-25 | 46 |
| 41 | 2026-09-22 | 18 |
| 42 | 2026-09-03 | 37 |
| 43 | 2026-09-12 | 28 |
| 44 | 2026-09-01 | 39 |
| 45 | 2026-09-17 | 23 |
| 46 | 2026-09-22 | 18 |
| 47 | 2026-09-15 | 25 |
| 48 | 2026-09-26 | 14 |
| 49 | 2026-09-01 | 39 |
| 50 | 2026-08-15 | 56 |
| 51 | 2026-09-10 | 30 |
| 52 | 2026-10-08 | 2 |
| 53 | 2026-09-10 | 30 |
| 54 | 2026-10-03 | 7 |
| 55 | 2026-10-01 | 9 |



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

