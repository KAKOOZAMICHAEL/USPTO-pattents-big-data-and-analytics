# USPTO Patent Analytics Pipeline (SQLite Edition) 🚀

A high-performance big data pipeline that processes 200,000+ USPTO patent records, performs ML-based classification, and visualizes insights in a real-time Streamlit dashboard.

## Features
- **Automated ETL**: Downloads, slices, cleans, and loads real USPTO PatentsView data.
- **SQLite Backend**: Ultra-fast performance with zero-config local storage.
- **Advanced Analytics**:
  - Descriptive: Volume trends, technology breakdown, geographic mapping.
  - Diagnostic: Technology concentration (HHI), anomaly detection.
  - Predictive: Linear regression for filing volume and tech trends.
  - Deep Learning: TF-IDF + Logistic Regression for patent abstract classification.
- **Interactive Dashboard**: Dark-themed Streamlit UI with multi-tab analytics.

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Pipeline**:
   This will download the data, build the database, and train the ML models (~4-5 mins).
   ```bash
   python pipeline.py
   ```

3. **Launch the Dashboard**:
   ```bash
   streamlit run dashboard.py
   ```

## Repository Structure
- `pipeline.py`: Main orchestrator.
- `extract_data.py`: Maps and extracts raw TSV columns.
- `analyze_db.py`: Optimized analytical queries and ML logic.
- `dashboard.py`: Streamlit visualization layer.
- `schema.sql`: Database structure definitions.
- `download_and_slice_uspto.py`: Script to fetch real data from PatentsView.

---
Built with ❤️ for Big Data and Intellectual Property Analytics.
