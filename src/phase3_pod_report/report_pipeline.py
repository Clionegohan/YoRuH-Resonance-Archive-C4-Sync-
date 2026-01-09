"""
Report Pipeline for Resonance Archive System.

Integrates search results and generates Pod201-style reports.
"""
from typing import List, Dict, Any, Optional


class ReportPipeline:
    """Pipeline for integrating search results and generating reports."""

    def __init__(self, result_integrator, report_generator):
        """
        Initialize ReportPipeline.

        Args:
            result_integrator: ResultIntegrator instance
            report_generator: Pod201ReportGenerator instance
        """
        self.result_integrator = result_integrator
        self.report_generator = report_generator

    def generate(
        self,
        level1_results: List[Dict[str, Any]],
        level2_results: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Generate Pod201-style report from multi-level search results.

        Args:
            level1_results: Level 1 (summary) search results
            level2_results: Level 2 (chunk) search results

        Returns:
            Generated Pod201-style report text, or None if generation fails

        Implementation:
            1. Integrates Level 1 and Level 2 results using ResultIntegrator
            2. Generates report using Pod201ReportGenerator
            3. Returns None on any error in the pipeline
        """
        try:
            # Step 1: Integrate search results (top 3)
            integrated_results = self.result_integrator.integrate(
                level1_results,
                level2_results
            )

            # Step 2: Generate Pod201-style report
            report = self.report_generator.generate_report(integrated_results)

            # Return None if generation failed
            if report is None:
                return None

            return report

        except Exception:
            # Return None on any pipeline error
            return None
