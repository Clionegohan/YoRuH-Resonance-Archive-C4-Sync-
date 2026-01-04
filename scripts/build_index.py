"""
Build Index Script for Resonance Archive System.

Phase 1 統合スクリプト: VaultScanner → MultilevelVectorizer → ChromaDBIndexer
"""
import logging
import time
from pathlib import Path
from typing import Dict, Any
import psutil
from tqdm import tqdm

from src.phase1_archive_sync.vault_scanner import VaultScanner
from src.phase1_archive_sync.multilevel_vectorizer import MultilevelVectorizer
from src.phase1_archive_sync.chromadb_indexer import ChromaDBIndexer

logger = logging.getLogger(__name__)


def build_index(
    vault_root: str,
    db_path: str = "./.chroma_db",
    show_progress: bool = True
) -> Dict[str, Any]:
    """
    Phase 1全体のインデックス構築を実行

    Args:
        vault_root: Obsidian Vaultのルートパス
        db_path: ChromaDB永続化ディレクトリパス (default: ./.chroma_db)
        show_progress: 進捗表示の有効/無効 (default: True)

    Returns:
        統計情報:
            - files_scanned: スキャンされたファイル数
            - files_processed: 処理されたファイル数
            - vectors_generated: 生成されたベクトル総数
            - level1_count: Level 1ベクトル数（要約）
            - level2_count: Level 2ベクトル数（チャンク）
            - elapsed_time: 処理時間（秒）
            - memory_peak_mb: ピークメモリ使用量（MB）
    """
    start_time = time.time()
    process = psutil.Process()
    memory_start = process.memory_info().rss / 1024 / 1024  # MB
    memory_peak = memory_start

    # Statistics
    files_scanned = 0
    files_processed = 0
    level1_count = 0
    level2_count = 0

    try:
        # Step 1: Scan vault
        if show_progress:
            print(f"\n{'='*60}")
            print(f"📂 Scanning Vault: {vault_root}")
            print(f"{'='*60}\n")

        scanner = VaultScanner(vault_root=vault_root)
        file_paths = scanner.scan()
        files_scanned = len(file_paths)

        if show_progress:
            print(f"✅ Found {files_scanned} files to index\n")

        if files_scanned == 0:
            if show_progress:
                print("⚠️  No files found to index")
            return {
                'files_scanned': 0,
                'files_processed': 0,
                'vectors_generated': 0,
                'level1_count': 0,
                'level2_count': 0,
                'elapsed_time': time.time() - start_time,
                'memory_peak_mb': memory_peak
            }

        # Step 2: Initialize components
        vectorizer = MultilevelVectorizer()
        indexer = ChromaDBIndexer(persist_directory=db_path)

        # Step 3: Process files
        if show_progress:
            print("🔄 Processing files and generating vectors...\n")

        all_records = []
        iterator = tqdm(file_paths, desc="Vectorizing files", disable=not show_progress)

        for file_path in iterator:
            try:
                # Read file
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()

                # Get relative path from vault root
                relative_path = str(Path(file_path).relative_to(vault_root))

                # Vectorize
                records = vectorizer.vectorize(text=text, file_path=relative_path)

                if records:
                    all_records.extend(records)
                    files_processed += 1

                    # Count by level
                    for record in records:
                        if record.metadata['level'] == 1:
                            level1_count += 1
                        else:
                            level2_count += 1

                    # Update memory peak
                    current_memory = process.memory_info().rss / 1024 / 1024
                    memory_peak = max(memory_peak, current_memory)

            except Exception as e:
                logger.exception(f"Error processing {file_path}")
                continue

        # Step 4: Batch insert to ChromaDB
        if all_records:
            if show_progress:
                print(f"\n💾 Indexing {len(all_records)} vectors to ChromaDB...\n")

            result = indexer.add_vectors_batch(
                records=all_records,
                show_progress=show_progress
            )

            if show_progress:
                print(f"\n✅ Successfully indexed {result['success']} vectors")
                if result['failed'] > 0:
                    print(f"⚠️  Failed to index {result['failed']} vectors")

        # Final statistics
        elapsed_time = time.time() - start_time
        vectors_generated = level1_count + level2_count

        if show_progress:
            print(f"\n{'='*60}")
            print("📊 Index Build Complete")
            print(f"{'='*60}")
            print(f"Files scanned:       {files_scanned}")
            print(f"Files processed:     {files_processed}")
            print(f"Vectors generated:   {vectors_generated}")
            print(f"  - Level 1 (summary): {level1_count}")
            print(f"  - Level 2 (chunks):  {level2_count}")
            print(f"Elapsed time:        {elapsed_time:.2f} seconds")
            print(f"Memory peak:         {memory_peak:.2f} MB")
            print(f"{'='*60}\n")

        return {
            'files_scanned': files_scanned,
            'files_processed': files_processed,
            'vectors_generated': vectors_generated,
            'level1_count': level1_count,
            'level2_count': level2_count,
            'elapsed_time': elapsed_time,
            'memory_peak_mb': memory_peak
        }

    except Exception as e:
        logger.exception("Error during index build")
        return {
            'files_scanned': files_scanned,
            'files_processed': files_processed,
            'vectors_generated': level1_count + level2_count,
            'level1_count': level1_count,
            'level2_count': level2_count,
            'elapsed_time': time.time() - start_time,
            'memory_peak_mb': memory_peak
        }


if __name__ == "__main__":
    import sys

    # Simple CLI interface
    vault_root = sys.argv[1] if len(sys.argv) > 1 else "."
    db_path = sys.argv[2] if len(sys.argv) > 2 else "./.chroma_db"

    build_index(vault_root=vault_root, db_path=db_path, show_progress=True)
