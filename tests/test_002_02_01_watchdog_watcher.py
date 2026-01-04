"""
Test for Subtask 002-02-01: Watchdogファイル監視実装

このテストは承認されたAcceptance Criteriaから導出されています。
"""
import pytest
import shutil
import tempfile
import time
from pathlib import Path
from datetime import datetime
from src.phase2_realtime_analysis.file_watcher import FileWatcher


@pytest.fixture
def temp_diary_dir():
    """テスト用の一時的な日記ディレクトリを作成"""
    temp_dir = tempfile.mkdtemp()
    today = datetime.now()
    diary_path = Path(temp_dir) / "01_diary" / str(today.year)
    diary_path.mkdir(parents=True)

    # Create today's diary file
    diary_file = diary_path / f"{today.strftime('%Y-%m-%d')}.md"
    diary_file.write_text("# Initial content\n\nTest diary.")

    yield str(diary_path.parent.parent), str(diary_file)

    # Cleanup
    shutil.rmtree(temp_dir)


def test_file_watcher_class_exists():
    """AC: FileWatcherクラスが存在すること"""
    assert FileWatcher is not None


def test_watches_diary_directory(temp_diary_dir):
    """AC: Watchdogを統合し、01_diary/YYYY/YYYY-MM-dd.md を監視すること"""
    vault_root, _ = temp_diary_dir

    watcher = FileWatcher(vault_root=vault_root, on_change_callback=lambda _: None)

    # Should watch the 01_diary directory
    expected_diary_dir = Path(vault_root) / "01_diary"
    assert watcher.diary_dir == str(expected_diary_dir)


def test_on_modified_event_fires(temp_diary_dir):
    """AC: ファイルが保存された際にon_modifiedイベントが発火すること"""
    vault_root, diary_file = temp_diary_dir
    events_received = []

    def callback(event):
        events_received.append(event)

    watcher = FileWatcher(vault_root=vault_root, on_change_callback=callback)
    watcher.start()

    try:
        # Modify the diary file
        with open(diary_file, 'a', encoding='utf-8') as f:
            f.write("\n\nNew paragraph added.")

        # Wait for watchdog to detect the change
        time.sleep(0.5)

        # Should have received at least one event
        assert len(events_received) > 0

    finally:
        watcher.stop()


def test_passes_event_to_callback(temp_diary_dir):
    """AC: ファイル変更イベントを次の処理に渡すこと"""
    vault_root, diary_file = temp_diary_dir
    events_received = []

    def callback(event):
        events_received.append(event)

    watcher = FileWatcher(vault_root=vault_root, on_change_callback=callback)
    watcher.start()

    try:
        # Modify file
        with open(diary_file, 'a', encoding='utf-8') as f:
            f.write("\n\nContent update.")

        time.sleep(0.5)

        # Event should be passed to callback
        assert len(events_received) > 0
        event = events_received[0]

        # Event should contain file path
        assert hasattr(event, 'src_path')
        assert diary_file in str(event.src_path)

    finally:
        watcher.stop()
