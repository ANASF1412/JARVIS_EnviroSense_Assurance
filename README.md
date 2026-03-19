<div align="center">
  
# 🛡️ GigShield AI
### Parametric Income Protection for Delivery Workers

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Hugging Face](https://img.shields.io/badge/Hugging_Face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/)
[![Machine Learning](https://img.shields.io/badge/Machine_Learning-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![DEVTrails Phase 1](https://img.shields.io/badge/DEVTrails_2026-Phase_1_Winner-blueviolet?style=for-the-badge)](#)

*An AI-powered parametric insurance platform defending gig economy workers from income loss caused by sudden environmental & civic disruptions.*

</div>

---

## 🌍 The Problem Statement

Delivery workers serve as the backbone of the urban gig economy, yet they are extremely vulnerable to outdoor conditions. When extreme weather or civic disruptions hit, deliveries halt, resulting in sudden and severe income loss.

**Common livelihood-halting disruptions include:**
- ⛈️ **Heavy Rainfall & Monsoons**
- 🌡️ **Extreme Heatwaves**
- 🌊 **Flash Flooding**
- 🏭 **Severe Air Pollution (AQI Spikes)**
- 🚧 **Government Curfews & Lockdowns**

Traditional insurance is broken for the gig economy. It requires **manual claim filing, tedious verification, and agonizingly long processing times**. Gig workers cannot wait weeks for a payout when their daily wage is lost.

---

## 💡 Solution Overview

**GigShield AI** is a fully automated, transparent, and instant insurance layer. It automatically:
1. **Predicts** disruption risks hyper-locally using state-of-the-art Time-Series AI models.
2. **Detects** real-time environmental disruption events via Parametric triggers.
3. **Calculates** precise lost delivery income based on historical earnings.
4. **Verifies** claim authenticity using an advanced Behavioral Anti-Spoofing Engine.
5. **Triggers** instant smart payouts directly to the worker's wallet.

***Zero paperwork. Zero delay. Absolute financial resilience.***

---

## 🎯 Target Persona

Designed primarily for **Food & Grocery Delivery Partners** operating on platforms such as:
- 🚴 **Zomato**
- 🍔 **Swiggy**
- 📦 **Blinkit / Zepto / Dunzo**

**Why this demographic?**
- **100% Outdoor Dependent**: Their workplace is the literal street.
- **High Delivery Frequency**: Earnings are mapped directly to hourly activity.
- **Weather Sensitive**: Minor rain can drop order volume; heavy rain stops it completely.
- **Predictable Earning Patterns**: Easy to model baseline income for accurate loss estimation.

---

## ⚡ Real-Life Scenario

Let's look at how GigShield AI protects a worker's livelihood in real-time:

1. A delivery worker normally averages **₹120 per hour**.
2. A sudden, severe monsoon hits their specific delivery zone.
3. **GigShield AI detects:** 70mm of rainfall within 2 hours.
4. **Parametric Trigger activated:** (Condition: `Rainfall > 50mm`).
5. **Disruption Duration recorded:** 5 hours of total downtime.
6. **Income Loss Estimated:** `5 hours × ₹120 = ₹600`.
7. **Anti-Spoofing Check:** Passed ✅ (Verified multi-sensor environmental data).
8. **GigShield AI Automatically Triggers:** Instant Payout of **₹600**.

> *The worker simply receives a notification of the credit—no forms to fill out, no support tickets to raise.*

---

## ⭐ Key Features

- ⛓️ **Parametric Insurance Model**: Event-driven payouts without manual human claims adjusters.
- 🔮 **AI Disruption Prediction**: Time-series forecasting to predict hazard zones before they happen.
- 💸 **Instant Automatic Payouts**: Frictionless money transfer matching the exact hours lost.
- 🗺️ **Hyperlocal Risk Scoring**: Risk evaluated at the micro-zone level, optimizing premium pools.
- 📉 **Delivery Income Loss Estimation**: Dynamic loss calculation tailored to each worker's historical earn rate.
- 📊 **Real-time Monitoring Dashboard**: Streamlit-powered transparency layer for operators and workers.
- 🛡️ **Advanced Fraud Detection**: Next-gen anti-spoofing engine isolating fake claims from genuine distress.

---

## 🧠 Innovation Layer

What makes GigShield AI a paradigm shift?
Instead of operating reactively, GigShield AI operates **predictively and automatically**. 
- **It eliminates the "Claim" mechanic**: The environment *is* the claim. By relying on deterministic external data (Weather APIs, AQI indices), we remove the friction of proof.
- **Dynamic Micro-Premiums**: High-risk zones adjust dynamically, ensuring the liquidity pool remains solvent.
- **NLP Zero-Shot Event Detection**: Reading live government APIs and news feeds via Hugging Face Transformers to trigger Civic Disruption (Curfew) payouts without human intervention.

---

# 🚨 Adversarial Defense & Anti-Spoofing Strategy
*Response to the DEVTrails Phase 1 "Market Crash" Syndicate Threat*

The recent attack by a 500-user syndicate utilizing advanced GPS-spoofing to drain a beta liquidity pool proved one thing: **Simple GPS verification is officially dead.** 

GigShield AI's architecture has pivoted to a **"Behavioral-Proof-of-Presence"** model. Here is our airtight strategy to protect the liquidity pool without harming honest workers.

### 1. 🔍 The Differentiation: Genuine vs. Synthetic

How does GigShield AI differentiate a genuinely stranded delivery partner from a bad actor resting at home while spoofing their location?

- **Behavioral Consistency Modeling**: A genuinely stranded worker Exhibits a "Thermal/Kinetic Signature." Even when parked under an overpass to hide from the rain, there are micro-movements (shifting the bike, checking the phone, pacing). A spoofed GPS feed often projects a "Perfect Path" or "Absolute Dead Zero" movement that physically contradicts human nature.
- **Environmental Consistency Check**: We map internal device telemetry against external localized data. If you claim to be in a flood, your device should reflect the localized atmospheric pressure of a storm front, not the climate-controlled equilibrium of a 5th-floor apartment.

### 2. 📡 Data Signals Used (Non-GPS Vectors)

To detect a coordinated fraud ring, we analyze a rich **"Digital Environment Fingerprint"**:

| Data Signal | Why it Catches Fraudsters |
| :--- | :--- |
| **Accelerometer / Gyroscope** | Detects "Synthetic Stillness." Spoofers can fake coordinates, but faking realistic 3D human micro-movements on physical IMU sensors in real-time is computationally complex and unscalable for syndicates. |
| **BSSID / Wi-Fi Triangulation** | Maps nearby MAC addresses of Wi-Fi routers. A worker spoofing their location to an active flood zone won't be able to "hear" the localized routers of that zone. |
| **Network Latency (RTT)** | GPS spoofers often combine tools with VPNs to mask IPs. We measure Round-Trip-Time to local edge servers. If a worker is "in the rain" 2 miles away, a 300ms latency spike implies they are routing through a proxy. |
| **Atmospheric Pressure (Barometer)** | Modern phones track barometric pressure. Severe rain/cyclones cause massive, localized pressure drops. The device's sensor must match the Weather API's delta. |
| **Crowd Anomaly Detection** | If 500 devices suddenly converge on a hyper-specific 200-meter radius claiming disruption, while historical delivery heatmaps show that area only supports 30 active workers, it triggers a Syndicate Alert. |

### 3. 🧠 AI Fraud Detection Architecture

- **Isolation Forest (Anomaly Detection)**: Evaluates claims in high-dimensional space. An array of `[Location Consistency, IMU Variance, Historical Earnings, BSSID Match]` is checked. Anomalies are isolated immediately.
- **Graph-Based Syndicate Detection**: Maps connections between flagged nodes. Do 50 flagged workers share the same IP subnet or bank account routing prefix? The graph catches coordinated rings.
- **Multi-Signal Fraud Risk Score**: 
  *Fraud Score = f(IMU Authenticity) + f(Network Latency) + f(Colocation Variance) + f(Historical Reliability)*
  Any score > 85 triggers active defense protocols.

### 4. ⚖️ UX Balance

We must never penalize an honest worker experiencing a genuine 4G dropout during a monsoon.
- **Soft Flagging vs. Hard Rejection**: Questionable claims are placed in "Pending Verification" rather than denied.
- **"Proof of Environment" (PoE)**: If flagged, the worker is prompted on the app: *"Due to network issues, please record a quick 5-second video of your surroundings or press this button (which flashes the screen to check ambient light sensors)."* Honest workers pass in 10 seconds. Automated spoofers cannot comply.
- **Confidence-Based Payout Tiers**: 100% confidence = Instant Payout. 70% confidence = 20% instant payout to secure them, the remaining 80% clears upon overnight automated verification.
- **Transparent Communication**: Notifications explicitly state: *"Your payout is under verification due to unusual network signals in your zone. It will be cleared shortly."*

### 5. 🛡️ System Resilience

How GigShield handles mass coordinated attacks:
- **Rate Limiting & Liquidity Throttling**: The smart contract locks the liquidity pool if it detects >200% standard deviation in payout volume within a 10-minute window for a specific micro-zone.
- **Cluster Anomaly Detection**: Rapid clustering flags instances where dozens of devices share identical "fake" trajectories generated by the same Telegram-circulated spoofing script.

### 6. 🧪 Example Fraud Scenario
- **The Attack**: 500 workers coordinate on Telegram, launch GPS-spoofers pointing to a "Red Alert Flood Zone," and await ₹500,000 in mass payouts.
- **The Defense**: 
  1. GigShield detects 500 devices arriving in the zone at exactly 30km/h with `0.00` variance. 
  2. BSSID scans return home Wi-Fi names instead of flooded zone routers.
  3. Graph AI flags a massive cluster anomaly.
  4. **Action**: Liquidity pool is throttled. Payouts are blocked. Accounts flagged for "PoE" verification. Fraud ring neutralized instantly without human intervention.

---

## 🏗 System Architecture

```text
            Worker App / Dashboard (Telemetry, IMU, GPS)
                    │
                    │ Encrypted API Requests & Signal Streams
                    │
            Backend Server (FastAPI)
                    │
    ┌───────────────┼───────────────────────────────┐
    │               │                               │
AI Risk Engine   Parametric Engine           Adversarial Defense
    │               │                        (Anti-Spoofing AI)
    └───────────────┬───────────────────────────────┘
                    │
            Data Processing Layer
  Weather API | Pollution API | Govt Alerts | Delivery Logs
                    │
                    ▼
               Database
               (SQLite)
                    │
                    ▼
            Payout Engine
         Mock UPI / Razorpay Gateway
```

---

## 🔄 End-to-End Workflow

1. **Telemetry & Environment Ingestion**: Constant streaming of weather, pollution, and encrypted worker telemetry.
2. **AI Risk Profiling**: Model predicts disruption likelihood for upcoming shifts.
3. **Trigger Detection**: Parametric conditions (e.g., Rainfall > 50mm) are met in a micro-zone.
4. **Income Loss Calculation**: Engine computes `Downtime × Historical Hourly Rate`.
5. **Adversarial Check (Critical)**: Fraud Risk Score evaluated using IMU, Network, and Cluster data.
6. **Smart Execution**: If Fraud Score is low -> **Automatic Instant Payout** generated.
7. **Worker Notification**: Worker dashboard updates with payout confirmation.

---

## 🤖 AI/ML Architecture

GigShield employs a multi-model approach:
- **Disruption Prediction**: Time-series analysis of meteorological data.
- **Parametric Detection**: Algorithmic rules engine crossing live API thresholds.
- **Income Estimation**: Baseline generation using historical earnings regression.
- **Hyperlocal Scoring**: Geo-spatial risk mapping allocating risk values to micro-zones.
- **Fraud Detection**: Unsupervised Learning (Isolation Forest) filtering structural anomalies in claim meta-data.

---

## 📊 Hugging Face Integration

We heavily utilized the **Hugging Face Ecosystem** to power our text and time-series AI:

### Models Used
- `distilbert-base-uncased`: General text classification, utilized to read and categorize incoming news/weather alerts.
- `facebook/bart-large-mnli`: **Zero-shot classification** to instantly categorize municipal announcements into disruption types (`rain`, `flood`, `pollution`, `curfew`).
- `huggingface/time-series-transformer`: Time-series forecasting for predicting localized weather disruption probabilities 24 hours in advance.

### Datasets Used
- **`load_dataset()` pipeline**: Imported various climate, weather, and environmental event datasets to pre-train our anomaly and risk detection algorithms, simulating thousands of hours of varied disruption events.

---

## 💻 Tech Stack

| Category | Technology |
| :--- | :--- |
| **Frontend/Dashboard** | Streamlit |
| **Backend/API Core** | FastAPI Python |
| **Machine Learning** | Scikit-learn, Hugging Face Transformers |
| **Data Management** | Hugging Face Datasets, Pandas |
| **Database** | SQLite |
| **Visualization** | Plotly |
| **External APIs** | OpenWeather API, Live AQI API, Mock UPI |

---

## 📁 Project Structure

```text
gigshield-ai/
├── app.py                # Fast API Backend Entry Point
├── data_loader.py        # Hugging Face Dataset Ingestion & Preprocessing
├── risk_model.py         # Time-series Risk Prediction Logic
├── trigger_engine.py     # Parametric Event Engine
├── income_estimator.py   # Baseline Earnings Loss Calculator
├── fraud_detector.py     # Isolation Forest & Anti-Spoofing AI
├── payout_engine.py      # Mock UPI / Financial Gateway
├── dashboard.py          # Streamlit Real-Time Visuals
├── requirements.txt      # Python Dependencies
└── README.md             # This Document
```

---

## 📊 Dashboard Features

The Streamlit interface acts as the command center, displaying:
- 👤 **Worker Profile & Trust Score**
- 🌦️ **Live Weather & Micro-Zone Conditions**
- 🚨 **Live Disruption Risk Score (0-100)**
- 📈 **Risk Forecast Visualization (Plotly)**
- 🗺️ **Interactive Zone Risk Heatmap**
- 💰 **Calculated Income Loss & Automatic Ledger**
- 💸 **Live Triggered Payout Feed**

---

## 🚀 Installation & Run Instructions

```bash
# 1. Clone the repository
git clone https://github.com/ANASF1412/GigShield-AI.git
cd GigShield-AI

# 2. Install required dependencies
pip install -r requirements.txt

# 3. Launch the Streamlit Dashboard Prototype
streamlit run app.py
```
*Open your browser to `http://localhost:8501` to view the live dashboard.*

---

## 📈 Example Output

```yaml
[SYSTEM_ALERT] ⚠️ Disruption Detected
-------------------------------------
Event Type:         Heavy Rain
Zone ID:            BLR-KORAMANGALA-04
Trigger Condition:  Rainfall 72mm (> 50mm Threshold)
Duration Status:    Active (Target: 4 hours)

[LOSS_ESTIMATION]
Worker ID:          DeliveryPtnr_8921
Baseline Rate:      ₹120/hr
Estimated Loss:     ₹480

[ANTI_SPOOFING]
Status:             CLEARED ✅ (IMU/Location Match 98%)

[PAYOUT_ENGINE]
Action:             TRIGGERED
Amount:             ₹480
Transfer:           SUCCESS (Mock_UPI_TX_99182A)
```

---

## 🔮 Future Improvements

To take GigShield from prototype to production:
- **Real-Time GPS & IMU Integration**: Hooking directly into worker mobile device hardware.
- **Smart Contracts via Blockchain**: Deploying payout logic onto Polygon/Ethereum for 100% transparent algorithmic claim resolution.
- **Dynamic Insurance Marketplace**: Allowing external liquidity providers to underwrite specific micro-zones based on dynamic risk profiling.
- **Multi-City Scaling**: Standardize BSSID & Latency mapping for Pan-India deployment.

---

## 🌍 Impact

GigShield AI fundamentally protects the most vulnerable tier of the modern workforce. By combining **predictive AI, immutable parametric data, and next-gen behavioral fraud defense**, we can provide:
- Absolute **Financial Stability** for gig workers.
- **Frictionless, instant payouts** replacing traditional bureaucratic insurance.
- A **Syndicate-Proof liquidity pool** guaranteeing platform longevity.

*This system proves that structural AI and Parametric modeling can revolutionize social safety nets for the next billion internet users.*

---

<div align="center">
  
**MIT License** • Built for DEVTrails 2026

</div>
