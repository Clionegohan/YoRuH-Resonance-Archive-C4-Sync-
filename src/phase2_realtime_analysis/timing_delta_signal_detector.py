"""
Timing and Delta Signal Detector for Resonance Archive System.

Detects timing patterns (pauses) and content delta (character additions).
"""
from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass
class TimingSignal:
    """Represents a detected timing signal (pause)."""

    type: str  # "long_pause" | "medium_pause"
    elapsed_seconds: float  # Elapsed time since last save


@dataclass
class DeltaSignal:
    """Represents a detected delta signal (character addition)."""

    type: str  # "large_delta" | "medium_delta" | "small_delta"
    char_delta: int  # Number of characters added


class TimingDeltaSignalDetector:
    """Detects timing and delta signals in text changes."""

    # Timing thresholds (seconds)
    LONG_PAUSE_SECONDS = 300  # 5 minutes
    MEDIUM_PAUSE_SECONDS = 120  # 2 minutes

    # Delta thresholds (characters)
    LARGE_DELTA_CHARS = 100
    MEDIUM_DELTA_CHARS = 30
    SMALL_DELTA_CHARS = 10

    def detect(
        self,
        previous_text: Optional[str],
        previous_timestamp: Optional[float],
        current_text: str,
        current_timestamp: float
    ) -> List[Union[TimingSignal, DeltaSignal]]:
        """
        Detect timing and delta signals from text changes.

        Args:
            previous_text: Previous text content (None for first save)
            previous_timestamp: Previous save timestamp (None for first save)
            current_text: Current text content
            current_timestamp: Current save timestamp

        Returns:
            List of TimingSignal and DeltaSignal objects
        """
        signals = []

        # Detect timing signals (only if previous save exists)
        if previous_timestamp is not None:
            elapsed = current_timestamp - previous_timestamp
            timing_signal = self._detect_timing_signal(elapsed)
            if timing_signal:
                signals.append(timing_signal)

        # Detect delta signals
        if previous_text is None:
            # First save: treat all content as new
            char_delta = len(current_text)
        else:
            # Calculate delta
            char_delta = len(current_text) - len(previous_text)

        # Only positive deltas (additions) are considered
        if char_delta > 0:
            delta_signal = self._detect_delta_signal(char_delta)
            if delta_signal:
                signals.append(delta_signal)

        return signals

    def _detect_timing_signal(self, elapsed_seconds: float) -> Optional[TimingSignal]:
        """
        Detect timing signal based on elapsed time.

        Args:
            elapsed_seconds: Elapsed time since last save

        Returns:
            TimingSignal or None
        """
        if elapsed_seconds >= self.LONG_PAUSE_SECONDS:
            return TimingSignal(
                type="long_pause",
                elapsed_seconds=elapsed_seconds
            )
        elif elapsed_seconds >= self.MEDIUM_PAUSE_SECONDS:
            return TimingSignal(
                type="medium_pause",
                elapsed_seconds=elapsed_seconds
            )
        else:
            return None

    def _detect_delta_signal(self, char_delta: int) -> Optional[DeltaSignal]:
        """
        Detect delta signal based on character addition.

        Args:
            char_delta: Number of characters added (positive value)

        Returns:
            DeltaSignal or None
        """
        if char_delta >= self.LARGE_DELTA_CHARS:
            return DeltaSignal(
                type="large_delta",
                char_delta=char_delta
            )
        elif char_delta >= self.MEDIUM_DELTA_CHARS:
            return DeltaSignal(
                type="medium_delta",
                char_delta=char_delta
            )
        elif char_delta >= self.SMALL_DELTA_CHARS:
            return DeltaSignal(
                type="small_delta",
                char_delta=char_delta
            )
        else:
            return None
