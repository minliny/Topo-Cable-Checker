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
from src.infrastructure.repository import BaselineRepository
from src.domain.baseline_model import BaselineProfile
from src.crosscutting.errors.exceptions import DomainError, ErrorCode
from src.crosscutting.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SaveDraftResult:
    success: bool
    saved_at: Optional[str] = None
    message: Optional[str] = None


@dataclass
class LoadDraftResult:
    has_draft: bool
    draft_data: Optional[Dict[str, Any]] = None
    saved_at: Optional[str] = None


class RuleDraftSaveService:
    """
    Application service for managing working drafts on baselines.
    Drafts are persisted as the working_draft field on BaselineProfile.
    """

    def __init__(self, repo: Optional[IBaselineRepository] = None):
        self.repo = repo or BaselineRepository()

    def save_draft(
        self,
        baseline_id: str,
        req: Any,
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

        draft_wrapper = {
            "rule_set": getattr(req, "rule_set", req.get("rule_set", {}) if isinstance(req, dict) else {}),
            "active_rule_id": getattr(req, "active_rule_id", req.get("active_rule_id") if isinstance(req, dict) else None),
            "saved_at": datetime.datetime.now().isoformat()
        }
        
        # In dict form or object form
        if isinstance(baseline, dict):
            baseline["working_draft"] = draft_wrapper
        else:
            baseline.working_draft = draft_wrapper
        self.repo.save(baseline)

        logger.info(f"Draft saved for baseline={baseline_id}")

        return SaveDraftResult(
            success=True,
            saved_at=draft_wrapper["saved_at"],
            message="Draft saved successfully"
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
            return LoadDraftResult(has_draft=False)

        return LoadDraftResult(
            has_draft=True,
            draft_data=draft,
            saved_at=draft.get("saved_at")
        )

    def clear_draft(self, baseline_id: str) -> bool:
        """
        Clear the working draft after successful publish.
        Sets working_draft to None (strict: not {}).
        
        Returns True if draft was cleared, False if baseline not found.
        """
        baseline = self.repo.get_by_id(baseline_id)
        if not baseline:
            logger.warning(f"Cannot clear draft: baseline {baseline_id} not found")
            return False

        if baseline.working_draft is not None:
            baseline.working_draft = None
            self.repo.save(baseline)
            logger.info(f"Draft cleared for baseline={baseline_id}")

        return True
