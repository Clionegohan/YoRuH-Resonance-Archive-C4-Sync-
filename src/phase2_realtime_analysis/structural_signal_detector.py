"""
Structural Signal Detector for Resonance Archive System.

Detects structural patterns in text (paragraph breaks, horizontal rules, sentence ends).
"""
import re
from dataclasses import dataclass
from typing import List


@dataclass
class StructuralSignal:
    """Represents a detected structural signal in text."""

    type: str  # "paragraph_break" | "horizontal_rule" | "sentence_end"
    position: int  # Character index where the signal was detected
    pattern: str  # The actual pattern string that was matched


class StructuralSignalDetector:
    """Detects structural signals in text."""

    # Patterns to detect
    PARAGRAPH_BREAK = r"\n\n"
    HORIZONTAL_RULE = r"---"
    SENTENCE_END = r"[。！？]"

    def detect(self, text: str) -> List[StructuralSignal]:
        """
        Detect all structural signals in the given text.

        Args:
            text: Input text to analyze

        Returns:
            List of StructuralSignal objects, sorted by position
        """
        if not text:
            return []

        signals = []

        # Detect paragraph breaks
        for match in re.finditer(self.PARAGRAPH_BREAK, text):
            signals.append(
                StructuralSignal(
                    type="paragraph_break",
                    position=match.start(),
                    pattern=match.group()
                )
            )

        # Detect horizontal rules
        for match in re.finditer(self.HORIZONTAL_RULE, text):
            signals.append(
                StructuralSignal(
                    type="horizontal_rule",
                    position=match.start(),
                    pattern=match.group()
                )
            )

        # Detect sentence ends
        for match in re.finditer(self.SENTENCE_END, text):
            signals.append(
                StructuralSignal(
                    type="sentence_end",
                    position=match.start(),
                    pattern=match.group()
                )
            )

        # Sort by position
        signals.sort(key=lambda s: s.position)

        return signals
