"""
Resonance Archive System - Main Integration Class

Integrates all components from Phase 1-3 into a unified system.
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ResonanceArchiveSystem:
    """
    Main system class integrating all Resonance Archive components.

    Coordinates:
    - Phase 1: ChromaDBIndexer (archive synchronization)
    - Phase 2: FileWatcher (real-time analysis)
    - Phase 3: ReportPipeline (Pod201 report generation)
    """

    def __init__(self, indexer, watcher, pipeline):
        """
        Initialize Resonance Archive System.

        Args:
            indexer: ChromaDBIndexer instance for vault indexing
            watcher: FileWatcher instance for file monitoring
            pipeline: ReportPipeline instance for report generation
        """
        self.indexer = indexer
        self.watcher = watcher
        self.pipeline = pipeline
        self._monitoring_active = False

    def initialize(self) -> Optional[Dict[str, Any]]:
        """
        Initialize the system by scanning and indexing the vault.

        Returns:
            Dict with initialization results, or None on error

        Implementation:
            - Calls indexer.index_vault() to build the index
            - Logs progress and errors
            - Returns summary of indexed items
        """
        try:
            logger.info("Initializing Resonance Archive System...")
            result = self.indexer.index_vault()
            logger.info(f"Initialization complete: {result}")
            return result
        except Exception as e:
            logger.error(f"Initialization failed: {e}", exc_info=True)
            return {"error": str(e), "success": False}

    def start_monitoring(self):
        """
        Start file monitoring for real-time analysis.

        Implementation:
            - Starts FileWatcher to monitor file changes
            - Runs in background
            - Sets monitoring flag
        """
        try:
            logger.info("Starting file monitoring...")
            self.watcher.start()
            self._monitoring_active = True
            logger.info("File monitoring started")
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}", exc_info=True)
            self._monitoring_active = False

    def search(self, query: str) -> str:
        """
        Perform manual similarity search and generate Pod201 report.

        Args:
            query: Search query string

        Returns:
            Pod201-style report as string

        Implementation:
            - Uses pipeline.generate() to search and generate report
            - Handles errors gracefully
        """
        try:
            logger.info(f"Performing search for query: {query}")
            report = self.pipeline.generate(query)
            return report
        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            return f"【エラー】検索に失敗しました: {str(e)}"

    def get_status(self) -> Dict[str, Any]:
        """
        Get current system status.

        Returns:
            Dict containing system status information

        Implementation:
            - Checks ChromaDB connection and index count
            - Checks monitoring state
            - Returns component health status
        """
        try:
            status = {
                "monitoring": self._monitoring_active,
                "indexed_count": self.indexer.get_collection_count() if hasattr(self.indexer, 'get_collection_count') else 0,
                "watcher_running": self.watcher.is_running() if hasattr(self.watcher, 'is_running') else False
            }
            return status
        except Exception as e:
            logger.error(f"Failed to get status: {e}", exc_info=True)
            return {"error": str(e)}

    def shutdown(self):
        """
        Shutdown the system gracefully.

        Implementation:
            - Stops FileWatcher (always, for safety)
            - Releases resources
            - Logs shutdown progress
        """
        try:
            logger.info("Shutting down Resonance Archive System...")

            # Always try to stop watcher for safety
            self.watcher.stop()
            self._monitoring_active = False

            logger.info("Shutdown complete")
        except Exception as e:
            logger.error(f"Shutdown error: {e}", exc_info=True)
