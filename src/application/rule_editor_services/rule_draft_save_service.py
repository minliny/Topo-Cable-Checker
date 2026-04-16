"""
A1-3: Rule Draft Save Service — Save / Load / Clear working drafts.

Design decisions:
- Reuses BaselineRepository for persistence (no new repository)
- working_draft is stored as a field on BaselineProfile
- Strict semantics: None = no draft, dict = draft exists, {} is NOT used for "no draft"
- Save does NOT compile/validate the draft — invalid drafts can be saved
- Clear is called after successful publish to remove the working draft
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import datetime

from src.domain.interfaces import IBaselineRepository
from src.domain.baseline_model import BaselineProfile
from src.crosscutting.errors.exceptions import DomainError, ErrorCode, ConcurrencyError
from src.crosscutting.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SaveDraftResult:
    success: bool
    saved_at: Optional[str] = None
    message: Optional[str] = None
    new_revision: Optional[int] = None


@dataclass
class LoadDraftResult:
    has_draft: bool
    draft_data: Optional[Dict[str, Any]] = None
    saved_at: Optional[str] = None
    base_revision: Optional[int] = None


class RuleDraftSaveService:
    """
    Application service for managing working drafts on baselines.
    Drafts are persisted as the working_draft field on BaselineProfile.
    """
class RuleDraftSaveService:
    def __init__(self, repo: IBaselineRepository):
        self.repo = repo

    def save_draft(
        self,
        baseline_id: str,
        rule_id: str,
        rule_type: str,
        target_type: str,
        severity: str,
        params: Dict[str, Any],
        expected_revision: int,
    ) -> SaveDraftResult:
        """
        Save a working draft to the baseline.
        
        A1-8: Invalid drafts CAN be saved (no compile gate).
        This is intentional — users save work-in-progress.
        """
        baseline = self.repo.get_by_id(baseline_id)
        if not baseline:
            return SaveDraftResult(
                success=False,
                message=f"Baseline {baseline_id} not found"
            )

        draft_data = {
            "rule_id": rule_id,
            "rule_type": rule_type,
            "target_type": target_type,
            "severity": severity,
            "params": params,
            "saved_at": datetime.datetime.now().isoformat(),
        }

        baseline.working_draft = draft_data
        self.repo.save(baseline, expected_revision=expected_revision)

        saved_at = draft_data["saved_at"]
        logger.info(f"Draft saved for baseline={baseline_id} rule_id={rule_id}")

        # Re-fetch or get the updated revision after save
        updated_baseline = self.repo.get_by_id(baseline_id)
        new_rev = getattr(updated_baseline, "revision", 1)

        return SaveDraftResult(
            success=True,
            saved_at=saved_at,
            message="Draft saved successfully",
            new_revision=new_rev
        )

    def load_draft(self, baseline_id: str) -> LoadDraftResult:
        """
        Load a working draft from the baseline.
        Returns has_draft=False if no draft exists (working_draft is None).
        """
        baseline = self.repo.get_by_id(baseline_id)
        if not baseline:
            return LoadDraftResult(has_draft=False)

        draft = baseline.working_draft
        if draft is None:
            return LoadDraftResult(
                has_draft=False,
                base_revision=getattr(baseline, "revision", 1)
            )

        return LoadDraftResult(
            has_draft=True,
            draft_data=draft,
            saved_at=draft.get("saved_at"),
            base_revision=getattr(baseline, "revision", 1)
        )

    def clear_draft(self, baseline_id: str, expected_revision: int) -> Optional[int]:
        baseline = self.repo.get_by_id(baseline_id)
        if not baseline:
            logger.warning(f"Cannot clear draft: baseline {baseline_id} not found")
            return None

        current_rev = getattr(baseline, "revision", 1)
        if current_rev != expected_revision:
            raise ConcurrencyError(
                f"Baseline {baseline_id} has been modified by another process. "
                f"Expected revision: {expected_revision}, got: {current_rev}"
            )

        if baseline.working_draft is None:
            return current_rev

        baseline.working_draft = None
        self.repo.save(baseline, expected_revision=expected_revision)

        updated = self.repo.get_by_id(baseline_id)
        new_rev = getattr(updated, "revision", 1)
        logger.info(f"Draft cleared for baseline={baseline_id}")
        return new_rev
