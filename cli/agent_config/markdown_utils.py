# cli/agent_config/markdown_utils.py
import logging
import re
from pathlib import Path
from typing import List, Optional, Tuple

from pydantic import ValidationError

from cli import constants  # Corrected import path
from .models import AgentConfig

# Get a logger for this module
logger = logging.getLogger(__name__)

# --- Constants ---
ROLE_DEFINITION_HEADINGS = [
    constants.MD_HEADING_CORE_ID,
    constants.MD_HEADING_PERSONA,
    constants.MD_HEADING_ROLE,
]
# List of headings that signify the start of a custom instructions section
CUSTOM_INSTRUCTIONS_HEADINGS = [
    constants.MD_HEADING_CUSTOM_INSTRUCTIONS,
    constants.MD_HEADING_MODE_INSTRUCTIONS,
    constants.MD_HEADING_SOP,
]
HEADING_PATTERN = re.compile(r"^\s*(#+)\s+(.*)", re.MULTILINE)

# --- Helper Functions ---


def _find_section(
    content: str, start_headings: List[str], start_offset: int = 0
) -> Optional[Tuple[str, int, int]]:
    """
    Finds the first occurrence of any start_heading from the offset
    and returns the full section content including the heading, its start index, and its end index.
    The section ends before the next heading of the same or lower level, or EOF.
    """
    best_match_start_index = -1
    logger.debug(
        f"Entering _find_section with start_headings={start_headings}, start_offset={start_offset}"
    )
    found_heading = None

    # Find the earliest occurrence of any of the start headings
    for heading in start_headings:
        try:
            current_start_index = content.index(heading, start_offset)
            if (
                best_match_start_index == -1
                or current_start_index < best_match_start_index
            ):
                best_match_start_index = current_start_index
                found_heading = heading
        except ValueError:
            continue  # Heading not found

    if best_match_start_index == -1:
        logger.debug(
            f"No start heading found from {start_headings} after offset {start_offset}."
        )
        return None  # No start heading found

    # Determine the level of the found heading
    heading_match = HEADING_PATTERN.match(content[best_match_start_index:])
    if not heading_match:
        # This should ideally not happen if the heading was found by index, but safeguard anyway
        logger.warning(
            f"Could not parse heading level for found heading: '{found_heading}'"
        )
        start_level = heading.count("#")  # Fallback to counting '#'
    else:
        start_level = len(heading_match.group(1))
    logger.debug(
        f"Found heading '{found_heading}' at index {best_match_start_index} with level {start_level}."
    )

    # Find the end of the section
    end_index = len(content)
    # Assert found_heading is not None to satisfy mypy
    assert found_heading is not None, "Internal logic error: found_heading is None despite valid start index"
    content_start_after_heading = best_match_start_index + len(found_heading)

    # Look for the *first* heading after the found heading to mark the end
    first_heading_after_start = HEADING_PATTERN.search(
        content, content_start_after_heading
    )
    if first_heading_after_start:
        end_index = first_heading_after_start.start()
        logger.debug(
            f"Found next heading '{first_heading_after_start.group(2)}' at index {end_index}. Ending section."
        )
    # Note: If no heading is found after the start, end_index remains len(content)

    section_content = content[best_match_start_index:end_index].strip()
    logger.debug(
        f"Section content extracted from index {best_match_start_index} to {end_index}."
    )
    logger.debug(
        f"Exiting _find_section. Found section: {section_content[:50]}..."
    )
    return section_content, best_match_start_index, end_index


def parse_markdown(markdown_path: Path) -> AgentConfig:
    """Parses an agent Markdown file and returns an AgentConfig object."""
    logger.debug(
        f"Entering parse_markdown with markdown_path='{markdown_path}'"
    )
    if not markdown_path.is_file():
        raise FileNotFoundError(f"Markdown file not found: {markdown_path}")

    logger.info(f"Parsing Markdown file: {markdown_path}")
    logger.debug(f"Reading content from: {markdown_path}")
    content = markdown_path.read_text(encoding="utf-8")
    logger.debug(f"Read {len(content)} characters from file.")

    # Extract slug from parent directory
    slug = markdown_path.parent.name
    if not slug:
        raise ValueError(
            f"Could not determine slug from path: {markdown_path}"
        )
    logger.debug(f"Extracted slug: '{slug}'")

    # Extract name from first H1 (more robust regex)
    name_match = re.search(r"^\s*#\s+(.*)", content, re.MULTILINE)
    if not name_match:
        raise ValueError(
            f"Could not find H1 heading for 'name' in: {markdown_path}"
        )
    name = name_match.group(1).strip()
    logger.debug(f"Extracted name: '{name}'")

    # Extract roleDefinition (first match of specified headings)
    role_section_result = _find_section(
        content, ROLE_DEFINITION_HEADINGS
    )  # Uses updated constant list
    if not role_section_result:
        raise ValueError(
            f"Could not find any role definition heading ({', '.join(constants.ROLE_DEFINITION_HEADINGS)}) in: {markdown_path}"
        )
    role_definition, _, _ = role_section_result
    logger.debug(
        f"Extracted roleDefinition (length {len(role_definition)}) starting with: {role_definition[:50]}..."
    )

    # Extract and concatenate customInstructions (all matches)
    custom_instructions_list = []
    current_offset = 0
    while True:
        instruction_section_result = _find_section(
            content, CUSTOM_INSTRUCTIONS_HEADINGS, start_offset=current_offset
        )
        if not instruction_section_result:
            logger.debug("No more custom instruction sections found.")
            break
        section_content, start_idx, end_idx = instruction_section_result
        custom_instructions_list.append(section_content)
        current_offset = (
            end_idx  # Start next search after the current section ends
        )

    custom_instructions_final = None
    if custom_instructions_list:
        logger.debug(
            f"Found {len(custom_instructions_list)} custom instruction section(s). Concatenating."
        )
        # Concatenate: keep heading of the first, append content of the rest
        first_section = custom_instructions_list[0]
        concatenated_parts = [first_section]

        for subsequent_section in custom_instructions_list[1:]:
            # Find the end of the heading line in the subsequent section
            heading_line_end = subsequent_section.find("\n")
            if heading_line_end != -1:
                content_part = subsequent_section[
                    heading_line_end + 1 :
                ].strip()
                if (
                    content_part
                ):  # Only append if there's actual content after the heading
                    concatenated_parts.append(content_part)
            # else: If no newline, it's just a heading, ignore content part

        custom_instructions_final = "\n\n".join(concatenated_parts).strip()
        logger.debug(
            f"Final customInstructions (length {len(custom_instructions_final)}) starting with: {custom_instructions_final[:50]}..."
        )
    else:
        logger.debug("No custom instruction sections found.")

    try:
        config_data = {
            constants.SLUG: slug,
            constants.NAME: name,
            constants.ROLE_DEFINITION: role_definition,
        }
        if custom_instructions_final:
            config_data[constants.CUSTOM_INSTRUCTIONS] = custom_instructions_final

        logger.debug(
            f"Attempting to validate and create AgentConfig for slug '{slug}'."
        )
        # Use model_validate for Pydantic v2 compatibility and clarity
        agent_config = AgentConfig.model_validate(config_data)
        logger.info(
            f"Successfully parsed and validated AgentConfig for slug: {slug}"
        )
        logger.debug(f"Exiting parse_markdown (success) for slug '{slug}'")
        return agent_config
    except ValidationError as e:
        logger.error(
            f"Pydantic validation error creating AgentConfig for {markdown_path}: {e}"
        )
        raise ValueError(
            f"Validation error creating AgentConfig for {markdown_path}: {e}"
        )
