# Consensus Test Vector Implementation Plan for leanSpec

## Executive Summary

Implement a Pydantic + JSON test vector generation system for leanSpec consensus tests, using the proven architectural patterns from execution-spec-tests. This provides type-safe, git-diffable, developer-friendly test vectors for consensus clients.

## Core Design Decision: Pure JSON (No SSZ Compression)

**Rationale**: execution-spec-tests successfully uses pure JSON for fixtures up to **160MB** for edge cases. leanSpec's simplified 3SF consensus will have much smaller test vectors (typically 10-100KB, max ~10-50MB for edge cases).

**Benefits**:
- ✅ Fully git-diffable (even large tests)
- ✅ No SSZ library dependency for test consumption
- ✅ Type-safe with Pydantic throughout
- ✅ Human-readable debugging
- ✅ IDE autocomplete works
- ✅ Same developer experience as execution-spec-tests

## Test Formats for leanSpec Devnet-0

Based on current leanSpec capabilities, we can implement **4 test formats**:

### 1. VoteProcessingTest
**Tests**: Processing `SignedVote` objects (attestation-like)
**leanSpec has**: `Vote`, `SignedVote` containers
**Structure**:
```json
{
    "pre": {...},           // State (JSON)
    "vote": {...},          // SignedVote (JSON)
    "post": {...}           // Expected State (JSON), null if invalid
}
```
**Similar to**: consensus-specs' `operations/attestation`

### 2. ForkChoiceTest
**Tests**: Multi-step LMD GHOST fork choice scenarios
**leanSpec has**: `Store`, `get_fork_choice_head()`, vote tracking
**Structure**:
```json
{
    "anchor_state": {...},   // State (JSON)
    "anchor_block": {...},   // SignedBlock (JSON)
    "steps": [               // Array of steps (JSON)
        {"tick": 12},
        {"add_block": {...}},
        {"add_vote": {...}},
        {"checks": {"head": "0x...", "latest_justified": {...}}}
    ]
}
```
**Similar to**: consensus-specs' `fork_choice` tests

### 3. BlockProcessingTest
**Tests**: Processing `SignedBlock` objects
**leanSpec has**: `Block`, `SignedBlock`, `BlockBody`, `BlockHeader`
**Structure**:
```json
{
    "pre": {...},           // State (JSON)
    "block": {...},         // SignedBlock (JSON)
    "post": {...}           // Expected State (JSON), null if invalid
}
```
**Similar to**: consensus-specs' `sanity/blocks`

### 4. ChainTest
**Tests**: Multi-block chain validation
**leanSpec has**: Block containers, state tracking
**Structure**:
```json
{
    "pre": {...},           // State (JSON)
    "blocks": [{...}, {...}],  // Array of SignedBlock (JSON)
    "post": {...}           // Expected State (JSON), null if invalid
}
```
**Similar to**: execution-spec-tests' `BlockchainTest` but for consensus

## Architectural Patterns from execution-spec-tests

### 1. Auto-Registration System
```python
class BaseConsensusFixture(BaseModel):
    """Base for all consensus fixtures with auto-registration."""

    format_name: ClassVar[str] = ""
    formats: ClassVar[Dict[str, Type["BaseConsensusFixture"]]] = {}

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        """Auto-register fixture formats."""
        if cls.format_name:
            BaseConsensusFixture.formats[cls.format_name] = cls
```

### 2. JSON Serialization with Custom Encoders
```python
from ethereum_test_base_types import CamelModel

class ConsensusFixture(CamelModel):
    """CamelModel provides camelCase aliasing for JSON."""

    class Config:
        json_encoders = {
            bytes: lambda v: f"0x{v.hex()}",
            Bytes32: lambda v: f"0x{v.hex()}",
            # ... other custom encoders
        }
```

### 3. Fork Compatibility System
```python
class VoteProcessingTest(BaseConsensusFixture):

    @classmethod
    def supports_fork(cls, fork: str) -> bool:
        """Check if this format supports the given fork."""
        return fork in ["3sf", "devnet-0"]  # Extensible
```

### 4. Pytest Plugin Structure
Following execution-spec-tests patterns:
```
src/pytest_plugins/
├── consensus_filler/           # Generate JSON test vectors
│   ├── filler.py              # Main fixture generation
│   ├── pre_alloc.py           # Dynamic state/validator allocation
│   └── fixtures.py            # Pytest fixtures (pre, consensus_test)
├── consensus_consumer/         # Execute tests against clients
│   └── consumer.py
└── shared/                    # Common utilities
    └── helpers.py
```

### 5. Dynamic Allocation Pattern
```python
class ConsensusState:
    """Dynamic consensus state allocation (like execution's `pre` fixture)."""

    def __init__(self, node_id: str):
        self._validator_iterator = self._create_validator_iterator(node_id)
        self._state = State.generate_genesis(...)

    def fund_validator(self, balance: int = 32_000_000_000) -> ValidatorIndex:
        """Allocate validator dynamically (like pre.fund_eoa())."""
        validator_id = next(self._validator_iterator)
        # ... fund logic
        return validator_id

    def advance_to_slot(self, slot: Slot) -> None:
        """Advance state to target slot."""
        # ... slot transition logic
```

## Implementation Phases

### Phase 1: Foundation (Week 1)
**Goal**: Core Pydantic models and base infrastructure

**Tasks**:
1. Create directory structure:
   ```
   src/lean_spec_test_tools/
   ├── fixtures/
   │   ├── base.py                    # BaseConsensusFixture
   │   ├── vote_processing.py         # VoteProcessingTest
   │   ├── fork_choice.py             # ForkChoiceTest
   │   ├── block_processing.py        # BlockProcessingTest
   │   └── chain.py                   # ChainTest
   └── consensus_state.py             # Dynamic state allocation
   ```

2. Implement base classes:
   - `BaseConsensusFixture` with auto-registration
   - Custom JSON encoders for leanSpec types (Bytes32, Slot, etc.)
   - CamelCase aliasing (snake_case Python → camelCase JSON)

3. Implement all 4 fixture format classes with:
   - Pydantic models
   - Type validation
   - Fork compatibility markers

**Deliverables**:
- All fixture types defined with Pydantic
- Auto-registration working
- JSON serialization configured
- Type safety verified with MyPy

### Phase 2: Pytest Plugin System (Week 2)
**Goal**: Test generation infrastructure

**Tasks**:
1. Create pytest plugin structure:
   ```
   src/pytest_plugins/
   ├── consensus_filler/
   │   ├── __init__.py
   │   ├── filler.py              # Main plugin
   │   └── fixtures.py            # pre, consensus_test fixtures
   └── shared/
       └── helpers.py
   ```

2. Implement core fixtures:
   - `pre` fixture (ConsensusState with dynamic allocation)
   - `vote_test` fixture (VoteProcessingTest filler)
   - `fork_choice_test` fixture (ForkChoiceTest filler)
   - `block_test` fixture (BlockProcessingTest filler)
   - `chain_test` fixture (ChainTest filler)

3. Implement CLI command:
   - `lean-fill` command (like `uv run fill`)
   - Fork selection (`--fork=3sf`)
   - Output directory management
   - Clean flag (`--clean`)

**Deliverables**:
- Working pytest plugin system
- `lean-fill` command functional
- Test authoring patterns established
- Example tests written

### Phase 3: Test Authoring (Week 3)
**Goal**: Write actual consensus tests using the framework

**Tasks**:
1. Create test directory structure:
   ```
   tests/
   ├── vote_processing/
   │   ├── test_valid_vote.py
   │   └── test_invalid_vote.py
   ├── fork_choice/
   │   ├── test_basic_fork_choice.py
   │   └── test_reorg.py
   ├── block_processing/
   │   └── test_valid_block.py
   └── chain/
       └── test_multi_block.py
   ```

2. Write example tests for each format:
   - Vote processing tests
   - Fork choice scenarios
   - Block validation tests
   - Multi-block chain tests

3. Generate fixtures:
   ```bash
   uv run lean-fill --fork=3sf tests/ --clean -v
   ```

**Deliverables**:
- Working test examples for all 4 formats
- Generated JSON fixtures in `fixtures/` directory
- Test authoring documentation

### Phase 4: Client Consumption (Week 4)
**Goal**: Enable clients to consume test vectors

**Tasks**:
1. Implement `lean-consume` command:
   - Load JSON fixtures
   - Execute against leanSpec implementation
   - Report results

2. Create validation utilities:
   - JSON schema export
   - Fixture validation
   - Format verification

3. Documentation:
   - Test authoring guide
   - Fixture format specification
   - Client integration guide

**Deliverables**:
- `lean-consume` command working
- Validation tooling complete
- Comprehensive documentation

## Test Writing Patterns

### Example: Vote Processing Test
```python
def test_valid_vote(pre: ConsensusState, vote_test: VoteProcessingTestFiller):
    """Test processing a valid vote."""

    # Dynamic allocation - no hardcoded values
    validator = pre.fund_validator()

    # Create vote
    vote = pre.create_vote(
        validator_id=validator,
        slot=Slot(1),
        head=pre.latest_justified,
        target=pre.latest_justified,
        source=pre.latest_finalized
    )

    # Sign vote
    signed_vote = pre.sign_vote(vote)

    # Generate test
    vote_test(
        pre=pre,
        vote=signed_vote,
        expected_valid=True
    )
```

### Example: Fork Choice Test
```python
def test_fork_choice_reorg(pre: ConsensusState, fork_choice_test: ForkChoiceTestFiller):
    """Test fork choice reorg scenario."""

    validators = pre.allocate_validators(count=10)

    steps = [
        pre.advance_to_slot(1),
        pre.add_block("block_a", parent=pre.genesis_block),
        pre.add_votes_for_block("block_a", validators[:5]),
        pre.check_head(expected="block_a"),

        pre.advance_to_slot(2),
        pre.add_block("block_b", parent=pre.genesis_block),
        pre.add_votes_for_block("block_b", validators[:8]),
        pre.check_head(expected="block_b"),  # Reorg!
    ]

    fork_choice_test(
        anchor_state=pre.state,
        anchor_block=pre.genesis_block,
        steps=steps
    )
```

### Example: Chain Test
```python
def test_multi_block_chain(pre: ConsensusState, chain_test: ChainTestFiller):
    """Test multi-block chain validation."""

    blocks = []
    for slot in range(1, 5):
        pre.advance_to_slot(Slot(slot))
        block = pre.build_block()
        signed_block = pre.sign_block(block)
        blocks.append(signed_block)

    chain_test(
        pre=pre,
        blocks=blocks,
        expected_valid=True
    )
```

## File Organization

### Output Structure
```
fixtures/
└── consensus/
    ├── 3sf/                           # Fork name
    │   ├── vote_processing/           # Test category
    │   │   └── valid_vote/            # Test suite
    │   │       └── test_001.json      # Test case (JSON fixture)
    │   ├── fork_choice/
    │   │   ├── basic/
    │   │   │   └── test_001.json
    │   │   └── reorg/
    │   │       └── test_001.json
    │   ├── block_processing/
    │   │   └── valid_block/
    │   │       └── test_001.json
    │   └── chain/
    │       └── multi_block/
    │           └── test_001.json
    └── devnet-0/
        └── ...
```

### Fixture Format Example (VoteProcessingTest)
```json
{
  "vote_processing_test": {
    "testId": "test_valid_vote",
    "fork": "3sf",
    "description": "Test processing a valid vote",
    "pre": {
      "config": {...},
      "slot": "0x01",
      "latestBlockHeader": {...},
      "latestJustified": {"epoch": "0x00", "root": "0x..."},
      "latestFinalized": {"epoch": "0x00", "root": "0x..."},
      "historicalBlockHashes": ["0x...", "0x..."],
      "justifiedSlots": "0xff",
      "justificationsRoots": ["0x...", "0x..."],
      "justificationsValidators": "0xffff"
    },
    "vote": {
      "data": {
        "validatorId": "0x00",
        "slot": "0x01",
        "head": {"epoch": "0x00", "root": "0x..."},
        "target": {"epoch": "0x00", "root": "0x..."},
        "source": {"epoch": "0x00", "root": "0x..."}
      },
      "signature": "0x..."
    },
    "post": {
      "config": {...},
      "slot": "0x01",
      // ... updated state
    }
  }
}
```

## Key Differences from consensus-specs

| Aspect | consensus-specs | leanSpec (New) |
|--------|----------------|----------------|
| **Format** | YAML + SSZ-snappy | Pure JSON |
| **Type Safety** | None (YAML) | Full (Pydantic) |
| **Test Generation** | Yield-based generators | Pytest fixtures + fillers |
| **Dev Experience** | Manual YAML editing | IDE autocomplete, type hints |
| **State Allocation** | Manual/hardcoded | Dynamic (like execution-spec-tests) |
| **Git Diffs** | Binary SSZ files | Human-readable JSON |
| **Size** | Compressed (~100KB-5MB) | Uncompressed (~10KB-50MB) |

## Success Criteria

### Technical
- ✅ All 4 fixture formats implemented with Pydantic
- ✅ Type safety verified with MyPy (no type errors)
- ✅ Auto-registration system working
- ✅ Dynamic state allocation (no hardcoded values)
- ✅ JSON fixtures generate correctly
- ✅ `lean-fill` command functional

### Developer Experience
- ✅ IDE autocomplete works for all fixture types
- ✅ Test authoring feels natural (like execution-spec-tests)
- ✅ Clear error messages from Pydantic validation
- ✅ Git diffs show meaningful changes

### Ecosystem
- ✅ Fixtures compatible with leanSpec implementation
- ✅ Documentation covers all test formats
- ✅ Example tests for each category
- ✅ Client consumption tooling ready

## Next Steps

1. **Review this plan** - ensure alignment on approach
2. **Begin Phase 1** - implement base Pydantic models
3. **Iterate quickly** - small PRs, frequent feedback
4. **Expand gradually** - add more formats as leanSpec evolves (epoch processing, rewards, etc.)

## Future Extensions

As leanSpec adds more functionality, we can add:
- **EpochProcessingTest** (when epoch transitions implemented)
- **ValidatorLifecycleTest** (when activation/exit added)
- **RewardsTest** (when reward calculation added)
- **SlashingTest** (when slashing implemented)
- **SyncTest** (when sync protocol added)

The framework is designed to be extensible - new formats just inherit from `BaseConsensusFixture` and auto-register.

## References

- **execution-spec-tests patterns**: `/Users/fselmo/codigo/e/py/execution-spec-tests/src/ethereum_test_fixtures/`
- **consensus-specs formats**: `/Users/fselmo/codigo/e/py/consensus-specs/tests/formats/`
- **leanSpec implementation**: `/Users/fselmo/codigo/e/py/leanSpec/src/lean_spec/`
- **Design document**: `/Users/fselmo/codigo/e/py/leanSpec/CONSENSUS_TESTING_DESIGN.md`