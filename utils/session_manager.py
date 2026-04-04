"""Session state management utilities for Streamlit."""

from typing import Dict, List

import streamlit as st


def initialize_session_state() -> None:
    """Initialize all session state variables if they don't exist."""
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = {}  # dict mapping filename -> text
    if "messages" not in st.session_state:
        st.session_state.messages = []  # list of chat messages
    if "selected_file" not in st.session_state:
        st.session_state.selected_file = None  # currently selected document


def add_message(role: str, content: str) -> None:
    """
    Add a message to the chat history.

    Args:
        role: Message role ("user" or "assistant").
        content: Message content.
    """
    st.session_state.messages.append({"role": role, "content": content})


def get_messages() -> List[Dict[str, str]]:
    """
    Get all chat messages.

    Returns:
        List of message dictionaries with 'role' and 'content' keys.
    """
    return st.session_state.messages


def get_recent_history(n: int = 5) -> List[Dict[str, str]]:
    """
    Get the most recent n message exchanges (user + assistant pairs).

    Args:
        n: Number of recent exchanges to retrieve.

    Returns:
        List of recent message dictionaries.
    """
    # Get last 2*n messages to get n exchanges (user + assistant)
    return st.session_state.messages[-(n * 2):] if st.session_state.messages else []


def clear_messages() -> None:
    """Clear all chat messages but keep uploaded files."""
    st.session_state.messages = []


def clear_all() -> None:
    """Clear both uploaded files and messages."""
    st.session_state.uploaded_files = {}
    st.session_state.messages = []
    st.session_state.selected_file = None


def remove_file(filename: str) -> None:
    """
    Remove a specific file from uploaded files.

    Args:
        filename: Name of the file to remove.
    """
    if filename in st.session_state.uploaded_files:
        del st.session_state.uploaded_files[filename]
        # If the removed file was selected, clear selection
        if st.session_state.selected_file == filename:
            st.session_state.selected_file = None
            # Auto-select another file if available
            if st.session_state.uploaded_files:
                st.session_state.selected_file = next(iter(st.session_state.uploaded_files.keys()))


def get_uploaded_files() -> Dict[str, str]:
    """
    Get all uploaded files.

    Returns:
        Dictionary mapping filenames to their extracted text content.
    """
    return st.session_state.uploaded_files
