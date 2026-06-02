# Export Paths and Writable Locations

## Context
In executable mode (PyInstaller), bundled resources are read-only and extracted under `sys._MEIPASS`.
Modelers need a clear, safe, and consistent location for export outputs (logs, screenshots, configs).

## Open Questions
- What is the official default export directory for executables?
- Should the path include the model name (e.g., `Documents/SGE/<ModelName>/`)?
- Should SGE provide a helper like `getWritablePath()`?
- How should existing APIs (`exportGameActionLogs`, layout config save/load) behave by default?

## Proposed Direction (TBD)
- Define a user-writable base directory (platform-specific).
- Provide a centralized helper for exports (read/write separation from resource paths).
- Update docs and examples once the default is decided.
