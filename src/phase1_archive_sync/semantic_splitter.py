"""
Semantic Splitter for Resonance Archive System.

This module splits text into semantic chunks while preserving context and structure.
"""
import re
import logging
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """Represents a semantic chunk of text with metadata."""
    text: str
    start_offset: int
    end_offset: int
    seq: int
    source_markers: Optional[str] = None


class SemanticSplitter:
    """Splits text into semantic chunks with configurable parameters."""

    def __init__(self, max_chars: int = 600, overlap: int = 100):
        """
        Initialize SemanticSplitter.

        Args:
            max_chars: Maximum characters per chunk (default: 600)
            overlap: Overlap characters between chunks (default: 100)
        """
        self.max_chars = max_chars
        self.overlap = overlap

    def split(self, text: str) -> List[Chunk]:
        """
        Split text into semantic chunks following priority rules.

        Priority:
        1. Protect code blocks
        2. Split by headings/horizontal rules
        3. Split by paragraphs
        4. Split by sentences
        5. Split by commas/spaces
        6. Hard split with overlap

        Args:
            text: Input text to split

        Returns:
            List of Chunk objects
        """
        if not text.strip():
            return []

        chunks = []
        current_offset = 0

        # Step 1: Extract and protect code blocks
        segments = self._extract_code_blocks(text)

        for segment_text, is_code_block in segments:
            if is_code_block:
                # Code block: treat as single chunk even if oversized
                if len(segment_text) > self.max_chars:
                    logger.warning(
                        f"Code block exceeds max_chars ({len(segment_text)} > {self.max_chars}). "
                        "Keeping as single chunk."
                    )
                chunk = Chunk(
                    text=segment_text,
                    start_offset=current_offset,
                    end_offset=current_offset + len(segment_text),
                    seq=len(chunks),
                    source_markers="code_block"
                )
                chunks.append(chunk)
                current_offset += len(segment_text)
            else:
                # Non-code block: apply splitting rules
                segment_chunks = self._split_segment(segment_text, current_offset)
                for chunk in segment_chunks:
                    chunk.seq = len(chunks)
                    chunks.append(chunk)
                current_offset += len(segment_text)

        return chunks

    def _extract_code_blocks(self, text: str) -> List[tuple[str, bool]]:
        """
        Extract code blocks and regular text segments.

        Args:
            text: Input text

        Returns:
            List of (segment_text, is_code_block) tuples
        """
        segments = []
        pattern = r'(```[\s\S]*?```)'
        parts = re.split(pattern, text)

        for part in parts:
            if not part:
                continue
            is_code_block = part.startswith('```') and part.endswith('```')
            segments.append((part, is_code_block))

        return segments

    def _split_segment(self, text: str, base_offset: int) -> List[Chunk]:
        """
        Split a non-code segment using priority rules.

        Args:
            text: Segment text
            base_offset: Offset in original text

        Returns:
            List of Chunk objects
        """
        # Step 2: Split by headings and horizontal rules
        parts = self._split_by_structure(text)

        chunks = []
        current_offset = base_offset

        for part_text, marker in parts:
            if len(part_text) <= self.max_chars:
                # Small enough: create chunk
                chunk = Chunk(
                    text=part_text,
                    start_offset=current_offset,
                    end_offset=current_offset + len(part_text),
                    seq=0,  # Will be set later
                    source_markers=marker
                )
                chunks.append(chunk)
                current_offset += len(part_text)
            else:
                # Too large: apply further splitting
                sub_chunks = self._split_large_part(part_text, current_offset, marker)
                chunks.extend(sub_chunks)
                current_offset += len(part_text)

        return chunks

    def _split_by_structure(self, text: str) -> List[tuple[str, Optional[str]]]:
        """
        Split by Markdown structure (headings, horizontal rules).

        Args:
            text: Input text

        Returns:
            List of (text, marker) tuples
        """
        # Pattern for headings (# Title) and horizontal rules (---, ***)
        pattern = r'(^#{1,6}\s+.+$|^---+$|^\*\*\*+$)'
        parts = re.split(pattern, text, flags=re.MULTILINE)

        segments = []
        current_marker = None

        for part in parts:
            if not part:
                continue

            # Check if this is a marker
            if re.match(r'^#{1,6}\s+', part):
                current_marker = part.strip()
                segments.append((part, current_marker))
            elif re.match(r'^(---+|\*\*\*+)$', part):
                current_marker = "separator"
                segments.append((part, current_marker))
            else:
                segments.append((part, current_marker))

        return segments if segments else [(text, None)]

    def _split_large_part(self, text: str, base_offset: int, marker: Optional[str]) -> List[Chunk]:
        """
        Split large text part using cascading rules.

        Args:
            text: Text to split
            base_offset: Offset in original text
            marker: Source marker

        Returns:
            List of Chunk objects
        """
        # Step 3: Split by paragraphs
        paragraphs = text.split('\n\n')

        chunks = []
        current_offset = base_offset

        for para in paragraphs:
            if len(para) <= self.max_chars:
                if para.strip():
                    chunk = Chunk(
                        text=para,
                        start_offset=current_offset,
                        end_offset=current_offset + len(para),
                        seq=0,
                        source_markers=marker
                    )
                    chunks.append(chunk)
                current_offset += len(para) + 2  # +2 for '\n\n'
            else:
                # Paragraph too large: split by sentences
                para_chunks = self._split_by_sentences(para, current_offset, marker)
                chunks.extend(para_chunks)
                current_offset += len(para) + 2

        return chunks

    def _split_by_sentences(self, text: str, base_offset: int, marker: Optional[str]) -> List[Chunk]:
        """
        Split by sentences (。！？).

        Args:
            text: Text to split
            base_offset: Offset in original text
            marker: Source marker

        Returns:
            List of Chunk objects
        """
        # Split by sentence delimiters
        sentences = re.split(r'([。！？])', text)

        chunks = []
        current_text = ""
        current_start = base_offset

        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            delimiter = sentences[i + 1] if i + 1 < len(sentences) else ""
            full_sentence = sentence + delimiter

            if len(current_text + full_sentence) <= self.max_chars:
                current_text += full_sentence
            else:
                # Flush current chunk
                if current_text:
                    chunk = Chunk(
                        text=current_text,
                        start_offset=current_start,
                        end_offset=current_start + len(current_text),
                        seq=0,
                        source_markers=marker
                    )
                    chunks.append(chunk)
                    current_start += len(current_text)

                # Check if single sentence exceeds max
                if len(full_sentence) > self.max_chars:
                    # Split by commas
                    comma_chunks = self._split_by_commas(full_sentence, current_start, marker)
                    chunks.extend(comma_chunks)
                    current_start += len(full_sentence)
                    current_text = ""
                else:
                    current_text = full_sentence

        # Flush remaining
        if current_text:
            chunk = Chunk(
                text=current_text,
                start_offset=current_start,
                end_offset=current_start + len(current_text),
                seq=0,
                source_markers=marker
            )
            chunks.append(chunk)

        return chunks

    def _split_by_commas(self, text: str, base_offset: int, marker: Optional[str]) -> List[Chunk]:
        """
        Split by commas (、) and spaces.

        Args:
            text: Text to split
            base_offset: Offset in original text
            marker: Source marker

        Returns:
            List of Chunk objects
        """
        # Split by commas and spaces
        parts = re.split(r'([、\s])', text)

        chunks = []
        current_text = ""
        current_start = base_offset

        for i in range(0, len(parts), 2):
            part = parts[i]
            delimiter = parts[i + 1] if i + 1 < len(parts) else ""
            full_part = part + delimiter

            if len(current_text + full_part) <= self.max_chars:
                current_text += full_part
            else:
                # Flush current chunk
                if current_text:
                    chunk = Chunk(
                        text=current_text,
                        start_offset=current_start,
                        end_offset=current_start + len(current_text),
                        seq=0,
                        source_markers=marker
                    )
                    chunks.append(chunk)
                    current_start += len(current_text)

                # Check if single part exceeds max
                if len(full_part) > self.max_chars:
                    # Hard split with overlap
                    hard_chunks = self._hard_split_with_overlap(full_part, current_start, marker)
                    chunks.extend(hard_chunks)
                    current_start += len(full_part)
                    current_text = ""
                else:
                    current_text = full_part

        # Flush remaining
        if current_text:
            chunk = Chunk(
                text=current_text,
                start_offset=current_start,
                end_offset=current_start + len(current_text),
                seq=0,
                source_markers=marker
            )
            chunks.append(chunk)

        return chunks

    def _hard_split_with_overlap(self, text: str, base_offset: int, marker: Optional[str]) -> List[Chunk]:
        """
        Hard split text with overlap.

        Args:
            text: Text to split
            base_offset: Offset in original text
            marker: Source marker

        Returns:
            List of Chunk objects
        """
        chunks = []
        start = 0

        while start < len(text):
            end = min(start + self.max_chars, len(text))
            chunk_text = text[start:end]

            chunk = Chunk(
                text=chunk_text,
                start_offset=base_offset + start,
                end_offset=base_offset + end,
                seq=0,
                source_markers=marker
            )
            chunks.append(chunk)

            # Move forward with overlap
            start = end - self.overlap if end < len(text) else len(text)

        return chunks
