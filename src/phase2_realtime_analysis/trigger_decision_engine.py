"""
Trigger Decision Engine for Resonance Archive System.

Calculates confidence scores from multiple signals and determines if analysis should be triggered.
"""
from typing import ClassVar, List, Union


class TriggerDecisionEngine:
    """
    Determines whether to trigger analysis based on multiple signal types.

    Confidence is calculated by summing weights of detected signal types.
    Duplicate signal types are counted only once.
    """

    # Signal weights (adjustable for tuning)
    WEIGHTS: ClassVar[dict[str, float]] = {
        # Structural signals
        'paragraph_break': 0.2,
        'horizontal_rule': 0.3,
        'sentence_end': 0.1,

        # Timing signals
        'long_pause': 0.4,
        'medium_pause': 0.2,

        # Delta signals
        'large_delta': 0.3,
        'medium_delta': 0.2,
        'small_delta': 0.1,
    }

    # Confidence threshold for triggering analysis
    CONFIDENCE_THRESHOLD: ClassVar[float] = 0.6

    def calculate_confidence(
        self,
        signals: List[Union['StructuralSignal', 'TimingSignal', 'DeltaSignal']]
    ) -> float:
        """
        Calculate confidence score from detected signals.

        Args:
            signals: List of detected signals (StructuralSignal, TimingSignal, DeltaSignal)

        Returns:
            Confidence score (0.0 to 1.0)

        Implementation:
            - Extracts unique signal types (deduplicates)
            - Sums weights for each unique type
            - Caps result at 1.0
        """
        if not signals:
            return 0.0

        # Extract unique signal types
        detected_types = set()
        for signal in signals:
            detected_types.add(signal.type)

        # Sum weights for detected types
        score = sum(self.WEIGHTS.get(signal_type, 0.0) for signal_type in detected_types)

        # Cap at 1.0
        return min(score, 1.0)

    def should_trigger(
        self,
        signals: List[Union['StructuralSignal', 'TimingSignal', 'DeltaSignal']]
    ) -> bool:
        """
        Determine if analysis should be triggered based on confidence score.

        Args:
            signals: List of detected signals

        Returns:
            True if confidence >= threshold, False otherwise
        """
        confidence = self.calculate_confidence(signals)
        return confidence >= self.CONFIDENCE_THRESHOLD
