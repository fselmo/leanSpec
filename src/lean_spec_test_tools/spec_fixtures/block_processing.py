"""Block processing test fixture format."""

from typing import ClassVar

from lean_spec.subspecs.containers.block.block import SignedBlock
from lean_spec.subspecs.containers.state.state import State

from .base import BaseConsensusFixture


class BlockProcessingTest(BaseConsensusFixture):
    """
    Test fixture for processing SignedBlock objects.

    This fixture tests the processing of a single block against a pre-state,
    expecting either a valid post-state or an error.

    Structure:
        pre: Initial consensus state
        block: The signed block to process
        post: Expected state after processing (None if block is invalid)

    Similar to consensus-specs' sanity/blocks tests.
    """

    format_name: ClassVar[str] = "block_processing_test"
    description: ClassVar[str] = "Tests processing of SignedBlock objects"

    pre: State
    """The consensus state before processing the block."""

    block: SignedBlock
    """The signed block to process."""

    post: State | None
    """
    The expected state after processing.

    If None, the block is expected to be invalid and processing should fail.
    """
