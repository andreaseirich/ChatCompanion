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
    render_what_this_tool_can_do,
)
from app.ui.input_handler import load_demo_chats
from app.ui.theme import inject_theme_css, render_badge

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
    # Inject theme CSS
    inject_theme_css()
    
    # ============================================================
    # ZONE 1: Header
    # ============================================================
    st.title("🛡️ ChatCompanion")
    st.markdown(
        "**Privacy-first assistant to help recognize risky chat patterns** "
        + render_badge("Offline / on-device")
    )
    st.markdown(
        "Paste a chat conversation below, and we'll help you understand if there are "
        "any concerning patterns. All processing happens locally on your device - "
        "nothing is uploaded or saved."
    )

    st.divider()

    # Initialize detection engine
    engine = get_detection_engine()
    
    # Load demo chats
    demo_dir = Path(__file__).parent.parent / "demo_data"
    demo_chats = load_demo_chats(demo_dir)
    
    # Load specific example chats for buttons
    chats_dir = demo_dir / "chats"
    example_green = ""
    example_yellow = ""
    example_red = ""
    
    if (chats_dir / "safe_chat.txt").exists():
        with open(chats_dir / "safe_chat.txt", "r", encoding="utf-8") as f:
            example_green = f.read().strip()
    
    if (chats_dir / "manipulation_pressure.txt").exists():
        with open(chats_dir / "manipulation_pressure.txt", "r", encoding="utf-8") as f:
            example_yellow = f.read().strip()
    
    if (chats_dir / "grooming_example.txt").exists():
        with open(chats_dir / "grooming_example.txt", "r", encoding="utf-8") as f:
            example_red = f.read().strip()

    # ============================================================
    # ZONE 2: Input Area
    # ============================================================
    st.header("Chat Input")
    
    # Example buttons
    col1, col2, col3 = st.columns(3)
    example_selected = None
    
    with col1:
        if st.button("🟢 Try GREEN Example", use_container_width=True):
            example_selected = "green"
    
    with col2:
        if st.button("🟡 Try YELLOW Example", use_container_width=True):
            example_selected = "yellow"
    
    with col3:
        if st.button("🔴 Try RED Example", use_container_width=True):
            example_selected = "red"
    
    # Get chat text (from example buttons or manual input)
    chat_text = ""
    
    # Initialize session state for chat input if not exists
    if "chat_input" not in st.session_state:
        st.session_state.chat_input = ""
    
    # Handle example button clicks
    if example_selected == "green" and example_green:
        st.session_state.chat_input = example_green
    elif example_selected == "yellow" and example_yellow:
        st.session_state.chat_input = example_yellow
    elif example_selected == "red" and example_red:
        st.session_state.chat_input = example_red
    
    # Text area for chat input
    chat_text = st.text_area(
        "Paste a chat conversation here:",
        value=st.session_state.chat_input,
        height=200,
        key="chat_input",
        help="You can paste a conversation from any messaging app. "
        "The text is processed locally and never saved.",
    )
    
    # Clear button
    col_clear, col_analyze = st.columns([1, 3])
    with col_clear:
        if st.button("Clear", use_container_width=True):
            st.session_state.chat_input = ""
            st.rerun()
    
    with col_analyze:
        analyze_button = st.button("🔍 Analyze Chat", type="primary", use_container_width=True)

    # Process analysis
    if analyze_button and chat_text.strip():
        with st.spinner("Analyzing conversation..."):
            try:
                result = engine.analyze(chat_text)

                st.divider()

                # ============================================================
                # ZONE 3: Results Area
                # ============================================================
                st.header("Analysis Results")

                # Main result card: Traffic light + Explanation
                with st.container():
                    # Traffic light
                    render_traffic_light(result.risk_level)
                    
                    st.divider()
                    
                    # Explanation (single main explanation box)
                    render_explanation(result.explanation, result.risk_level)
                    
                    # Advice
                    render_advice(result.advice)
                    
                    # Help section (only for RED, rendered once)
                    render_help_section(result.risk_level)
                
                # Details accordion (for observed behaviors, if present)
                if result.matches:
                    with st.expander("📋 Details", expanded=False):
                        st.markdown("**Observed behaviors:**")
                        for category, category_matches in result.matches.items():
                            if category_matches:
                                unique_patterns = len(set(m.pattern.pattern for m in category_matches))
                                total_instances = len(category_matches)
                                st.write(f"  - {category}: {total_instances} instance(s) across {unique_patterns} pattern(s)")

                # Developer Debug Info (clearly separate, collapsed by default)
                with st.expander("🔧 Developer Debug Info", expanded=False):
                    st.write(f"**Risk Level:** {result.risk_level.value}")
                    st.write(f"**Overall Score:** {result.overall_score:.2f}")
                    st.write(f"**ML Available:** {result.ml_available}")
                    st.write("**Category Scores:**")
                    for category, score in result.category_scores.items():
                        st.write(f"  - {category}: {score:.2f}")
                    if result.matches:
                        st.write("**Pattern Matches:**")
                        for category, category_matches in result.matches.items():
                            if category_matches:
                                unique_patterns = len(set(m.pattern.pattern for m in category_matches))
                                total_instances = len(category_matches)
                                st.write(f"  - {category}: {total_instances} instance(s) across {unique_patterns} pattern(s)")

            except Exception as e:
                logger.error(f"Error during analysis: {e}", exc_info=True)
                st.error(
                    "An error occurred while analyzing the chat. Please try again or check the logs."
                )

    elif analyze_button:
        st.warning("Please enter some chat text to analyze.")

    # What this tool can/can't do section
    st.divider()
    render_what_this_tool_can_do()

    # Footer
    st.divider()
    st.markdown(
        '<div class="footer">ChatCompanion - Privacy-first risk detection. '
        "All processing happens locally. No data is saved or uploaded.</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

