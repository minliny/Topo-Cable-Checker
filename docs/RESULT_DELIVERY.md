# Result Delivery Module

The **Result Delivery Module** sits within the Presentation layer and orchestrates the final presentation and delivery of checking results to the end-user.

## 1. Architectural Boundaries

- **`src/presentation/result_delivery.py`**: The main orchestrator (`ResultDeliveryService`). It formats DTOs from `CheckRunService` and `ResultQueryService` into user-friendly text (Markdown or Plain Text). It handles edge cases like missing summaries, empty issue lists, or negative max issue counts.
- **`src/crosscutting/clipboard.py`**: Provides a cross-platform (Windows/macOS/Linux) implementation for copying text to the clipboard.
- **`src/crosscutting/ide_launcher.py`**: Attempts to launch an IDE (PyCharm) for viewing result files, with an automatic fallback to the system's default text editor.
- **`src/crosscutting/temp_files.py`**: Safely creates timestamped result files in the operating system's standard temporary directory (`/tmp`, `%TEMP%`, etc.).

**Crucial Note**: The core formatting logic has no dependencies on the Domain or Infrastructure layer. The module fails gracefully (e.g., if the clipboard is unavailable, it logs a warning but allows the execution to finish successfully).

## 2. Testing Baseline

The module is covered by formal automated tests (`pytest`) in `tests/test_result_delivery.py`.
The tests cover:
- Markdown and Plain Text formatting outputs.
- Edge conditions (e.g., `max_issues <= 0`, empty inputs).
- Graceful degradation when subprocess calls (clipboard/IDE) fail.
- Temporary file creation success and cleanup.

Do **not** place manual testing scripts for Result Delivery in `tests/`. All exploratory test scripts belong in `scripts/manual/`.

## 3. Next Steps

If extending the Result Delivery module (e.g., adding Email, Slack, or Webhook integration):
1. Create new utilities in `src/crosscutting/` (if it's a general capability like an SMTP client) or `src/infrastructure/` (if it relies on specific API implementations).
2. Expand `ResultDeliveryService.deliver_result()` to accommodate new output modes.
3. Ensure to follow the strict "Do Not Block Main Flow" rule: delivery failures must only log warnings, not raise unhandled exceptions.
