"""UI components for ChatCompanion."""

import streamlit as st

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


def render_explanation(explanation: str) -> None:
    """
    Render child-friendly explanation.

    Args:
        explanation: Explanation text
    """
    st.markdown("### What This Means")
    st.info(explanation)


def render_advice(advice: list) -> None:
    """
    Render help advice section.

    Args:
        advice: List of advice messages
    """
    st.markdown("### Remember")
    for item in advice:
        st.markdown(f"• {item}")


def render_help_section() -> None:
    """Render help section with resources (only for high-risk scenarios)."""
    # Only show this section for high-risk situations
    # For low/moderate risk, the main advice section is sufficient
    with st.expander("Need Immediate Help?"):
        st.markdown(
            """
            **If you're feeling unsafe or need immediate support:**
            - Reach out to someone you trust: a parent, teacher, counselor, or another trusted person
            - Contact appropriate support services in your area
            - Trust your instincts - if something feels wrong, it probably is
            
            **Important:** This tool helps recognize patterns but is not a replacement for professional support or trusted guidance.
            """
        )

