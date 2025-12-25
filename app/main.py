"""Main Streamlit application entry point."""

import sys
from pathlib import Path

# Fix: Add project root to sys.path before imports
# Streamlit adds 'app/main.py' and 'app' to sys.path, but not the project root.
# This ensures 'from app.xxx' imports work correctly.
project_root = Path(__file__).parent.parent
project_root_str = str(project_root.resolve())
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)

import logging

import streamlit as st

from app.detection.engine import DetectionEngine
from app.ui.components import (
    render_advice,
    render_explanation,
    render_help_section,
    render_traffic_light,
)
from app.ui.input_handler import load_demo_chats

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="ChatCompanion",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize detection engine (cached)
@st.cache_resource
def get_detection_engine():
    """Get or create detection engine instance."""
    return DetectionEngine(use_ml=True)


def main():
    """Main application function."""
    # Header
    st.title("🛡️ ChatCompanion")
    st.markdown(
        "**Privacy-first assistant to help recognize risky chat patterns**\n\n"
        "Paste a chat conversation below, and we'll help you understand if there are "
        "any concerning patterns. All processing happens locally on your device - "
        "nothing is uploaded or saved."
    )

    st.divider()

    # Initialize detection engine
    engine = get_detection_engine()

    # Sidebar with demo chats
    with st.sidebar:
        st.header("Demo Chats")
        st.markdown("Try these example conversations to see how ChatCompanion works:")

        demo_dir = Path(__file__).parent.parent / "demo_data"
        demo_chats = load_demo_chats(demo_dir)

        selected_demo = None
        if demo_chats:
            selected_demo = st.selectbox(
                "Select a demo chat:",
                options=["None"] + list(demo_chats.keys()),
            )

    # Main input area
    st.header("Chat Input")

    # Get chat text (from demo or manual input)
    chat_text = ""
    if selected_demo and selected_demo != "None" and selected_demo in demo_chats:
        chat_text = demo_chats[selected_demo]
        st.text_area(
            "Chat conversation:",
            value=chat_text,
            height=200,
            key="chat_input_demo",
        )
    else:
        chat_text = st.text_area(
            "Paste a chat conversation here:",
            height=200,
            key="chat_input_manual",
            help="You can paste a conversation from any messaging app. "
            "The text is processed locally and never saved.",
        )

    # Analyze button
    analyze_button = st.button("🔍 Analyze Chat", type="primary", use_container_width=True)

    # Process analysis
    if analyze_button and chat_text.strip():
        with st.spinner("Analyzing conversation..."):
            try:
                result = engine.analyze(chat_text)

                st.divider()

                # Display results
                st.header("Analysis Results")

                # Traffic light
                render_traffic_light(result.risk_level)

                st.divider()

                # Explanation
                render_explanation(result.explanation)

                # Advice
                render_advice(result.advice)

                # Help section
                render_help_section()

                # Debug info (collapsible)
                with st.expander("Technical Details (for debugging)"):
                    st.write(f"**Risk Level:** {result.risk_level.value}")
                    st.write(f"**Overall Score:** {result.overall_score:.2f}")
                    st.write(f"**ML Available:** {result.ml_available}")
                    st.write("**Category Scores:**")
                    for category, score in result.category_scores.items():
                        st.write(f"  - {category}: {score:.2f}")

            except Exception as e:
                logger.error(f"Error during analysis: {e}", exc_info=True)
                st.error(
                    "An error occurred while analyzing the chat. Please try again or check the logs."
                )

    elif analyze_button:
        st.warning("Please enter some chat text to analyze.")

    # Footer
    st.divider()
    st.markdown(
        "<small>ChatCompanion - Privacy-first risk detection. "
        "All processing happens locally. No data is saved or uploaded.</small>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

