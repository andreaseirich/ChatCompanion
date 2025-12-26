"""Theme system for ChatCompanion UI.

Provides consistent styling, colors, spacing, and kid-friendly design elements.
"""

import streamlit as st


def inject_theme_css():
    """Inject custom CSS theme for kid-friendly, product-like UI."""
    css = """
    <style>
        /* Base typography - kid-friendly fonts */
        * {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 
                         'Helvetica Neue', Arial, sans-serif;
        }
        
        /* Main container - centered, max-width for readability */
        .main .block-container {
            max-width: 1200px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Card styling - rounded corners, subtle shadows */
        .card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 24px;
            margin: 16px 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            border: 1px solid #e0e0e0;
        }
        
        /* Input card styling */
        .input-card {
            background-color: #f8f9fa;
            border-radius: 12px;
            padding: 24px;
            margin: 16px 0;
            border: 1px solid #e0e0e0;
        }
        
        /* Result card styling */
        .result-card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 24px;
            margin: 16px 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            border: 1px solid #e0e0e0;
        }
        
        /* Header styling */
        h1 {
            color: #1a73e8;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        h2 {
            color: #202124;
            font-weight: 500;
            margin-top: 24px;
            margin-bottom: 16px;
        }
        
        h3 {
            color: #5f6368;
            font-weight: 500;
            margin-top: 20px;
            margin-bottom: 12px;
        }
        
        /* Badge styling */
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 0.75rem;
            font-weight: 500;
            background-color: #e8f0fe;
            color: #1a73e8;
            margin-left: 8px;
        }
        
        /* Static badge for header (safe: constant string only) */
        .badge-static {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 0.75rem;
            font-weight: 500;
            background-color: #e8f0fe;
            color: #1a73e8;
            margin-top: 8px;
        }
        
        /* Button spacing */
        .stButton > button {
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        /* Text area styling */
        .stTextArea > div > div > textarea {
            border-radius: 8px;
            border: 1px solid #dadce0;
        }
        
        /* Info boxes - calm, non-threatening */
        .stInfo {
            background-color: #e8f5e9;
            border-left: 4px solid #4caf50;
            border-radius: 4px;
        }
        
        /* Warning boxes - supportive, not scary */
        .stWarning {
            background-color: #fff3e0;
            border-left: 4px solid #ff9800;
            border-radius: 4px;
        }
        
        /* Error boxes - serious but supportive */
        .stError {
            background-color: #ffebee;
            border-left: 4px solid #f44336;
            border-radius: 4px;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            font-weight: 500;
            color: #5f6368;
        }
        
        /* Divider spacing */
        hr {
            margin: 32px 0;
            border: none;
            border-top: 1px solid #e0e0e0;
        }
        
        /* Footer styling */
        .footer {
            text-align: center;
            color: #5f6368;
            font-size: 0.875rem;
            margin-top: 48px;
            padding-top: 24px;
            border-top: 1px solid #e0e0e0;
        }
        
        /* Example button container */
        .example-buttons {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin: 16px 0;
        }
        
        /* Hide Streamlit menu and footer for cleaner look */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Status dots with pulse animation */
        @keyframes pulse {
            0%, 100% {
                transform: scale(1);
                opacity: 1;
            }
            50% {
                transform: scale(1.05);
                opacity: 0.95;
            }
        }
        
        .status-dot {
            display: inline-block;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            margin: 0 auto;
            transition: opacity 0.3s ease;
        }
        
        .status-dot.active {
            animation: pulse 2s ease-in-out infinite;
        }
        
        .status-dot.inactive {
            opacity: 0.2;
        }
        
        .status-dot-container {
            text-align: center;
            padding: 12px;
        }
        
        .status-dot-label {
            margin-top: 8px;
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        /* Modern container styling - flat design */
        .main .block-container {
            border-radius: 15px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        }
        
        .streamlit-expanderContent {
            border-radius: 0 0 15px 15px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            border: none;
        }
        
        .streamlit-expanderHeader {
            border-radius: 15px 15px 0 0;
            border: none;
        }
        
        .stAlert {
            border-radius: 15px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            border: none;
        }
        
        /* Behavior badges */
        .behavior-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 500;
            margin: 4px;
            background-color: #f0f0f0;
            color: #333;
        }
        
        .behavior-badge.pressure {
            background-color: #fff3e0;
            color: #e65100;
        }
        
        .behavior-badge.secrecy {
            background-color: #f3e5f5;
            color: #6a1b9a;
        }
        
        .behavior-badge.manipulation {
            background-color: #e1f5fe;
            color: #01579b;
        }
        
        .behavior-badge.guilt_shifting {
            background-color: #fce4ec;
            color: #880e4f;
        }
        
        .behavior-badge.bullying {
            background-color: #ffebee;
            color: #b71c1c;
        }
        
        .behavior-badge.grooming {
            background-color: #fff8e1;
            color: #f57f17;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)



