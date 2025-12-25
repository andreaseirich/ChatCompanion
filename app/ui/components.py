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


def render_uneasy_button_and_help() -> None:
    """
    Render "This makes me uneasy" button with toggleable help panel.
    
    Uses Streamlit session state to persist the toggle state.
    """
    # Initialize session state for toggle
    if "show_uneasy_help" not in st.session_state:
        st.session_state.show_uneasy_help = False
    
    # Button to toggle help panel
    button_label = "🛡️ Show Additional Help" if not st.session_state.show_uneasy_help else "🛡️ Hide Additional Help"
    
    if st.button(button_label, use_container_width=True):
        st.session_state.show_uneasy_help = not st.session_state.show_uneasy_help
    
    # Show help panel if toggled
    if st.session_state.show_uneasy_help:
        st.markdown("### Additional Support & Resources")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **What You Can Do:**
            - Take a break from the conversation if needed
            - Write down what happened and how it made you feel
            - Talk to someone you trust about the situation
            """)
        
        with col2:
            st.markdown("""
            **Setting Boundaries:**
            - It's okay to say no or ask for time to think
            - You can end conversations that make you uncomfortable
            - Your feelings and safety are important
            """)
        
        st.info(
            "💡 **Note:** If you feel unsafe or need immediate support, reach out to someone you trust "
            "or contact appropriate support services in your area."
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

