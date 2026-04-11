# Known Gaps & Future Roadmap

This document outlines the known gaps that are deliberately left open in the current Rule Editor MVP (Phase 1) implementation. These gaps do not block the functional acceptance of the three-column workbench but should be addressed in subsequent iterations before full production deployment.

## 1. Backend Application & Domain Layer

### 1.1 Incomplete User Context (Auth & Identity)
- **Status**: Hardcoded
- **Gap**: Currently, the `publish_baseline` API hardcodes the `publisher` field to `"admin"`.
- **Action Required**: Integrate FastAPI `Depends(get_current_user)` to extract real user tokens (e.g., JWT) and inject the actual username into the `version_history_meta`.

### 1.2 Shallow Diff Implementation
- **Status**: Functional but shallow
- **Gap**: The current `RuleBaselineHistoryService.diff_versions` calculates added/removed/modified rules correctly, but the `changed_fields` array for modified rules is simply returning a list of keys without deep JSON diffing of the actual rule parameters.
- **Action Required**: Implement a recursive JSON diff algorithm (like `dictdiffer` or `deepdiff`) inside the domain service to provide exact field-level change paths.

### 1.3 No Database (File-based Persistence)
- **Status**: In-Memory/JSON File
- **Gap**: The `BaselineRepository` writes to a local `baselines.json` file. While atomic write logic (`tempfile`) was added for safety, this is not suitable for horizontal scaling or concurrent multi-user environments.
- **Action Required**: Migrate `BaselineRepository` to SQLAlchemy/PostgreSQL.

---

## 2. Frontend UI & UX Enhancements

### 2.1 Physical `scrollToField` Integration
- **Status**: Partially Implemented (Logical only)
- **Gap**: The state machine correctly dispatches `JUMP_TO_FIELD` and updates the `targetFieldPath` prop in the Reducer. However, the actual Ant Design Form might not scroll if the field is nested deep inside a complex JSON string editor (like a CodeMirror or Monaco editor) rather than standard Antd Form items.
- **Action Required**: Integrate a real code editor component (e.g., `@monaco-editor/react`) and map the `targetFieldPath` to Monaco line numbers/markers.

### 2.2 Debounced Draft Autosave
- **Status**: Sync on every keystroke
- **Gap**: The `EditorView` currently dispatches `UPDATE_DRAFT` on every change. If the rule parameters JSON grows to thousands of lines, this will cause React rendering jank and state machine bloat.
- **Action Required**: Introduce a `useDebounce` hook in the editor component to batch keystrokes before syncing to the global Reducer.

### 2.3 Internationalization (i18n)
- **Status**: Hardcoded English
- **Gap**: All toast messages, modal titles, and button labels are hardcoded.
- **Action Required**: Introduce `react-i18next` and move all literal strings into locale JSON files.

### 2.4 Error Toast Normalization
- **Status**: Basic
- **Gap**: When API calls fail with generic 500s or network timeouts, the UI simply shows "Error during validation" or similar hardcoded strings.
- **Action Required**: Build a global Axios interceptor or Reducer middleware that parses HTTP error codes into user-friendly actionable messages (e.g., "Network timeout, please retry").