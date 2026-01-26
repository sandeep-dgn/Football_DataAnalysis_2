# Football Match Analysis: Metrica Sports Sample Game 1

This repository contains a data science analysis of professional football (soccer) data, focusing on the integration of event-stream data with high-frequency tracking data.

## 📌 Project Overview
The objective of this project is to extract tactical and physical insights from a professional match. By synchronizing event data (what happened) with tracking data (where everyone was), we can analyze spatial control, player spacing, and the physical demands of the game.

## 📊 Dataset Description
The analysis is performed using the **Metrica Sports Open Dataset**. This is one of the most comprehensive public datasets available for football analytics.



### 1. Tracking Data
* **Source:** `Sample_Game_1_RawTrackingData_Home_Team.csv` & `Away_Team.csv`
* **Frequency:** 25 frames per second (Hz).
* **Details:** X and Y coordinates for all 22 players and the ball.
* **Coordinates:** Normalized between 0 and 1.

### 2. Event Data
* **Source:** `Sample_Game_1_RawEventsData.csv`
* **Details:** Discrete actions including passes, shots, ball recoveries, and set pieces.
* **Linkage:** Events are mapped to specific "Frames" in the tracking data for synchronized analysis.

## 🛠️ Tech Stack & Requirements
* **Language:** Python 3.10+
* **Primary Libraries:** * `pandas` & `numpy` (Data Manipulation)
    * `matplotlib` (Data Visualization)
    * `scipy` (Signal Processing for velocity/acceleration)

## 🏗️ Development Phases
- [ ] **Phase 1:** Data Loading and Coordinate Transformation (Converting 0-1 to Meters).
- [ ] **Phase 2:** Visualizing "Game States" (Plotting player positions during goals).
- [ ] **Phase 3:** Calculating Physical Metrics (Top speed, distance covered, and accelerations).
- [ ] **Phase 4:** Tactical Analysis (Pitch control models and passing networks).

## ⚖️ License & Data Credits
The data used in this project is owned by **Metrica Sports**. 

* **Data Provider:** [Metrica Sports](https://metrica-sports.com/)
* **Repository:** [metrica-sports/sample-data](https://github.com/metrica-sports/sample-data)

> **Disclaimer:** This project is for educational purposes only. All rights to the raw data belong to Metrica Sports.

---

