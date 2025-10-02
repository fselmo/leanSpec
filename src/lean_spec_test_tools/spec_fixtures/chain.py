"""Chain test fixture format."""

from typing import ClassVar, List

from lean_spec.subspecs.containers.block.block import SignedBlock
from lean_spec.subspecs.containers.state.state import State

from .base import BaseConsensusFixture


class ChainTest(BaseConsensusFixture):
    """
    Test fixture for multi-block chain validation.

    This fixture tests the sequential processing of multiple blocks,
    validating that the chain transitions correctly from pre-state
    through each block to the final post-state.

    Structure:
        pre: Initial consensus state
        blocks: Sequence of signed blocks to process
        post: Expected state after processing all blocks (None if chain is invalid)

    Similar to execution-spec-tests' BlockchainTest but for consensus layer.
    """

    format_name: ClassVar[str] = "chain_test"
    description: ClassVar[str] = "Tests multi-block chain validation"

    pre: State
    """The consensus state before processing the chain."""

    blocks: List[SignedBlock]
    """The sequence of signed blocks to process in order."""

    post: State | None
    """
    The expected state after processing all blocks.

    If None, the chain is expected to be invalid at some point and
    processing should fail.
    """
