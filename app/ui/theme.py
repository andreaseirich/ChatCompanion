"""Theme system for ChatCompanion UI.

Provides consistent styling, colors, spacing, and kid-friendly design elements.
"""

import streamlit as st


def inject_theme_css():
    """Inject custom CSS theme for kid-friendly, product-like UI."""
    css = """
    <style>
        /* Brand color system - CSS variables for consistency */
        :root {
            --brand-primary: #1e7ae8;
            --brand-primary-hover: #1557b0;
            --focus-ring: 0 0 0 3px rgba(30, 122, 232, 0.3);
        }
        
        /* Base typography - kid-friendly fonts */
        * {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 
                         'Helvetica Neue', Arial, sans-serif;
        }
        
        /* Main container - centered, max-width for readability */
        .main .block-container {
            max-width: 1000px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Mobile responsiveness */
        @media (max-width: 768px) {
            .main .block-container {
                max-width: 100%;
                padding-left: 1rem;
                padding-right: 1rem;
            }
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
            color: var(--brand-primary);
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
            color: var(--brand-primary);
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
            color: var(--brand-primary);
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
        
        /* Primary button styling - neutral brand color (not red/danger) */
        .stButton > button[kind="primary"],
        .stButton > button[type="primary"] {
            background-color: var(--brand-primary);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .stButton > button[kind="primary"]:hover,
        .stButton > button[type="primary"]:hover {
            background-color: var(--brand-primary-hover);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(30, 122, 232, 0.3);
        }
        
        /* Focus states for accessibility */
        .stButton > button:focus-visible {
            outline: none;
            box-shadow: var(--focus-ring);
        }
        
        .stTextArea > div > div > textarea:focus-visible {
            outline: none;
            box-shadow: var(--focus-ring);
            border-color: var(--brand-primary);
        }
        
        .streamlit-expanderHeader:focus-visible {
            outline: none;
            box-shadow: var(--focus-ring);
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
            padding: 8px 12px;
            margin-top: 8px;
            margin-bottom: 8px;
        }
        
        .status-dot-label {
            margin-top: 8px;
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        /* Compact spacing for Analysis Results section */
        h2 + .status-dot-container {
            margin-top: 8px;
        }
        
        /* Reduce spacing after status dots */
        .status-dot-container + hr {
            margin-top: 16px;
            margin-bottom: 16px;
        }
        
        /* Tighten spacing around result headline */
        .status-dot-container ~ h3:first-of-type {
            margin-top: 12px;
        }
        
        /* Modern container styling - flat design (max-width already set above) */
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
        
        /* Hide anchor icons next to headings (judge-friendly polish)
         * Intent: Hide only the anchor/link icons (🔗) that appear next to headings.
         * Content links (e.g., klicksafe.de) remain visible and clickable.
         * External links (http://, https://) are explicitly preserved.
         */
        a[aria-label="Link to this section"] { 
            display: none !important; 
        }
        a.header-anchor { 
            display: none !important; 
        }
        a.anchor-link { 
            display: none !important; 
        }
        a[class*="anchor"] { 
            display: none !important; 
        }
        a[class*="header"] { 
            display: none !important; 
        }
        .stMarkdown a[href^="#"][aria-label] { 
            display: none !important; 
        }
        .stMarkdown h1 > a,
        .stMarkdown h2 > a,
        .stMarkdown h3 > a,
        .stMarkdown h4 > a,
        .stMarkdown h5 > a,
        .stMarkdown h6 > a {
            display: none !important;
        }
        h1 a, h2 a, h3 a, h4 a, h5 a, h6 a { 
            display: none !important; 
        }
        /* Preserve external links and content links - only hide anchor links */
        .stMarkdown a[href^="http://"],
        .stMarkdown a[href^="https://"] {
            display: inline !important;
        }
        .stMarkdown a:not([href^="#"]) {
            display: inline !important;
        }
        
        /* Next Steps panel styling - clean panel feel */
        /* Style containers that follow dividers and contain buttons/expanders (Next Steps section) */
        /* This targets the container wrapping "Recommended Next Steps" */
        hr + .element-container:has(button),
        hr ~ .element-container:has(button) {
            background-color: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin: 16px 0;
            border: 1px solid #e0e0e0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        }
        
        /* Ensure dividers themselves don't get panel styling */
        hr {
            background: none !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)



