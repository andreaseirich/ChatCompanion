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
    
    # Category to icon mapping
    category_icons = {
        "pressure": "⏳",
        "secrecy": "🤫",
        "isolation": "🤫",
        "manipulation": "🎭",
        "guilt_shifting": "🧷",
        "bullying": "🚫",
        "grooming": "⚠️",
    }
    
    # Category to display name mapping
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
    
    # Render badges in a flex container
    badge_html = '<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;">'
    
    for category, category_matches in matches.items():
        if category_matches:
            icon = category_icons.get(category.lower(), "•")
            name = category_names.get(category.lower(), category)
            badge_class = f"behavior-badge {category.lower().replace('_', '_')}"
            
            badge_html += (
                f'<span class="{badge_class}">'
                f'{icon} {name}'
                f'</span>'
            )
    
    badge_html += '</div>'
    
    st.markdown(badge_html, unsafe_allow_html=True)


def render_next_steps(risk_level: RiskLevel) -> None:
    """
    Render recommended next steps section with action buttons.
    
    Args:
        risk_level: Current risk level (GREEN, YELLOW, or RED)
    """
    st.divider()
    st.markdown("### Recommended Next Steps")
    
    col1, col2 = st.columns(2)
    
    with col1:
        show_no_examples = st.button("Show how to say NO", use_container_width=True)
    
    with col2:
        get_help = st.button("Get Professional Help", use_container_width=True)
    
    # "Show how to say NO" expander
    if show_no_examples:
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
    
    # "Get Professional Help" section
    if get_help:
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

