"""Stream handler for wetwire-core integration.

Provides streaming output support for long-running operations.
"""

from io import StringIO
from typing import TextIO


class StreamHandler:
    """Handler for streaming output during workflow operations.

    Captures output that can be streamed to clients or written to files.
    """

    def __init__(self, output_stream: TextIO | None = None):
        """Initialize stream handler.

        Args:
            output_stream: Optional output stream to write to.
                          If None, captures to internal buffer.
        """
        self._buffer = StringIO()
        self._output_stream = output_stream

    def write(self, content: str) -> None:
        """Write content to the stream.

        Args:
            content: Content to write
        """
        self._buffer.write(content)
        if self._output_stream is not None:
            self._output_stream.write(content)
            self._output_stream.flush()

    def writeln(self, content: str = "") -> None:
        """Write content followed by newline.

        Args:
            content: Content to write
        """
        self.write(content + "\n")

    def get_output(self) -> str:
        """Get all captured output.

        Returns:
            All content written to the stream
        """
        return self._buffer.getvalue()

    def clear(self) -> None:
        """Clear the internal buffer."""
        self._buffer = StringIO()


def create_stream_handler(output_stream: TextIO | None = None) -> StreamHandler:
    """Create a new stream handler.

    Args:
        output_stream: Optional output stream to write to

    Returns:
        StreamHandler instance
    """
    return StreamHandler(output_stream)
