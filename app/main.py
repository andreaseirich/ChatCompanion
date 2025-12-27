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

import hashlib
import logging
import time

import streamlit as st

from app.detection.engine import DetectionEngine
from app.ui.components import (
    render_advice,
    render_behavior_badges,
    render_explanation,
    render_help_section,
    render_next_steps,
    render_traffic_light,
    render_what_this_tool_can_do,
)
from app.ui.input_handler import load_demo_chats
from app.ui.theme import inject_theme_css
from app.utils.constants import RiskLevel
from app.utils.dev_mode import is_dev_mode
from app.utils.fun_ui import is_fun_ui_enabled
from app.utils.test_mode import is_test_mode

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
    st.markdown("**Privacy-first assistant to help recognize risky chat patterns**")
    # Static badge - safe: constant string only, no user content
    st.markdown(
        '<span class="badge-static">Offline / on-device</span>',
        unsafe_allow_html=True
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
    
    # Initialize session state for chat input if not exists
    if "chat_input" not in st.session_state:
        st.session_state.chat_input = ""
    
    # Initialize clear flag if not exists
    if "clear_requested" not in st.session_state:
        st.session_state.clear_requested = False
    
    # Handle clear request BEFORE widget creation
    if st.session_state.clear_requested:
        st.session_state.chat_input = ""
        st.session_state.clear_requested = False
    
    # Handle example button clicks - use rerun to avoid widget conflict
    if example_selected == "green" and example_green:
        st.session_state.chat_input = example_green
        st.rerun()
    elif example_selected == "yellow" and example_yellow:
        st.session_state.chat_input = example_yellow
        st.rerun()
    elif example_selected == "red" and example_red:
        st.session_state.chat_input = example_red
        st.rerun()
    
    # Text area for chat input
    # Don't set value parameter - Streamlit will automatically use session_state[key] if it exists
    # This avoids the warning about default value + Session State API conflict
        chat_text = st.text_area(
            "Paste a chat conversation here:",
            height=200,
        key="chat_input",
            help="You can paste a conversation from any messaging app. "
            "The text is processed locally and never saved.",
        )

    # Clear button - set flag instead of modifying session_state directly
    col_clear, col_analyze = st.columns([1, 3])
    with col_clear:
        if st.button("Clear", use_container_width=True):
            st.session_state.clear_requested = True
            # Clear analysis results when clearing chat input
            if "last_result" in st.session_state:
                del st.session_state.last_result
            if "last_chat_text" in st.session_state:
                del st.session_state.last_chat_text
            st.rerun()
    
    with col_analyze:
        analyze_button = st.button("🔍 Analyze Chat", type="primary", use_container_width=True)

    # Process analysis
    if analyze_button and chat_text.strip():
        with st.spinner("Scanning for risky patterns..."):
            try:
                # Add processing delay (bypassed in test mode)
                if not is_test_mode():
                    time.sleep(1.5)
                
                result = engine.analyze(chat_text)

                # Store result in session state (convert to dict for serialization)
                st.session_state.last_result = {
                    "risk_level": result.risk_level.value,
                    "overall_score": result.overall_score,
                    "category_scores": result.category_scores,
                    "explanation": result.explanation,
                    "advice": result.advice,
                    "matches": result.matches,  # This contains PatternMatch objects - may need special handling
                    "ml_available": result.ml_available,
                }
                st.session_state.last_chat_text = chat_text
                
                # Generate unique result ID to prevent duplicate balloons
                result_id = hashlib.md5((chat_text + str(result.risk_level.value)).encode()).hexdigest()
                balloons_key = f"balloons_shown_{result_id}"
                
                # Show balloons for GREEN results (once per unique result) if fun UI is enabled
                if result.risk_level == RiskLevel.GREEN and is_fun_ui_enabled():
                    if balloons_key not in st.session_state:
                        st.balloons()
                        st.session_state[balloons_key] = True

            except Exception as e:
                logger.error(f"Error during analysis: {e}", exc_info=True)
                st.error(
                    "An error occurred while analyzing the chat. Please try again or check the logs."
                )
                # Clear result on error
                if "last_result" in st.session_state:
                    del st.session_state.last_result
                if "last_chat_text" in st.session_state:
                    del st.session_state.last_chat_text

    elif analyze_button:
        st.warning("Please enter some chat text to analyze.")
    
    # Display results if available (either from new analysis or from session state)
    if "last_result" in st.session_state and st.session_state.last_result:
        result_dict = st.session_state.last_result
        # Reconstruct RiskLevel enum
        risk_level = RiskLevel(result_dict["risk_level"])
        
        st.divider()

        # ============================================================
        # ZONE 3: Results Area
        # ============================================================
        st.header("Analysis Results")

        # Main result card: Traffic light + Explanation
        with st.container():
            # Traffic light
            render_traffic_light(risk_level)
            
            st.divider()
            
            # Explanation (single main explanation box)
            render_explanation(result_dict["explanation"], risk_level)
            
            # Advice
            render_advice(result_dict["advice"])
            
            # Help section (only for RED, rendered once)
            render_help_section(risk_level)
        
        # Observed behaviors as badges
        if result_dict["matches"]:
            render_behavior_badges(result_dict["matches"])
        
        # Recommended Next Steps
        render_next_steps(risk_level)
        
        # Details accordion (for pattern counts, if present)
        if result_dict["matches"]:
            with st.expander("📋 Details", expanded=False):
                st.markdown("**Pattern counts:**")
                col_label, col_count, col_patterns = st.columns([2, 1, 1])
                with col_label:
                    st.markdown("**Category**")
                with col_count:
                    st.markdown("**Instances**")
                with col_patterns:
                    st.markdown("**Patterns**")
                
                for category, category_matches in result_dict["matches"].items():
                    if category_matches:
                        unique_patterns = len(set(m.pattern.pattern for m in category_matches))
                        total_instances = len(category_matches)
                        col_label, col_count, col_patterns = st.columns([2, 1, 1])
                        with col_label:
                            st.write(category)
                        with col_count:
                            st.write(str(total_instances))
                        with col_patterns:
                            st.write(str(unique_patterns))

        # Developer Debug Info (only shown in dev mode)
        if is_dev_mode():
            with st.expander("🔧 Developer Debug Info", expanded=False):
                st.write(f"**Risk Level:** {result_dict['risk_level']}")
                st.write(f"**Overall Score:** {result_dict['overall_score']:.2f}")
                st.write(f"**ML Available:** {result_dict['ml_available']}")
                st.write("**Category Scores:**")
                for category, score in result_dict["category_scores"].items():
                    st.write(f"  - {category}: {score:.2f}")
                if result_dict["matches"]:
                    st.write("**Pattern Matches:**")
                    for category, category_matches in result_dict["matches"].items():
                        if category_matches:
                            unique_patterns = len(set(m.pattern.pattern for m in category_matches))
                            total_instances = len(category_matches)
                            st.write(f"  - {category}: {total_instances} instance(s) across {unique_patterns} pattern(s)")

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

