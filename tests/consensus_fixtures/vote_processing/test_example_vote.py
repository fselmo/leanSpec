"""Example vote processing test to demonstrate fixture generation."""

from lean_spec.subspecs.containers.checkpoint import Checkpoint
from lean_spec.subspecs.containers.slot import Slot
from lean_spec.subspecs.containers.state.state import State
from lean_spec.subspecs.containers.vote import SignedVote, Vote
from lean_spec.types import Bytes32, Uint64


def test_simple_vote(vote_test):  # type: ignore[no-untyped-def]
    """Test processing a simple valid vote."""
    # Create genesis state
    state = State.generate_genesis(
        genesis_time=Uint64(1000),
        num_validators=Uint64(10),
    )

    # Create a checkpoint
    checkpoint = Checkpoint(root=Bytes32.zero(), slot=Slot(0))

    # Create a vote
    vote = Vote(
        validator_id=Uint64(0),
        slot=Slot(1),
        head=checkpoint,
        target=checkpoint,
        source=checkpoint,
    )

    # Sign the vote (placeholder signature)
    signed_vote = SignedVote(
        data=vote,
        signature=Bytes32.zero(),
    )

    # Generate fixture
    # In a real implementation, we'd use the spec to process the vote
    # For now, we just create a fixture with pre/post states
    vote_test(
        pre=state,
        vote=signed_vote,
        post=state,  # For now, no state changes
        description="Test processing a simple valid vote",
    )


def test_invalid_vote(vote_test):  # type: ignore[no-untyped-def]
    """Test processing an invalid vote."""
    # Create genesis state
    state = State.generate_genesis(
        genesis_time=Uint64(1000),
        num_validators=Uint64(10),
    )

    # Create a checkpoint
    checkpoint = Checkpoint(root=Bytes32.zero(), slot=Slot(0))

    # Create an invalid vote (validator doesn't exist)
    vote = Vote(
        validator_id=Uint64(999),  # Invalid validator
        slot=Slot(1),
        head=checkpoint,
        target=checkpoint,
        source=checkpoint,
    )

    # Sign the vote
    signed_vote = SignedVote(
        data=vote,
        signature=Bytes32.zero(),
    )

    # Generate fixture (expect invalid)
    vote_test(
        pre=state,
        vote=signed_vote,
        post=None,  # Expect failure
        description="Test processing an invalid vote from non-existent validator",
    )
