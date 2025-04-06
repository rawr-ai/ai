from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field

class EntryType(str, Enum):
    """Enumeration for the type of entry."""
    DEVLOG = "devlog"
    JOURNAL = "journal"
    SYSTEM_EVENT = "system_event"
    USER_NOTE = "user_note"
    AGENT_TRACE = "agent_trace"
    GENERIC = "generic" # Default or fallback

class LogLevel(str, Enum):
    """Enumeration for log severity levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING" # Common alias for WARN
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    FATAL = "FATAL" # Sometimes used interchangeably with CRITICAL

class Entry(BaseModel):
    """
    Represents a single log entry, journal record, system event, or other discrete piece of information
    captured over time. It serves as a fundamental unit for recording observations, actions, or states
    from various sources like development logs, user journals, or system outputs.

    Extraction Instructions for AI:

    1.  **Identify Discrete Entries:** Segment the source text (e.g., log file, journal document) into
        individual entries. This could be line-based for typical logs or paragraph/section-based for journals.

    2.  **Extract `timestamp`:**
        *   Look for explicit date and time information associated with the entry.
        *   Recognize common formats (e.g., ISO 8601 'YYYY-MM-DDTHH:MM:SS', 'YYYY-MM-DD HH:MM:SS', 'Mon DD HH:MM:SS YYYY').
        *   If only a date is present, consider using a default time (e.g., midnight) or marking it as date-only if the schema were adapted. This field is mandatory.
        *   Convert the extracted string to a Python `datetime` object.

    3.  **Extract `source`:**
        *   Determine the origin of the entry. This could be:
            *   The filename of the log file (e.g., 'app.log', 'devlog_2025-04-06.md').
            *   An application or module name if specified within the entry (e.g., 'AuthService', 'DataProcessor').
            *   A user ID or agent name if the entry represents their input or action.
        *   If the source is ambiguous, use a sensible default like the input document's name or 'unknown'. This field is mandatory.

    4.  **Extract `content`:**
        *   Capture the primary textual message or description of the entry.
        *   Exclude metadata already captured in other fields (like timestamp, level, source) unless it's intrinsically part of the message. This field is mandatory.

    5.  **Extract `entry_type`:**
        *   Classify the entry based on its context or explicit labels.
        *   Use the `EntryType` enum values (DEVLOG, JOURNAL, SYSTEM_EVENT, USER_NOTE, AGENT_TRACE, GENERIC).
        *   Infer from the source (e.g., files in `devlogs/` are likely `DEVLOG`).
        *   Look for keywords in the content or surrounding text.
        *   Default to `GENERIC` if the type cannot be reliably determined. This field is mandatory.

    6.  **Extract `level` (Optional):**
        *   Look for explicit logging level indicators (e.g., 'INFO', 'WARN', 'ERROR', 'DEBUG', 'CRITICAL', 'FATAL').
        *   Match these against the `LogLevel` enum values. Handle variations (e.g., 'Warning' -> WARN/WARNING).
        *   If no level indicator is found or applicable (e.g., for a journal entry), leave this field as `None`.

    7.  **Extract `tags` (Optional):**
        *   Identify keywords, hashtags (e.g., '#project-alpha', '#bugfix'), or explicit metadata tags associated with the entry.
        *   Collect these into a list of strings.
        *   If no tags are found, leave this field as `None`.
    """
    timestamp: datetime = Field(..., description="The date and time when the entry was recorded or occurred.")
    source: str = Field(..., description="Identifier for the origin of the entry (e.g., filename, application name, module, user ID).")
    content: str = Field(..., description="The main textual content of the entry.")
    entry_type: EntryType = Field(..., description="The classification or category of the entry.")
    level: Optional[LogLevel] = Field(default=None, description="The severity level, typically for log entries (e.g., INFO, WARN, ERROR).")
    tags: Optional[List[str]] = Field(default=None, description="Optional list of keywords or tags associated with the entry.")

    class Config:
        use_enum_values = True # Store enum values as strings