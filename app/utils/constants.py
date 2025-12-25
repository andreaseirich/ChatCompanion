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
# Adjusted to properly flag high-risk conversations:
# - RED requires severe patterns (0.75+) OR multiple strong patterns (secrecy + isolation + pressure combo)
# - YELLOW for mild concerns (0.3-0.75)
# - GREEN for safe conversations (<0.3)
RISK_THRESHOLDS = {
    RiskLevel.GREEN: 0.0,  # 0.0 - 0.3
    RiskLevel.YELLOW: 0.3,  # 0.3 - 0.75
    RiskLevel.RED: 0.75,  # 0.75 - 1.0 (lowered from 0.8 to catch high-risk cases)
}

