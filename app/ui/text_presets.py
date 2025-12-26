# Copyright 2024 Eirich Andreas
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Child-friendly text presets for risk level explanations.

All text is designed for ages 10-16, using simple English,
avoiding clinical/legal terms, and maintaining a calm and safe tone.
"""

from app.utils.constants import RiskLevel


class TextPresets:
    """Child-friendly text presets for each risk level."""

    # GREEN risk level
    GREEN_TITLE = "Everything looks okay."
    GREEN_MESSAGE = (
        "We didn't see warning signs in this chat. "
        "It's normal for people to be busy or tired."
    )

    # YELLOW risk level
    YELLOW_TITLE = "Something feels a bit off."
    YELLOW_MESSAGE = (
        "We noticed pressure or guilt-making language. "
        "You're allowed to take your time and say no."
    )

    # RED risk level
    RED_TITLE = "This is serious."
    RED_MESSAGE = (
        "Someone may be trying to control or isolate you. "
        "Talk to a trusted person as soon as you can."
    )

    @classmethod
    def get_title(cls, risk_level: RiskLevel) -> str:
        """
        Get title text for a risk level.

        Args:
            risk_level: Risk level (GREEN, YELLOW, or RED)

        Returns:
            Title text for the risk level
        """
        if risk_level == RiskLevel.GREEN:
            return cls.GREEN_TITLE
        elif risk_level == RiskLevel.YELLOW:
            return cls.YELLOW_TITLE
        elif risk_level == RiskLevel.RED:
            return cls.RED_TITLE
        else:
            return cls.GREEN_TITLE  # Default fallback

    @classmethod
    def get_message(cls, risk_level: RiskLevel) -> str:
        """
        Get message text for a risk level.

        Args:
            risk_level: Risk level (GREEN, YELLOW, or RED)

        Returns:
            Message text for the risk level
        """
        if risk_level == RiskLevel.GREEN:
            return cls.GREEN_MESSAGE
        elif risk_level == RiskLevel.YELLOW:
            return cls.YELLOW_MESSAGE
        elif risk_level == RiskLevel.RED:
            return cls.RED_MESSAGE
        else:
            return cls.GREEN_MESSAGE  # Default fallback

