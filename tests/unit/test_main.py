"""Test for main application entry point."""

from unittest.mock import patch

from job_agent.main import main


def test_main_function():
    """Test that main function executes without error."""
    # Mock both print and uvicorn.run to prevent actually starting the server
    with patch("builtins.print") as mock_print, patch("uvicorn.run") as mock_uvicorn:
        main()

        # Verify that print was called (indicating the function executed)
        assert mock_print.call_count > 0

        # Check that the first print call contains our app name
        first_call_args = mock_print.call_args_list[0][0]
        assert "Job Agent" in first_call_args[0]

        # Verify uvicorn.run was called
        assert mock_uvicorn.called
