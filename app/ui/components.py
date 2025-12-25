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


def render_uneasy_button() -> bool:
    """
    Render "This makes me uneasy" button.

    Returns:
        True if button was clicked, False otherwise
    """
    return st.button("🚨 This makes me uneasy", type="primary", use_container_width=True)


def render_uneasy_help_panel() -> None:
    """Render expanded help panel when user clicks uneasy button."""
    st.markdown("### 🛡️ You're Not Alone - Here's What You Can Do")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Talk to Someone You Trust:**
        - A parent, guardian, or family member
        - A teacher or school counselor
        - Another trusted adult in your life
        
        **What to Say:**
        - "This conversation makes me uncomfortable"
        - "I need help understanding if this is okay"
        - "Can we talk about something that's bothering me?"
        """)
    
    with col2:
        st.markdown("""
        **Remember:**
        - Your feelings are valid and important
        - It's okay to set boundaries
        - You don't have to handle this alone
        
        **If You Need Immediate Help:**
        - Reach out to a trusted adult right away
        - You can save or copy this conversation to show them
        """)
    
    st.info(
        "💡 **Tip:** If it's safe to do so, you can copy this conversation and share it with a trusted adult. "
        "They can help you understand what's happening and support you."
    )


def render_help_section() -> None:
    """Render help section with resources."""
    with st.expander("Need Help?"):
        st.markdown(
            """
            **If you're feeling unsafe or uncomfortable:**
            - Talk to a trusted adult: parent, teacher, counselor, or family member
            - Remember: you're not alone, and it's okay to ask for help
            - Trust your feelings - if something feels wrong, it probably is
            
            **Important:** This tool is not a replacement for talking to trusted adults.
            It's here to help you recognize patterns, but always trust your instincts.
            """
        )

