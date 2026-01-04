"""
File Watcher for Resonance Archive System.

Watches diary files using Watchdog and triggers callbacks on file changes.
"""
import logging
from pathlib import Path
from typing import Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)


class DiaryFileHandler(FileSystemEventHandler):
    """Event handler for diary file modifications."""

    def __init__(self, callback: Callable):
        """
        Initialize event handler.

        Args:
            callback: Function to call when a diary file is modified
        """
        super().__init__()
        self.callback = callback

    def on_modified(self, event):
        """
        Handle file modification events.

        Args:
            event: FileSystemEvent from Watchdog
        """
        # Only process file events (not directory events)
        if not event.is_directory:
            # Only process .md files
            if event.src_path.endswith('.md'):
                logger.debug(f"File modified: {event.src_path}")
                self.callback(event)


class FileWatcher:
    """Watches diary files for changes using Watchdog."""

    def __init__(self, vault_root: str, on_change_callback: Callable):
        """
        Initialize FileWatcher.

        Args:
            vault_root: Root directory of the Obsidian vault
            on_change_callback: Callback function to execute when files change
        """
        self.vault_root = vault_root
        self.diary_dir = str(Path(vault_root) / "01_diary")
        self.callback = on_change_callback

        # Create event handler
        self.event_handler = DiaryFileHandler(callback=on_change_callback)

        # Create observer (not started yet)
        self.observer = Observer()

    def start(self):
        """Start watching the diary directory."""
        logger.info(f"Starting file watcher on: {self.diary_dir}")

        # Schedule observer to watch diary directory recursively
        self.observer.schedule(
            self.event_handler,
            self.diary_dir,
            recursive=True
        )

        # Start observer thread
        self.observer.start()

    def stop(self):
        """Stop watching the diary directory."""
        logger.info("Stopping file watcher")
        self.observer.stop()
        self.observer.join()
