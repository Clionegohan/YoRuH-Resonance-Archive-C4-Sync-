"""
Result Integrator for Resonance Archive System.

Integrates multi-level similarity search results.
"""
from typing import List, Dict, Any, Optional


class ResultIntegrator:
    """Integrates Level 1 and Level 2 similarity search results."""

    def integrate(
        self,
        level1_results: Optional[List[Dict[str, Any]]],
        level2_results: Optional[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Integrate Level 1 and Level 2 search results.

        Args:
            level1_results: List of Level 1 (summary) search results
            level2_results: List of Level 2 (chunk) search results

        Returns:
            Top 3 integrated results sorted by distance (ascending)

        Implementation:
            - Handles None inputs by treating them as empty lists
            - Combines both result lists
            - Deduplicates by id, keeping entry with smallest distance
            - Sorts by distance (ascending)
            - Returns top 3 results (or fewer if less than 3 available)
        """
        # Handle None inputs
        level1 = level1_results if level1_results is not None else []
        level2 = level2_results if level2_results is not None else []

        # Combine results
        combined = level1 + level2

        # Return empty if no results
        if not combined:
            return []

        # Deduplicate by id, keeping smallest distance
        id_to_result: Dict[str, Dict[str, Any]] = {}
        for result in combined:
            result_id = result["id"]
            if result_id not in id_to_result:
                id_to_result[result_id] = result
            else:
                # Keep the one with smaller distance
                if result["distance"] < id_to_result[result_id]["distance"]:
                    id_to_result[result_id] = result

        # Convert back to list
        deduplicated = list(id_to_result.values())

        # Sort by distance (ascending)
        sorted_results = sorted(deduplicated, key=lambda x: x["distance"])

        # Return top 3
        return sorted_results[:3]
