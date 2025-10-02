"""Vote processing test fixture format."""

from typing import ClassVar

from lean_spec.subspecs.containers.state.state import State
from lean_spec.subspecs.containers.vote import SignedVote

from .base import BaseConsensusFixture


class VoteProcessingTest(BaseConsensusFixture):
    """
    Test fixture for processing SignedVote objects.

    This fixture tests the processing of a single vote (attestation-like)
    against a pre-state, expecting either a valid post-state or an error.

    Structure:
        pre: Initial consensus state
        vote: The signed vote to process
        post: Expected state after processing (None if vote is invalid)

    Similar to consensus-specs' operations/attestation tests.
    """

    format_name: ClassVar[str] = "vote_processing_test"
    description: ClassVar[str] = "Tests processing of SignedVote objects"

    pre: State
    """The consensus state before processing the vote."""

    vote: SignedVote
    """The signed vote to process."""

    post: State | None
    """
    The expected state after processing.

    If None, the vote is expected to be invalid and processing should fail.
    """
