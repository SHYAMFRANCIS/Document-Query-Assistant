"""Tests for session manager utilities."""



import streamlit as st

from utils.session_manager import (
    add_message,
    clear_all,
    clear_messages,
    get_messages,
    get_recent_history,
    get_uploaded_files,
    initialize_session_state,
    remove_file,
)


class TestSessionManager:
    """Test session state management."""

    def setup_method(self):
        """Setup clean session state for each test."""
        # Mock streamlit session state
        if hasattr(st, 'session_state'):
            st.session_state.clear()
        else:
            st.session_state = {}

    def test_initialize_session_state(self):
        """Test session state initialization."""
        initialize_session_state()

        assert "uploaded_files" in st.session_state
        assert "messages" in st.session_state
        assert "selected_file" in st.session_state
        assert st.session_state.uploaded_files == {}
        assert st.session_state.messages == []

    def test_add_message(self):
        """Test adding a message to session state."""
        initialize_session_state()
        add_message("user", "Hello!")

        assert len(st.session_state.messages) == 1
        assert st.session_state.messages[0]["role"] == "user"
        assert st.session_state.messages[0]["content"] == "Hello!"

    def test_get_messages(self):
        """Test retrieving all messages."""
        initialize_session_state()
        add_message("user", "Question?")
        add_message("assistant", "Answer!")

        messages = get_messages()
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"

    def test_get_recent_history(self):
        """Test retrieving recent conversation history."""
        initialize_session_state()

        # Add 6 messages
        for i in range(6):
            add_message("user", f"Question {i}")
            add_message("assistant", f"Answer {i}")

        recent = get_recent_history(n=2)
        # Should get last 4 messages (2 exchanges)
        assert len(recent) == 4

    def test_clear_messages(self):
        """Test clearing all messages."""
        initialize_session_state()
        add_message("user", "Test")

        clear_messages()

        assert st.session_state.messages == []
        assert st.session_state.uploaded_files == {}  # Should not affect files

    def test_clear_all(self):
        """Test clearing all session state."""
        initialize_session_state()
        st.session_state.uploaded_files["test.pdf"] = "content"
        add_message("user", "Test")

        clear_all()

        assert st.session_state.uploaded_files == {}
        assert st.session_state.messages == []
        assert st.session_state.selected_file is None

    def test_remove_file(self):
        """Test removing a specific file."""
        initialize_session_state()
        st.session_state.uploaded_files["file1.pdf"] = "content1"
        st.session_state.uploaded_files["file2.pdf"] = "content2"
        st.session_state.selected_file = "file1.pdf"

        remove_file("file1.pdf")

        assert "file1.pdf" not in st.session_state.uploaded_files
        assert "file2.pdf" in st.session_state.uploaded_files
        # Should auto-select another file
        assert st.session_state.selected_file == "file2.pdf"

    def test_remove_selected_file_clears_selection(self):
        """Test removing selected file clears selection if no other files."""
        initialize_session_state()
        st.session_state.uploaded_files["only.pdf"] = "content"
        st.session_state.selected_file = "only.pdf"

        remove_file("only.pdf")

        assert st.session_state.uploaded_files == {}
        assert st.session_state.selected_file is None

    def test_get_uploaded_files(self):
        """Test retrieving uploaded files."""
        initialize_session_state()
        st.session_state.uploaded_files["doc.pdf"] = "PDF content"
        st.session_state.uploaded_files["report.docx"] = "DOCX content"

        files = get_uploaded_files()

        assert len(files) == 2
        assert "doc.pdf" in files
        assert files["doc.pdf"] == "PDF content"
