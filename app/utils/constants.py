"""Constants for risk levels and categories."""

from enum import Enum


class RiskLevel(str, Enum):
    """Traffic light risk levels."""

    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


class RiskCategory(str, Enum):
    """Types of risks to detect."""

    BULLYING = "bullying"
    MANIPULATION = "manipulation"
    PRESSURE = "pressure"
    SECRECY = "secrecy"
    GUILT_SHIFTING = "guilt_shifting"
    GROOMING = "grooming"


# Risk level thresholds
# Adjusted to reduce false high-risk warnings:
# - RED requires clearly severe patterns (0.8+) or multiple moderate patterns
# - YELLOW for mild concerns (0.3-0.8)
# - GREEN for safe conversations (<0.3)
RISK_THRESHOLDS = {
    RiskLevel.GREEN: 0.0,  # 0.0 - 0.3
    RiskLevel.YELLOW: 0.3,  # 0.3 - 0.8
    RiskLevel.RED: 0.8,  # 0.8 - 1.0 (raised from 0.7)
}

