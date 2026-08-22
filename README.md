# HazeCrop Malaysia 🌾

**NASA MODIS Satellite Intelligence for Pre-Season Crop Planning**

HazeCrop uses multi-year NASA MODIS satellite Aerosol Optical Depth (AOD) data to identify recurring haze patterns across Malaysian states and territories. A four-agent AI system interprets the historical patterns and generates a pre-season crop preparedness plan so farmers can prepare **before** an anticipated haze period.

---

## How It Works

```
NASA MODIS MAIAC satellite data (MODIS/061/MCD19A2_GRANULES)
        ↓
Data Analyst Agent    — fetch & validate historical AOD
        ↓
Pattern Analyst Agent — detect seasonal recurring patterns
        ↓
Outlook Agent         — generate seasonal haze outlook + confidence
        ↓
Preparedness Agent    — produce pre-season crop planning guide
        ↓
Interactive Dashboard
```

The system answers three questions immediately:

1. **When is haze historically most likely?**
2. **Why does the system think that?**
3. **What should farmers prepare before that period?**

---

## Features

- 🛰 **NASA MODIS MAIAC AOD** — uses `MODIS/061/MCD19A2_GRANULES`, Optical_Depth_055 band (~0.55 µm)
- 📈 **Multi-year seasonal pattern detection** — analyses 3–10 years of monthly AOD data
- 🧠 **Four-agent AI pipeline** — Data Analyst → Pattern Analyst → Outlook Agent → Preparedness Agent
- 🗓 **Dynamic preparation timeline** — adjusts to the predicted haze window
- 🗺 **Interactive satellite map** — AOD raster + state boundary using geemap
- 📊 **Data transparency** — expandable section with full monthly AOD statistics
- 📥 **CSV and report export** — download monthly data and the full outlook report
- ⚡ **Reactive UI** — expensive satellite queries only run when the user clicks Analyse
- 🔒 **No fake data** — confidence scores are calculated from actual data quality metrics

---

## Important Disclaimer

> **This is a historical seasonal outlook based on recurring satellite-observed aerosol patterns. It is not a guaranteed real-time haze forecast.**

The system identifies historically recurring high-AOD months and seasonal aerosol peaks. It does not predict the exact date, exact location, or exact severity of future haze events.

---

## Architecture

```
hazecrop/
│
├── app.py                        # Streamlit entry point
├── requirements.txt
├── README.md
│
├── config/
│   └── settings.py               # All constants and tuning weights
│
├── services/
│   ├── earth_engine.py           # EE initialisation
│   ├── aod_service.py            # MODIS MAIAC AOD queries
│   └── malaysia_regions.py       # State boundaries & centroids
│
├── analysis/
│   ├── pattern_detection.py      # Monthly stats + seasonal risk scoring
│   ├── seasonal_prediction.py    # Outlook generation + timeline
│   └── confidence.py             # Data-driven confidence calculation
│
├── agents/
│   ├── data_analyst.py           # Agent 1: data fetch & validation
│   ├── pattern_analyst.py        # Agent 2: pattern detection
│   ├── outlook_agent.py          # Agent 3: seasonal outlook
│   └── preparedness_agent.py     # Agent 4: crop preparedness plan
│
├── ui/
│   ├── styles.py                 # Global CSS (dark glassmorphism theme)
│   ├── overview.py               # Overview cards
│   ├── map_view.py               # Satellite map
│   ├── patterns.py               # Historical AOD pattern charts
│   └── ai_insights.py           # AI insights + preparedness plan
│
└── utils/
    ├── formatters.py             # Number and HTML formatters
    └── dates.py                  # Calendar helpers
```

---

## NASA Data Source

| Property | Value |
|---|---|
| Dataset | `MODIS/061/MCD19A2_GRANULES` |
| Full name | MODIS/Terra+Aqua MAIAC Land Aerosol Optical Depth Daily 1km |
| AOD band | `Optical_Depth_055` (~0.55 µm) |
| Scale factor | 0.001 |
| Spatial resolution | 1 km |
| Temporal resolution | Daily |
| Provider | NASA LP DAAC |

---

## Google Earth Engine Setup

### 1. Create a Google Cloud / Earth Engine project

1. Go to [https://earthengine.google.com/](https://earthengine.google.com/)
2. Sign in with a Google account
3. Register a new project at [https://code.earthengine.google.com/register](https://code.earthengine.google.com/register)
4. Note your project ID (e.g. `my-hazecrop-project`)

### 2. Enable the Earth Engine API

In Google Cloud Console, enable the **Google Earth Engine API** for your project.

---

## Installation

### Clone the repository

```bash
git clone https://github.com/your-org/hazecrop-malaysia.git
cd hazecrop-malaysia
```

### Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## Earth Engine Authentication

### First time (interactive)

```bash
earthengine authenticate
```

This opens a browser window and saves credentials locally.

### Verify authentication

```bash
python -c "import ee; ee.Initialize(project='your-project-id'); print('EE ready')"
```

---

## Environment Variables

| Variable | Description | Required |
|---|---|---|
| `EARTHENGINE_PROJECT` | Your GEE project ID | Recommended |

Set it before running the app:

```bash
# Linux / macOS
export EARTHENGINE_PROJECT=your-project-id

# Windows PowerShell
$env:EARTHENGINE_PROJECT = "your-project-id"
```

Alternatively, add it to a `.streamlit/secrets.toml` file:

```toml
earthengine_project = "your-project-id"
```

---

## Running the App

```bash
streamlit run app.py
```

Open your browser at [http://localhost:8501](http://localhost:8501).

---

## Usage

1. **Select a state** from the dropdown (default: Selangor)
2. **Choose a target year** for the seasonal outlook
3. **Adjust the historical data slider** (3–10 years)
4. Click **🚀 Analyse Haze Pattern**
5. Review the seasonal outlook, pattern charts, map, and AI insights
6. Download the CSV data or the full Outlook Report

---

## Seasonal Risk Score

The system computes a 0–100 Seasonal Risk Score for each month using:

| Component | Weight | Description |
|---|---|---|
| Historical mean AOD | 40% | Mean AOD across all historical years |
| High-frequency score | 25% | Fraction of years where month is in top tercile |
| Recent trend | 20% | Positive AOD trend direction |
| Consistency | 15% | Inter-annual stability (lower variance = higher score) |

Scores are classified as:

| Score | Risk Level |
|---|---|
| 0–25 | Low |
| 26–50 | Moderate |
| 51–75 | High |
| 76–100 | Very High |

---

## Confidence Calculation

Pattern confidence is calculated from four data quality indicators:

1. **Year coverage** — number of historical years available
2. **Data completeness** — fraction of months with valid AOD observations
3. **Peak-month consistency** — agreement on peak month across years
4. **Pattern stability** — coefficient of variation in high-risk months

| Confidence | Threshold |
|---|---|
| High | ≥ 65% composite score |
| Medium | 40–64% |
| Low | < 40% |

---

## Limitations

- Analysis is based on historical patterns only — it cannot account for El Niño/La Niña, land-use change, or policy interventions
- MODIS MAIAC AOD data availability varies by location and cloud cover
- Results should be combined with local meteorological advisories and expert agricultural guidance
- Earth Engine query times depend on the size of the historical period and server load

---

## License

MIT License — see `LICENSE` for details.

---

*HazeCrop Malaysia uses NASA MODIS data provided through the Google Earth Engine public data catalogue.*
