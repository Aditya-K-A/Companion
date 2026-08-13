from enum import Enum


class SafetyLevel(str, Enum):
    SAFE = "safe"
    DISTRESS = "distress"
    CRISIS = "crisis"


class SafetyResult:
    def __init__(self, level: SafetyLevel, reason: str = ""):
        self.level = level
        self.reason = reason


class SafetyDetector:

    def __init__(self):

        self.crisis_phrases = [
            "kill myself",
            "killing myself",
            "suicide",
            "suicidal",
            "end my life",
            "ending my life",
            "take my own life",
            "take my life",
            "want to die",
            "don't want to live",
            "do not want to live",
            "better off dead",
            "no reason to live",
            "hurt myself",
            "harm myself",
            "self harm",
            "self-harm",
            "don't want to be alive",
            "do not want to be alive",
            "don't want to live anymore",
            "do not want to live anymore",
            "don't want to live any longer",
            "do not want to live any longer",
            "no point in living",
            "no point to living",
            "no sense in living",
            "no sense to living",
            "life isn't worth living",
            "life is not worth living",
            "life isn't worth it",
            "life is not worth it",
            "wish i were dead",
            "wish i was dead",
            "wish I could die",
            "If I die",
            "I want to die",
            "I want to end it all",
            "I want to end my life",
            "I should die.",
        ]

        self.distress_phrases = [
            "hopeless",
            "completely hopeless",
            "can't go on",
            "cannot go on",
            "nothing matters",
            "life is pointless",
            "feel worthless",
            "feel like a burden",
            "no one would care",
            "nobody would care",
            "feel like giving up",
        ]

    def detect(self, text: str) -> SafetyResult:

        normalized = text.lower().strip()

        for phrase in self.crisis_phrases:
            if phrase in normalized:
                return SafetyResult(
                    SafetyLevel.CRISIS,
                    reason=f"Matched crisis indicator: '{phrase}'"
                )

        for phrase in self.distress_phrases:
            if phrase in normalized:
                return SafetyResult(
                    SafetyLevel.DISTRESS,
                    reason=f"Matched distress indicator: '{phrase}'"
                )

        return SafetyResult(SafetyLevel.SAFE)