"""
Vault Scanner for Resonance Archive System.

This module scans the Obsidian vault and returns a list of files
that match INCLUDE patterns and don't match EXCLUDE patterns.
"""
import os
from pathlib import Path
from typing import List


class VaultScanner:
    """Scanner for Obsidian vault files."""

    # INCLUDEパターン: これらのディレクトリ配下の.mdファイルのみを対象
    INCLUDE_PATTERNS = [
        "01_diary",
        "02_notes",
        "07_works"
    ]

    # EXCLUDEパターン: これらに一致するパスは除外
    EXCLUDE_PATTERNS = [
        "00_templates",
        ".obsidian",
        ".git",
        ".vscode",
        "node_modules"
    ]

    def __init__(self, vault_root: str):
        """
        Initialize VaultScanner.

        Args:
            vault_root: Root directory path of Obsidian vault
        """
        self.vault_root = vault_root

    def scan(self) -> List[str]:
        """
        Scan vault and return list of markdown files matching patterns.

        Returns:
            List of absolute file paths that match INCLUDE patterns
            and don't match EXCLUDE patterns
        """
        matched_files = []
        vault_path = Path(self.vault_root)

        # 再帰的にすべてのファイルをスキャン
        for root, dirs, files in os.walk(vault_path):
            # EXCLUDEパターンに一致するディレクトリは探索しない
            dirs[:] = [d for d in dirs if not self._should_exclude(os.path.join(root, d))]

            # 各ファイルをチェック
            for file in files:
                file_path = os.path.join(root, file)

                # .mdファイルのみを対象
                if not file.endswith('.md'):
                    continue

                # EXCLUDEパターンチェック
                if self._should_exclude(file_path):
                    continue

                # INCLUDEパターンチェック
                if self._should_include(file_path):
                    matched_files.append(file_path)

        return sorted(matched_files)

    def _should_include(self, file_path: str) -> bool:
        """
        Check if file matches INCLUDE patterns.

        Args:
            file_path: File path to check

        Returns:
            True if file matches any INCLUDE pattern
        """
        for pattern in self.INCLUDE_PATTERNS:
            if f"/{pattern}/" in file_path or f"/{pattern}\\" in file_path:
                return True
        return False

    def _should_exclude(self, path: str) -> bool:
        """
        Check if path matches EXCLUDE patterns.

        Args:
            path: Path to check

        Returns:
            True if path matches any EXCLUDE pattern
        """
        for pattern in self.EXCLUDE_PATTERNS:
            if f"/{pattern}/" in path or f"/{pattern}\\" in path or path.endswith(f"/{pattern}"):
                return True
        return False
