"""Fork choice test fixture format."""

from typing import Any, ClassVar, Dict, List

from lean_spec.subspecs.containers.block.block import SignedBlock
from lean_spec.subspecs.containers.state.state import State

from .base import BaseConsensusFixture


class ForkChoiceTest(BaseConsensusFixture):
    """
    Test fixture for multi-step LMD GHOST fork choice scenarios.

    This fixture tests fork choice logic through a series of operations
    that modify the store state (time ticks, block additions, votes).
    Each step can optionally include checks to verify expected state.

    Structure:
        anchor_state: Initial trusted state
        anchor_block: Initial trusted block
        steps: Sequence of operations and checks

    Step types:
        - tick: Advance time
        - add_block: Add a block to the store
        - add_vote: Process a vote
        - checks: Verify fork choice head and checkpoints

    Similar to consensus-specs' fork_choice tests.
    """

    format_name: ClassVar[str] = "fork_choice_test"
    description: ClassVar[str] = "Tests multi-step LMD GHOST fork choice scenarios"

    anchor_state: State
    """The initial trusted consensus state."""

    anchor_block: SignedBlock
    """The initial trusted block."""

    steps: List[Dict[str, Any]]
    """
    Sequence of operations to perform.

    Each step is a dictionary with one of the following keys:
    - "tick": Advance time by this many intervals (value: Uint64)
    - "add_block": Add a block to the store (value: SignedBlock)
    - "add_vote": Process a vote (value: SignedVote)
    - "checks": Verify expected state (value: dict with "head", "latest_justified", etc.)

    Example:
        [
            {"tick": 12},
            {"add_block": {...}},
            {"add_vote": {...}},
            {"checks": {"head": "0x...", "latest_justified": {...}}}
        ]
    """
