import { 
  BaselineNodeDTO, 
  VersionMetaDTO, 
  ValidationResultDTO, 
  PublishResultDTO, 
  DiffSourceTargetDTO, 
  RollbackCandidateDTO
} from '../types/dto';

/**
 * Adapter layer to normalize raw backend responses into strict DTOs.
 * Ensures the UI and Reducer never consume unexpected data structures.
 */

export function normalizeBaselineTreeResponse(raw: any): BaselineNodeDTO[] {
  if (!raw || !Array.isArray(raw)) {
    console.warn('normalizeBaselineTreeResponse: Expected an array, got', typeof raw);
    return [];
  }
  
  return raw.map((item: any) => ({
    id: item.id || `fallback-id-${Math.random()}`,
    type: item.type || 'baseline_root',
    name: item.name || item.title || 'Unknown',
    baseline_id: item.baseline_id || item.id,
    parent_id: item.parent_id,
    version_id: item.version_id || 'root',
    source_version_id: item.source_version_id,
    source_version_label: item.source_version_label,
    status: item.status || 'draft',
  }));
}

export function normalizeVersionDetailResponse(raw: any): VersionMetaDTO {
  if (!raw) throw new Error('normalizeVersionDetailResponse: Raw response is empty');
  
  return {
    version_id: raw.version_id || raw.version || 'unknown-version',
    baseline_id: raw.baseline_id || 'unknown-baseline',
    version_label: raw.version_label || raw.name || raw.version || 'Unnamed Version',
    summary: raw.summary || 'No summary provided',
    publisher: raw.publisher || raw.author || 'System',
    published_at: raw.published_at || raw.timestamp || new Date().toISOString(),
    parent_version_id: raw.parent_version_id,
  };
}

export function normalizeValidationResponse(raw: any): ValidationResultDTO {
  // Handle both { valid: true } and { validation_result: { valid: true } } structures
  const data = raw?.validation_result || raw || {};
  
  const is_valid = data.valid === true;
  const raw_issues = Array.isArray(data.issues) ? data.issues : (Array.isArray(data.errors) ? data.errors : []);
  
  const issues = raw_issues.map((issue: any) => {
    // If issue is just a string, wrap it
    if (typeof issue === 'string') {
      return {
        field_path: 'unknown',
        issue_type: 'error',
        message: issue,
      };
    }
    
    return {
      field_path: issue.field_path || issue.field || 'unknown',
      issue_type: issue.issue_type || (issue.severity === 'warning' ? 'warning' : 'error'),
      message: issue.message || 'Unknown error',
      suggestion: issue.suggestion,
    };
  });
  
  return {
    valid: is_valid,
    issues,
  };
}

export function normalizePublishResponse(raw: any): PublishResultDTO {
  if (!raw) throw new Error('normalizePublishResponse: Raw response is empty');
  
  const success = raw.success !== false; // Default to true unless explicitly false
  
  let blocked_issues = undefined;
  if (!success && raw.blocked_issues) {
    blocked_issues = Array.isArray(raw.blocked_issues) ? raw.blocked_issues.map((i: any) => ({
      field_path: i.field_path || 'unknown',
      issue_type: 'error',
      message: i.message || 'Unknown blocking issue',
    })) : [];
  }

  return {
    success,
    version_id: raw.version_id || raw.version,
    version_label: raw.version_label || raw.version,
    summary: raw.summary || 'Published successfully',
    blocked_issues,
  };
}

export function normalizeDiffResponse(raw: any, sourceVersionId: string, targetVersionId: string): DiffSourceTargetDTO {
  if (!raw) {
    return {
      source_version_id: sourceVersionId,
      target_version_id: targetVersionId,
      diff_summary: { added: 0, removed: 0, modified: 0 },
      rules: []
    };
  }
  
  // Transform flat added/removed/modified arrays into a unified rules array if needed
  const rules: any[] = [];
  let addedCount = 0;
  let removedCount = 0;
  let modifiedCount = 0;

  if (Array.isArray(raw.rules)) {
    // Already unified format
    raw.rules.forEach((r: any) => {
      rules.push({
        rule_id: r.rule_id || r.id || `unknown-${Math.random()}`,
        change_type: r.change_type || 'modified',
        changed_fields: r.changed_fields || [],
        old_value: r.old_value,
        new_value: r.new_value,
      });
      if (r.change_type === 'added') addedCount++;
      if (r.change_type === 'removed') removedCount++;
      if (r.change_type === 'modified') modifiedCount++;
    });
  } else {
    // Old mock format: { added_rules: [], removed_rules: [], modified_rules: [] }
    if (Array.isArray(raw.added_rules)) {
      raw.added_rules.forEach((r: any) => {
        rules.push({ rule_id: r.id || r.rule_id, change_type: 'added', new_value: r });
        addedCount++;
      });
    }
    if (Array.isArray(raw.removed_rules)) {
      raw.removed_rules.forEach((r: any) => {
        rules.push({ rule_id: r.id || r.rule_id, change_type: 'removed', old_value: r });
        removedCount++;
      });
    }
    if (Array.isArray(raw.modified_rules)) {
      raw.modified_rules.forEach((r: any) => {
        rules.push({ 
          rule_id: r.id || r.rule_id, 
          change_type: 'modified', 
          changed_fields: r.changed_fields ? Object.keys(r.changed_fields) : [],
          old_value: r.old_value,
          new_value: r.new_value,
        });
        modifiedCount++;
      });
    }
  }

  return {
    source_version_id: raw.source_version_id || sourceVersionId,
    target_version_id: raw.target_version_id || targetVersionId,
    diff_summary: raw.diff_summary || { added: addedCount, removed: removedCount, modified: modifiedCount },
    rules,
  };
}

export function normalizeRollbackCandidateResponse(raw: any, fallbackBaselineId: string, fallbackSourceId: string): RollbackCandidateDTO {
  if (!raw) throw new Error('normalizeRollbackCandidateResponse: Raw response is empty');
  
  return {
    baseline_id: raw.baseline_id || fallbackBaselineId,
    source_version_id: raw.source_version_id || fallbackSourceId,
    source_version_label: raw.source_version_label || raw.source_version_id || fallbackSourceId,
    draft_data: raw.draft_data || raw.data || raw, // If the backend just returns the rule data directly
  };
}
