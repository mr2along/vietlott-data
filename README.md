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

Predicitons models are at [/src/predictions](./src/machine_learning/).

For background on these models, see the [Machine Learning README](./src/machine_learning/).

## 📊 Data Statistics

| Product | Total Draws | Start Date | End Date | Total Records | First ID | Latest ID |
| --- | --- | --- | --- | --- | --- | --- |
| Power 655 | 1410 | 2017-08-01 | 2026-10-13 | 1410 | 00001 | 01410 |
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
| 2026-10-13 | 01410 | [2, 14, 27, 40, 50, 53, 26] | 2026-10-14T01:22:56.824473 | baomoi.com |
| 2026-10-10 | 01409 | [14, 17, 21, 23, 24, 39, 30] | 2026-10-11T01:14:18.654267 | baomoi.com |
| 2026-10-08 | 01408 | [1, 7, 12, 27, 31, 52, 6] | 2026-10-09T18:53:51.307533 |  |
| 2026-10-06 | 01407 | [6, 7, 18, 20, 24, 27, 1] | 2026-10-07T19:25:51.351855 |  |
| 2026-10-03 | 01406 | [7, 11, 13, 16, 18, 54, 41] | 2026-10-05T21:20:39.061088 |  |
| 2026-10-01 | 01405 | [4, 5, 13, 34, 52, 55, 15] | 2026-10-02T18:34:26.030763 |  |
| 2026-09-29 | 01404 | [2, 4, 13, 17, 35, 36, 11] | 2026-10-01T02:18:11.319053 |  |
| 2026-09-26 | 01403 | [14, 18, 21, 38, 48, 52, 49] | 2026-10-01T02:18:09.794263 |  |
| 2026-09-24 | 01402 | [1, 13, 23, 25, 26, 28, 27] | 2026-10-01T02:18:08.286342 |  |
| 2026-09-22 | 01401 | [1, 3, 9, 11, 41, 46, 10] | 2026-10-01T02:18:06.812471 |  |

### 🎲 Number Frequency (All Time)
| result | count | % | -1 | 1result | 1count | 1% | -2 | 2result | 2count | 2% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 161 | 1.9 |  | 21 | 153 | 1.81 |  | 41 | 177 | 2.09 |
| 2 | 139 | 1.64 |  | 22 | 179 | 2.12 |  | 42 | 158 | 1.87 |
| 3 | 162 | 1.91 |  | 23 | 164 | 1.94 |  | 43 | 166 | 1.96 |
| 4 | 126 | 1.49 |  | 24 | 161 | 1.9 |  | 44 | 160 | 1.89 |
| 5 | 157 | 1.86 |  | 25 | 144 | 1.7 |  | 45 | 148 | 1.75 |
| 6 | 133 | 1.57 |  | 26 | 148 | 1.75 |  | 46 | 155 | 1.83 |
| 7 | 141 | 1.67 |  | 27 | 145 | 1.71 |  | 47 | 161 | 1.9 |
| 8 | 170 | 2.01 |  | 28 | 129 | 1.52 |  | 48 | 162 | 1.91 |
| 9 | 163 | 1.93 |  | 29 | 170 | 2.01 |  | 49 | 151 | 1.78 |
| 10 | 144 | 1.7 |  | 30 | 145 | 1.71 |  | 50 | 143 | 1.69 |
| 11 | 166 | 1.96 |  | 31 | 154 | 1.82 |  | 51 | 172 | 2.03 |
| 12 | 157 | 1.86 |  | 32 | 169 | 2.0 |  | 52 | 152 | 1.8 |
| 13 | 156 | 1.84 |  | 33 | 161 | 1.9 |  | 53 | 164 | 1.94 |
| 14 | 148 | 1.75 |  | 34 | 170 | 2.01 |  | 54 | 143 | 1.69 |
| 15 | 134 | 1.58 |  | 35 | 141 | 1.67 |  | 55 | 157 | 1.86 |
| 16 | 149 | 1.76 |  | 36 | 143 | 1.69 |  |  |  |  |
| 17 | 144 | 1.7 |  | 37 | 132 | 1.56 |  |  |  |  |
| 18 | 162 | 1.91 |  | 38 | 152 | 1.8 |  |  |  |  |
| 19 | 148 | 1.75 |  | 39 | 154 | 1.82 |  |  |  |  |
| 20 | 157 | 1.86 |  | 40 | 160 | 1.89 |  |  |  |  |

### 📊 Frequency Analysis by Period

#### Last 30 Days
| result | count | % | -1 | 1result | 1count | 1% | -2 | 2result | 2count | 2% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 3 | 3.85 |  | 25 | 3 | 3.85 |  | 53 | 1 | 1.28 |
| 2 | 2 | 2.56 |  | 26 | 1 | 1.28 |  | 54 | 1 | 1.28 |
| 3 | 1 | 1.28 |  | 27 | 5 | 6.41 |  | 55 | 1 | 1.28 |
| 4 | 3 | 3.85 |  | 28 | 1 | 1.28 |  |  |  |  |
| 5 | 1 | 1.28 |  | 31 | 1 | 1.28 |  |  |  |  |
| 6 | 2 | 2.56 |  | 32 | 1 | 1.28 |  |  |  |  |
| 7 | 4 | 5.13 |  | 34 | 1 | 1.28 |  |  |  |  |
| 9 | 1 | 1.28 |  | 35 | 1 | 1.28 |  |  |  |  |
| 11 | 4 | 5.13 |  | 36 | 2 | 2.56 |  |  |  |  |
| 12 | 1 | 1.28 |  | 37 | 1 | 1.28 |  |  |  |  |
| 13 | 4 | 5.13 |  | 38 | 2 | 2.56 |  |  |  |  |
| 14 | 3 | 3.85 |  | 39 | 1 | 1.28 |  |  |  |  |
| 16 | 1 | 1.28 |  | 40 | 1 | 1.28 |  |  |  |  |
| 17 | 2 | 2.56 |  | 41 | 1 | 1.28 |  |  |  |  |
| 18 | 4 | 5.13 |  | 45 | 1 | 1.28 |  |  |  |  |
| 20 | 1 | 1.28 |  | 46 | 1 | 1.28 |  |  |  |  |
| 21 | 2 | 2.56 |  | 47 | 1 | 1.28 |  |  |  |  |
| 22 | 1 | 1.28 |  | 48 | 1 | 1.28 |  |  |  |  |
| 23 | 2 | 2.56 |  | 50 | 1 | 1.28 |  |  |  |  |
| 24 | 3 | 3.85 |  | 52 | 3 | 3.85 |  |  |  |  |

#### Last 60 Days
| result | count | % | -1 | 1result | 1count | 1% | -2 | 2result | 2count | 2% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 5 | 3.33 |  | 21 | 4 | 2.67 |  | 42 | 1 | 0.67 |
| 2 | 4 | 2.67 |  | 22 | 1 | 0.67 |  | 43 | 1 | 0.67 |
| 3 | 3 | 2.0 |  | 23 | 3 | 2.0 |  | 44 | 2 | 1.33 |
| 4 | 3 | 2.0 |  | 24 | 5 | 3.33 |  | 45 | 2 | 1.33 |
| 5 | 4 | 2.67 |  | 25 | 5 | 3.33 |  | 46 | 2 | 1.33 |
| 6 | 2 | 1.33 |  | 26 | 2 | 1.33 |  | 47 | 4 | 2.67 |
| 7 | 6 | 4.0 |  | 27 | 5 | 3.33 |  | 48 | 2 | 1.33 |
| 8 | 3 | 2.0 |  | 28 | 2 | 1.33 |  | 49 | 1 | 0.67 |
| 9 | 4 | 2.67 |  | 29 | 2 | 1.33 |  | 50 | 1 | 0.67 |
| 10 | 1 | 0.67 |  | 31 | 4 | 2.67 |  | 51 | 2 | 1.33 |
| 11 | 7 | 4.67 |  | 32 | 2 | 1.33 |  | 52 | 3 | 2.0 |
| 12 | 1 | 0.67 |  | 33 | 1 | 0.67 |  | 53 | 2 | 1.33 |
| 13 | 5 | 3.33 |  | 34 | 2 | 1.33 |  | 54 | 3 | 2.0 |
| 14 | 4 | 2.67 |  | 35 | 1 | 0.67 |  | 55 | 2 | 1.33 |
| 15 | 2 | 1.33 |  | 36 | 3 | 2.0 |  |  |  |  |
| 16 | 2 | 1.33 |  | 37 | 1 | 0.67 |  |  |  |  |
| 17 | 3 | 2.0 |  | 38 | 4 | 2.67 |  |  |  |  |
| 18 | 7 | 4.67 |  | 39 | 2 | 1.33 |  |  |  |  |
| 19 | 1 | 0.67 |  | 40 | 2 | 1.33 |  |  |  |  |
| 20 | 1 | 0.67 |  | 41 | 3 | 2.0 |  |  |  |  |

#### Last 90 Days
| result | count | % | -1 | 1result | 1count | 1% | -2 | 2result | 2count | 2% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 6 | 2.63 |  | 21 | 4 | 1.75 |  | 41 | 5 | 2.19 |
| 2 | 6 | 2.63 |  | 22 | 4 | 1.75 |  | 42 | 2 | 0.88 |
| 3 | 4 | 1.75 |  | 23 | 5 | 2.19 |  | 43 | 2 | 0.88 |
| 4 | 3 | 1.32 |  | 24 | 7 | 3.07 |  | 44 | 4 | 1.75 |
| 5 | 7 | 3.07 |  | 25 | 6 | 2.63 |  | 45 | 5 | 2.19 |
| 6 | 2 | 0.88 |  | 26 | 2 | 0.88 |  | 46 | 3 | 1.32 |
| 7 | 8 | 3.51 |  | 27 | 9 | 3.95 |  | 47 | 5 | 2.19 |
| 8 | 5 | 2.19 |  | 28 | 3 | 1.32 |  | 48 | 3 | 1.32 |
| 9 | 6 | 2.63 |  | 29 | 4 | 1.75 |  | 49 | 3 | 1.32 |
| 10 | 1 | 0.44 |  | 30 | 1 | 0.44 |  | 50 | 4 | 1.75 |
| 11 | 9 | 3.95 |  | 31 | 4 | 1.75 |  | 51 | 3 | 1.32 |
| 12 | 2 | 0.88 |  | 32 | 3 | 1.32 |  | 52 | 3 | 1.32 |
| 13 | 5 | 2.19 |  | 33 | 3 | 1.32 |  | 53 | 2 | 0.88 |
| 14 | 7 | 3.07 |  | 34 | 2 | 0.88 |  | 54 | 5 | 2.19 |
| 15 | 2 | 0.88 |  | 35 | 2 | 0.88 |  | 55 | 6 | 2.63 |
| 16 | 4 | 1.75 |  | 36 | 3 | 1.32 |  |  |  |  |
| 17 | 3 | 1.32 |  | 37 | 2 | 0.88 |  |  |  |  |
| 18 | 8 | 3.51 |  | 38 | 6 | 2.63 |  |  |  |  |
| 19 | 2 | 0.88 |  | 39 | 5 | 2.19 |  |  |  |  |
| 20 | 3 | 1.32 |  | 40 | 5 | 2.19 |  |  |  |  |

### ⏳ Top 10 số lâu chưa xuất hiện (Top 10 Numbers by Days Since Last Appearance)
| result | last_date | days_since |
| --- | --- | --- |
| 30 | 2026-08-15 | 59 |
| 19 | 2026-08-22 | 52 |
| 15 | 2026-08-29 | 45 |
| 10 | 2026-08-29 | 45 |
| 29 | 2026-08-29 | 45 |
| 49 | 2026-09-01 | 42 |
| 44 | 2026-09-01 | 42 |
| 42 | 2026-09-03 | 40 |
| 33 | 2026-09-05 | 38 |
| 8 | 2026-09-08 | 35 |

### 📆 Số ngày từ lần xuất hiện cuối cùng (Days Since Last Appearance - All Numbers)
| result | last_date | days_since |
| --- | --- | --- |
| 1 | 2026-10-08 | 5 |
| 2 | 2026-10-13 | 0 |
| 3 | 2026-09-22 | 21 |
| 4 | 2026-10-01 | 12 |
| 5 | 2026-10-01 | 12 |
| 6 | 2026-10-06 | 7 |
| 7 | 2026-10-08 | 5 |
| 8 | 2026-09-08 | 35 |
| 9 | 2026-09-22 | 21 |
| 10 | 2026-08-29 | 45 |
| 11 | 2026-10-03 | 10 |
| 12 | 2026-10-08 | 5 |
| 13 | 2026-10-03 | 10 |
| 14 | 2026-10-13 | 0 |
| 15 | 2026-08-29 | 45 |
| 16 | 2026-10-03 | 10 |
| 17 | 2026-10-10 | 3 |
| 18 | 2026-10-06 | 7 |
| 19 | 2026-08-22 | 52 |
| 20 | 2026-10-06 | 7 |
| 21 | 2026-10-10 | 3 |
| 22 | 2026-09-19 | 24 |
| 23 | 2026-10-10 | 3 |
| 24 | 2026-10-10 | 3 |
| 25 | 2026-09-24 | 19 |
| 26 | 2026-09-24 | 19 |
| 27 | 2026-10-13 | 0 |
| 28 | 2026-09-24 | 19 |
| 29 | 2026-08-29 | 45 |
| 30 | 2026-08-15 | 59 |
| 31 | 2026-10-08 | 5 |
| 32 | 2026-09-15 | 28 |
| 33 | 2026-09-05 | 38 |
| 34 | 2026-10-01 | 12 |
| 35 | 2026-09-29 | 14 |
| 36 | 2026-09-29 | 14 |
| 37 | 2026-09-17 | 26 |
| 38 | 2026-09-26 | 17 |
| 39 | 2026-10-10 | 3 |
| 40 | 2026-10-13 | 0 |
| 41 | 2026-09-22 | 21 |
| 42 | 2026-09-03 | 40 |
| 43 | 2026-09-12 | 31 |
| 44 | 2026-09-01 | 42 |
| 45 | 2026-09-17 | 26 |
| 46 | 2026-09-22 | 21 |
| 47 | 2026-09-15 | 28 |
| 48 | 2026-09-26 | 17 |
| 49 | 2026-09-01 | 42 |
| 50 | 2026-10-13 | 0 |
| 51 | 2026-09-10 | 33 |
| 52 | 2026-10-08 | 5 |
| 53 | 2026-10-13 | 0 |
| 54 | 2026-10-03 | 10 |
| 55 | 2026-10-01 | 12 |



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

