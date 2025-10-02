"""Pytest fixtures for consensus test generation."""

from typing import Any, Callable

import pytest

from lean_spec_test_tools.spec_fixtures import (
    BlockProcessingTest,
    ChainTest,
    VoteProcessingTest,
)


@pytest.fixture
def fork(request: pytest.FixtureRequest) -> str:
    """Get the fork being tested."""
    return request.config.consensus_fork  # type: ignore[attr-defined,no-any-return]


@pytest.fixture
def vote_test(
    request: pytest.FixtureRequest,
    fork: str,
) -> Callable[..., None]:
    """
    Fixture for generating vote processing test vectors.

    Returns a callable that accepts test parameters and generates a fixture.
    """

    def _create_vote_test(**kwargs: Any) -> None:
        """
        Create a vote processing test fixture.

        Args:
            **kwargs: Test parameters including:
                - pre: Initial State
                - vote: SignedVote to process
                - post: Expected State after processing (None if invalid)
                - description: Test description
        """
        # Extract parameters
        pre_state = kwargs["pre"]
        vote = kwargs["vote"]
        post_state = kwargs.get("post", None)
        description = kwargs.get("description", "")

        # Create fixture
        fixture = VoteProcessingTest(
            pre=pre_state,
            vote=vote,
            post=post_state,
        )

        # Fill info
        fixture.fill_info(
            test_id=request.node.name,
            fork=fork,
            description=description,
        )

        # Add to collector
        # Use complete nodeid for test identification (execution-spec-tests pattern)
        request.config.fixture_collector.add_fixture(  # type: ignore[attr-defined]
            test_name=request.node.name,
            fixture_format=fixture.format_name,
            fixture=fixture,
            test_nodeid=request.node.nodeid,
        )

    return _create_vote_test


@pytest.fixture
def block_test(
    request: pytest.FixtureRequest,
    fork: str,
) -> Callable[..., None]:
    """
    Fixture for generating block processing test vectors.

    Returns a callable that accepts test parameters and generates a fixture.
    """

    def _create_block_test(**kwargs: Any) -> None:
        """
        Create a block processing test fixture.

        Args:
            **kwargs: Test parameters including:
                - pre: Initial State
                - block: SignedBlock to process
                - post: Expected State after processing (None if invalid)
                - description: Test description
        """
        # Extract parameters
        pre_state = kwargs["pre"]
        block = kwargs["block"]
        post_state = kwargs.get("post", None)
        description = kwargs.get("description", "")

        # Create fixture
        fixture = BlockProcessingTest(
            pre=pre_state,
            block=block,
            post=post_state,
        )

        # Fill info
        fixture.fill_info(
            test_id=request.node.name,
            fork=fork,
            description=description,
        )

        # Add to collector
        # Use complete nodeid for test identification (execution-spec-tests pattern)
        request.config.fixture_collector.add_fixture(  # type: ignore[attr-defined]
            test_name=request.node.name,
            fixture_format=fixture.format_name,
            fixture=fixture,
            test_nodeid=request.node.nodeid,
        )

    return _create_block_test


@pytest.fixture
def chain_test(
    request: pytest.FixtureRequest,
    fork: str,
) -> Callable[..., None]:
    """
    Fixture for generating chain test vectors.

    Returns a callable that accepts test parameters and generates a fixture.
    """

    def _create_chain_test(**kwargs: Any) -> None:
        """
        Create a chain test fixture.

        Args:
            **kwargs: Test parameters including:
                - pre: Initial State
                - blocks: List of SignedBlock to process
                - post: Expected State after processing (None if invalid)
                - description: Test description
        """
        # Extract parameters
        pre_state = kwargs["pre"]
        blocks = kwargs["blocks"]
        post_state = kwargs.get("post", None)
        description = kwargs.get("description", "")

        # Create fixture
        fixture = ChainTest(
            pre=pre_state,
            blocks=blocks,
            post=post_state,
        )

        # Fill info
        fixture.fill_info(
            test_id=request.node.name,
            fork=fork,
            description=description,
        )

        # Add to collector
        # Use complete nodeid for test identification (execution-spec-tests pattern)
        request.config.fixture_collector.add_fixture(  # type: ignore[attr-defined]
            test_name=request.node.name,
            fixture_format=fixture.format_name,
            fixture=fixture,
            test_nodeid=request.node.nodeid,
        )

    return _create_chain_test
