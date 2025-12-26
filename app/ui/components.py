"""UI components for ChatCompanion."""

import streamlit as st

from app.ui.text_presets import TextPresets
from app.utils.constants import RiskLevel


def render_traffic_light(risk_level: RiskLevel) -> None:
    """
    Render status dots with pulse animation for active dot and dimming for inactive dots.

    Args:
        risk_level: Risk level (GREEN, YELLOW, or RED)
    """
    col1, col2, col3 = st.columns(3)

    # GREEN dot
    with col1:
        is_active = risk_level == RiskLevel.GREEN
        dot_class = "status-dot active" if is_active else "status-dot inactive"
        dot_color = "#4CAF50" if is_active else "#cccccc"
        label_color = "#4CAF50" if is_active else "#999999"
        label_weight = "bold" if is_active else "normal"
        
        st.markdown(
            f'<div class="status-dot-container">'
            f'<div class="{dot_class}" style="background-color: {dot_color};"></div>'
            f'<div class="status-dot-label" style="color: {label_color}; font-weight: {label_weight};">GREEN</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # YELLOW dot
    with col2:
        is_active = risk_level == RiskLevel.YELLOW
        dot_class = "status-dot active" if is_active else "status-dot inactive"
        dot_color = "#FFC107" if is_active else "#cccccc"
        label_color = "#FFC107" if is_active else "#999999"
        label_weight = "bold" if is_active else "normal"
        
        st.markdown(
            f'<div class="status-dot-container">'
            f'<div class="{dot_class}" style="background-color: {dot_color};"></div>'
            f'<div class="status-dot-label" style="color: {label_color}; font-weight: {label_weight};">YELLOW</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # RED dot
    with col3:
        is_active = risk_level == RiskLevel.RED
        dot_class = "status-dot active" if is_active else "status-dot inactive"
        dot_color = "#F44336" if is_active else "#cccccc"
        label_color = "#F44336" if is_active else "#999999"
        label_weight = "bold" if is_active else "normal"
        
        st.markdown(
            f'<div class="status-dot-container">'
            f'<div class="{dot_class}" style="background-color: {dot_color};"></div>'
            f'<div class="status-dot-label" style="color: {label_color}; font-weight: {label_weight};">RED</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_explanation(explanation: str, risk_level: RiskLevel) -> None:
    """
    Render child-friendly explanation with preset title and message.
    Ensures exactly ONE main explanation box is rendered.

    Args:
        explanation: Detailed explanation text
        risk_level: Risk level (GREEN, YELLOW, or RED) for preset title/message
    """
    # Get preset title and message for the risk level
    title = TextPresets.get_title(risk_level)
    message = TextPresets.get_message(risk_level)
    
    # Display preset title as main heading
    st.markdown(f"### {title}")
    
    # Display preset message
    st.info(message)
    
    # Display detailed explanation if it differs from the preset message
    # This ensures we have exactly ONE main explanation box
    if explanation and explanation.strip() != message.strip():
        st.markdown("#### Details")
        st.markdown(explanation)


def render_advice(advice: list) -> None:
    """
    Render help advice section.

    Args:
        advice: List of advice messages
    """
    st.markdown("### Remember")
    for item in advice:
        st.markdown(f"• {item}")


def render_help_section(risk_level: RiskLevel) -> None:
    """Render help section with resources (only for high-risk scenarios)."""
    # Only show this section for RED/high-risk situations
    # For YELLOW, use softer phrasing
    # For GREEN, don't show at all
    
    if risk_level == RiskLevel.RED:
        with st.expander("Need Immediate Help?", expanded=False):
            st.markdown(
                """
                **If you're feeling unsafe or need immediate support:**
                - Reach out to someone you trust: a parent, teacher, counselor, or another trusted person
                - Contact appropriate support services in your area
                - Trust your instincts - if something feels wrong, it probably is
                
                **Important:** This tool helps recognize patterns but is not a replacement for professional support or trusted guidance.
                """
            )
    elif risk_level == RiskLevel.YELLOW:
        st.info(
            "If this pattern continues or you feel overwhelmed, consider talking to someone you trust."
        )


def render_behavior_badges(matches: dict) -> None:
    """
    Render observed behaviors as icon badges.
    
    Args:
        matches: Dictionary mapping category to list of PatternMatch objects
    """
    if not matches:
        return
    
    # Category to icon mapping (safe: constant mapping)
    category_icons = {
        "pressure": "⏳",
        "secrecy": "🤫",
        "isolation": "🤫",
        "manipulation": "🎭",
        "guilt_shifting": "🧷",
        "bullying": "🚫",
        "grooming": "⚠️",
    }
    
    # Category to display name mapping (safe: constant mapping)
    category_names = {
        "pressure": "Pressure",
        "secrecy": "Secrecy",
        "isolation": "Isolation",
        "manipulation": "Manipulation",
        "guilt_shifting": "Guilt-shifting",
        "bullying": "Bullying",
        "grooming": "Grooming",
    }
    
    st.markdown("**Observed behaviors:**")
    
    # Render badges using Streamlit columns (safer than HTML)
    # Use native components to avoid unsafe HTML with category names
    badge_cols = st.columns(min(len([c for c in matches.values() if c]), 4))
    col_idx = 0
    
    for category, category_matches in matches.items():
        if category_matches:
            if col_idx >= len(badge_cols):
                break
            icon = category_icons.get(category.lower(), "•")
            name = category_names.get(category.lower(), category)
            
            with badge_cols[col_idx]:
                # Use Streamlit native markdown with emoji (safe)
                st.markdown(f"{icon} **{name}**")
            col_idx += 1


def render_next_steps(risk_level: RiskLevel) -> None:
    """
    Render recommended next steps section with action buttons.
    
    Args:
        risk_level: Current risk level (GREEN, YELLOW, or RED)
    """
    st.divider()
    st.markdown("### Recommended Next Steps")
    
    # Initialize session state for next steps buttons
    if "show_no_examples" not in st.session_state:
        st.session_state.show_no_examples = False
    if "show_professional_help" not in st.session_state:
        st.session_state.show_professional_help = False
    
    # Define callbacks for button clicks
    def on_show_no_click():
        st.session_state.show_no_examples = True
        st.session_state.show_professional_help = False
    
    def on_get_help_click():
        st.session_state.show_professional_help = True
        st.session_state.show_no_examples = False
    
    # For GREEN: show only "Show how to say NO" button, with optional resources link below
    # For YELLOW and RED: show both buttons prominently
    if risk_level == RiskLevel.GREEN:
        # Single button for GREEN
        st.button("Show how to say NO", use_container_width=True, key="btn_show_no", on_click=on_show_no_click)
        
        # Small optional resources expander for GREEN (non-intrusive, collapsed by default)
        with st.expander("Optional resources", expanded=False):
            st.markdown(
                """
                **If you need support or have questions:**
                
                - **klicksafe.de** - Information and support for online safety
                - Talk to someone you trust: a parent, teacher, counselor, or another trusted person
                
                **Remember:** It's always okay to ask for help, even if you're not sure if something is wrong.
                
                **klicksafe.de**: https://www.klicksafe.de
                
                (You can copy this link and open it in your browser)
                """
            )
    else:
        # YELLOW and RED: show both buttons prominently
        col1, col2 = st.columns(2)
        
        with col1:
            # Use on_click callback to set state before rerun
            st.button("Show how to say NO", use_container_width=True, key="btn_show_no", on_click=on_show_no_click)
        
        with col2:
            # Use on_click callback to set state before rerun
            st.button("Get Professional Help", use_container_width=True, key="btn_get_help", on_click=on_get_help_click)
    
    # "Show how to say NO" expander - only render if state is True
    if st.session_state.show_no_examples:
        with st.expander("Ways to say NO", expanded=True):
            st.markdown(
                """
                Here are some simple ways to set boundaries:
                
                - "I'm not comfortable with that."
                - "I need some time to think about it."
                - "That doesn't work for me."
                - "I'd rather not do that."
                - "I'm going to talk to someone I trust about this."
                - "I need to set a boundary here."
                
                **Remember:** It's okay to say no. Real friends respect your boundaries.
                """
            )
    
    # "Get Professional Help" section - only render if state is True
    if st.session_state.show_professional_help:
        with st.expander("Professional Support Resources", expanded=True):
            if risk_level == RiskLevel.RED:
                st.markdown(
                    """
                    **If you're feeling unsafe or need immediate support:**
                    
                    - **klicksafe.de** - Information and support for online safety
                    - Reach out to someone you trust: a parent, teacher, counselor, or another trusted person
                    - Contact appropriate support services in your area
                    
                    **Important:** This tool helps recognize patterns but is not a replacement for professional support or trusted guidance.
                    """
                )
            else:
                st.markdown(
                    """
                    **If you need support or have questions:**
                    
                    - **klicksafe.de** - Information and support for online safety
                    - Talk to someone you trust: a parent, teacher, counselor, or another trusted person
                    
                    **Remember:** It's always okay to ask for help, even if you're not sure if something is wrong.
                    """
                )
            
            # Link to klicksafe (offline-first: show URL, user can copy)
            st.markdown(
                """
                **klicksafe.de**: https://www.klicksafe.de
                
                (You can copy this link and open it in your browser)
                """
            )


def render_what_this_tool_can_do() -> None:
    """Render collapsed section explaining what the tool can and cannot do."""
    with st.expander("What this tool can and cannot do", expanded=False):
        st.markdown(
            """
            **What ChatCompanion can do:**
            - Help you recognize patterns in chat conversations that might be concerning
            - Explain what patterns were detected in simple, easy-to-understand language
            - Give you guidance on setting boundaries and seeking help
            - Work completely offline - your conversations never leave your device
            
            **What ChatCompanion cannot do:**
            - Promise perfect detection - it might miss some risky conversations or flag safe ones incorrectly
            - Replace talking to trusted adults or professional help
            - Make decisions for you - you're always in control
            - Monitor conversations automatically - you choose when to analyze
            
            **Remember:** This tool is here to help you understand patterns and make informed decisions. 
            Always trust your instincts and talk to someone you trust if something feels wrong.
            """
        )

