"""UI components for ChatCompanion."""

import streamlit as st

from app.ui.text_presets import TextPresets
from app.utils.constants import RiskLevel


def render_traffic_light(risk_level: RiskLevel) -> None:
    """
    Render traffic light indicator.

    Args:
        risk_level: Risk level (GREEN, YELLOW, or RED)
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        if risk_level == RiskLevel.GREEN:
            st.markdown(
                '<div style="text-align: center; padding: 20px; background-color: #4CAF50; '
                'border-radius: 50%; width: 80px; height: 80px; margin: 0 auto;"></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<p style="text-align: center; font-weight: bold; color: #4CAF50;">GREEN</p>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="text-align: center; padding: 20px; background-color: #cccccc; '
                'border-radius: 50%; width: 80px; height: 80px; margin: 0 auto;"></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<p style="text-align: center; color: #999999;">GREEN</p>',
                unsafe_allow_html=True,
            )

    with col2:
        if risk_level == RiskLevel.YELLOW:
            st.markdown(
                '<div style="text-align: center; padding: 20px; background-color: #FFC107; '
                'border-radius: 50%; width: 80px; height: 80px; margin: 0 auto;"></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<p style="text-align: center; font-weight: bold; color: #FFC107;">YELLOW</p>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="text-align: center; padding: 20px; background-color: #cccccc; '
                'border-radius: 50%; width: 80px; height: 80px; margin: 0 auto;"></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<p style="text-align: center; color: #999999;">YELLOW</p>',
                unsafe_allow_html=True,
            )

    with col3:
        if risk_level == RiskLevel.RED:
            st.markdown(
                '<div style="text-align: center; padding: 20px; background-color: #F44336; '
                'border-radius: 50%; width: 80px; height: 80px; margin: 0 auto;"></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<p style="text-align: center; font-weight: bold; color: #F44336;">RED</p>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="text-align: center; padding: 20px; background-color: #cccccc; '
                'border-radius: 50%; width: 80px; height: 80px; margin: 0 auto;"></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<p style="text-align: center; color: #999999;">RED</p>',
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

