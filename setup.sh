#!/bin/bash

# Exit on error
set -e

echo "🔧 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "⚙️ Setting Streamlit environment variables..."
export STREAMlit_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_ENABLE_CORS=false
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

echo "🚀 Launching Asset Advisor Pro..."
streamlit run main.py --server.port=8501 --server.address=0.0.0.0
