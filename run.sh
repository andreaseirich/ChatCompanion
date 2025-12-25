#!/bin/bash
# Simple script to run ChatCompanion

# Check if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run Streamlit app
streamlit run app/main.py

