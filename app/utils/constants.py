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
RISK_THRESHOLDS = {
    RiskLevel.GREEN: 0.0,  # 0.0 - 0.3
    RiskLevel.YELLOW: 0.3,  # 0.3 - 0.7
    RiskLevel.RED: 0.7,  # 0.7 - 1.0
}

