---
type: community
cohesion: 1.00
members: 1
---

# Training Logger

**Cohesion:** 1.00 - tightly connected
**Members:** 1 nodes

## Members
- [[Flush and close all file handlers. Call before archiving the log file.]] - rationale - game/logger.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Training_Logger
SORT file.name ASC
```
