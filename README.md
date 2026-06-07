# 🚀 Sanofi R&D Capacity Management & Corporate Finance Dashboard

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Click%20Here-success?style=for-the-badge&logo=render)](https://sanofi-opcm-dashboard.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](#)
[![Dash](https://img.shields.io/badge/Dash-008DE4?style=for-the-badge&logo=plotly&logoColor=white)](#)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)](#)

Welcome to the **Sanofi OPCM Dashboard**! This enterprise-grade analytics application was engineered by **Namuuna** as a portfolio project for the *Data Analyses and Application Development Trainee* role at Sanofi Budapest.

It is designed to bridge the gap between operational resource management (FTEs) and corporate finance strategy (DCF, NPV, WACC), transforming raw clinical trial data into dynamic, multi-dimensional business intelligence.

---

## 🌟 Key Features

### 1. 📈 Dynamic Corporate Finance Engine
- **Live DCF Modeling:** Instantly calculates the Discounted Cash Flow (DCF) and Net Present Value (NPV) liabilities of up to 5,000 active R&D projects.
- **Sensitivity Analysis:** Features an interactive macro-assumptions control panel. Adjust the Blended Annual FTE Cost ($80k - $300k), Corporate WACC (2% - 15%), or Inflation/Escalation factors, and watch the entire enterprise valuation recalculate in real-time.

### 2. 🌌 Multi-Dimensional 4D Visualizations
- Switch seamlessly between clean **2D Classic Box Plots**, structural **3D Spatial Scatters**, and cinematic **4D Animated Time-Series** models.
- The 4D visualization maps Clinical Stage against Allocated FTEs, sizes the bubbles by Base Budget, and animates the financial progression across all four quarters of 2026.

### 3. 📂 Enterprise Data Management Architecture
- **Bring Your Own Data:** The dashboard runs on a highly reactive `dcc.Store` architecture. Use the drag-and-drop uploader to inject your own custom Sanofi Excel/CSV datasets.
- **Synthetic Generator:** Don't have data? Instantly generate thousands of randomized, logically-sound clinical trial projects with a single click.

### 4. 🤖 AI Virtual Advisor Chatbot
- Includes a built-in virtual assistant. Click the "Help & Documentation" button to open an interactive chat interface. 
- Ask it to define complex financial terms like *WACC*, *FTE*, or *NPV*, or ask it for instructions on how to navigate the dashboard.

---

## 🛠️ Technology Stack
- **Backend:** Python, Flask, Gunicorn
- **Frontend & Routing:** Plotly Dash, Dash Bootstrap Components (DBC)
- **Data Engineering & Math Engine:** Pandas, NumPy
- **Visualizations:** Plotly Graph Objects, Plotly Express
- **Deployment:** Render Platform

---

## 🚀 Running Locally

If you prefer to run the application locally instead of using the [Live Demo](https://sanofi-opcm-dashboard.onrender.com/):

```bash
# 1. Clone the repository
git clone https://github.com/namuundelger-nar/sanofi-opcm-dashboard.git

# 2. Navigate into the directory
cd sanofi-opcm-dashboard

# 3. Install the dependencies
pip install -r requirements.txt

# 4. Launch the application
python app.py
```
*The dashboard will be available in your browser at `http://127.0.0.1:8050/`.*

---
*Developed with ❤️ for Sanofi.*
