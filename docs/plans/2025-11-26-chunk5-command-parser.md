# Chunk 5: Command Parser Integration - TDD Implementation Plan

**Goal:** Connect compiled vocabulary tables to runtime command parsing
**Approach:** TDD with Red-Green-Refactor cycle

---

## Architecture Overview

```
Player Input: "put the brass lamp in wooden case"
     │
     ▼
┌─────────────────────────────────────────────────────┐
│  CommandLexer                                       │
│  - Tokenize input into words                        │
│  - Filter BUZZ words (THE, A, AN)                   │
│  - Apply SYNONYM mappings                           │
│  Output: ["PUT", "BRASS", "LAMP", "IN", "WOODEN", "CASE"]
└─────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────┐
│  CommandParser                                      │
│  - Extract verb                                     │
│  - Identify noun phrases (adj + noun)              │
│  - Identify prepositions                           │
│  Output: ParsedCommand(verb="PUT", objects=[...], prep="IN")
└─────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────┐
│  SyntaxMatcher                                      │
│  - Match against SYNTAX table                      │
│  - Check object count and preposition              │
│  Output: SyntaxEntry(action="V-PUT", preaction=...)
└─────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────┐
│  ObjectResolver                                     │
│  - Resolve noun phrases to game objects            │
│  - Check visibility/accessibility                  │
│  - Handle disambiguation ("Which one?")            │
│  Output: [lamp_obj, case_obj]
└─────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────┐
│  ParserState                                        │
│  - Set PRSA = V-PUT                                │
│  - Set PRSO = lamp object                          │
│  - Set PRSI = case object                          │
└─────────────────────────────────────────────────────┘
```

---

## Task Breakdown

### Task 5.1: Token Dataclass
**Goal:** Define data structures for parsed commands

**Test Cases:**
```python
def test_token_basic():
    """Token stores word and type."""
    token = Token("LAMP", TokenType.NOUN)
    assert token.word == "LAMP"
    assert token.type == TokenType.NOUN

def test_parsed_command_basic():
    """ParsedCommand stores command structure."""
    cmd = ParsedCommand(verb="TAKE", noun_phrases=[...])
    assert cmd.verb == "TAKE"

def test_noun_phrase_with_adjective():
    """NounPhrase stores adjective and noun."""
    np = NounPhrase(adjectives=["BRASS"], noun="LAMP")
    assert np.adjectives == ["BRASS"]
    assert np.noun == "LAMP"
```

**Implementation:**
- Token dataclass with word, type
- TokenType enum (VERB, NOUN, ADJECTIVE, PREPOSITION, DIRECTION, UNKNOWN)
- NounPhrase dataclass with adjectives and noun
- ParsedCommand dataclass with verb, noun_phrases, preposition

---

### Task 5.2: CommandLexer - Basic Tokenization
**Goal:** Tokenize input strings into word tokens

**Test Cases:**
```python
def test_lexer_simple_word():
    """Lexer tokenizes single word."""
    lexer = CommandLexer(directive_processor)
    tokens = lexer.tokenize("take")
    assert len(tokens) == 1
    assert tokens[0].word == "TAKE"

def test_lexer_multiple_words():
    """Lexer tokenizes multiple words."""
    tokens = lexer.tokenize("take brass lamp")
    assert len(tokens) == 3

def test_lexer_handles_punctuation():
    """Lexer strips punctuation."""
    tokens = lexer.tokenize("take lamp.")
    assert tokens[-1].word == "LAMP"

def test_lexer_normalizes_case():
    """Lexer converts to uppercase."""
    tokens = lexer.tokenize("Take LAMP")
    assert all(t.word == t.word.upper() for t in tokens)
```

**Implementation:**
- Split on whitespace
- Strip punctuation (.,!?)
- Normalize to uppercase

---

### Task 5.3: CommandLexer - BUZZ Word Filtering
**Goal:** Filter out noise words (THE, A, AN, etc.)

**Test Cases:**
```python
def test_lexer_filters_buzz_words():
    """Lexer removes THE, A, AN."""
    tokens = lexer.tokenize("take the brass lamp")
    words = [t.word for t in tokens]
    assert "THE" not in words
    assert "TAKE" in words
    assert "BRASS" in words
    assert "LAMP" in words

def test_lexer_preserves_non_buzz():
    """Lexer keeps non-buzz words."""
    tokens = lexer.tokenize("put the lamp in the case")
    words = [t.word for t in tokens]
    assert words == ["PUT", "LAMP", "IN", "CASE"]
```

**Implementation:**
- Use directive_processor.is_buzz_word()
- Filter out tokens where is_buzz_word() returns True

---

### Task 5.4: CommandLexer - SYNONYM Resolution
**Goal:** Map synonyms to canonical forms

**Test Cases:**
```python
def test_lexer_resolves_direction_synonyms():
    """Lexer maps N to NORTH."""
    tokens = lexer.tokenize("n")
    assert tokens[0].word == "NORTH"

def test_lexer_resolves_preposition_synonyms():
    """Lexer maps USING to WITH."""
    tokens = lexer.tokenize("cut rope using knife")
    words = [t.word for t in tokens]
    assert "WITH" in words
    assert "USING" not in words

def test_lexer_preserves_unknown_words():
    """Unknown words stay unchanged."""
    tokens = lexer.tokenize("xyzzy lamp")
    assert tokens[0].word == "XYZZY"
```

**Implementation:**
- Use directive_processor.get_canonical()
- Replace each token with canonical form

---

### Task 5.5: CommandLexer - Token Type Classification
**Goal:** Classify tokens by type (verb, noun, preposition, direction)

**Test Cases:**
```python
def test_lexer_identifies_directions():
    """Lexer marks directions."""
    tokens = lexer.tokenize("north")
    assert tokens[0].type == TokenType.DIRECTION

def test_lexer_identifies_prepositions():
    """Lexer marks prepositions."""
    tokens = lexer.tokenize("put lamp in case")
    assert tokens[2].type == TokenType.PREPOSITION

def test_lexer_verb_is_first_non_direction():
    """First word that has SYNTAX entry is verb."""
    tokens = lexer.tokenize("take lamp")
    assert tokens[0].type == TokenType.VERB
```

**Implementation:**
- Check if word is direction
- Check if word has SYNTAX entries
- Mark prepositions (WITH, IN, ON, TO, FROM, etc.)

---

### Task 5.6: CommandParser - Basic Structure
**Goal:** Parse token stream into ParsedCommand

**Test Cases:**
```python
def test_parser_simple_verb():
    """Parse verb-only command."""
    parser = CommandParser(directive_processor)
    cmd = parser.parse(lexer.tokenize("quit"))
    assert cmd.verb == "QUIT"
    assert len(cmd.noun_phrases) == 0

def test_parser_verb_object():
    """Parse VERB OBJECT command."""
    cmd = parser.parse(lexer.tokenize("take lamp"))
    assert cmd.verb == "TAKE"
    assert len(cmd.noun_phrases) == 1
    assert cmd.noun_phrases[0].noun == "LAMP"

def test_parser_direction_as_verb():
    """Direction alone becomes WALK direction."""
    cmd = parser.parse(lexer.tokenize("north"))
    assert cmd.verb == "WALK"
    assert cmd.direction == "NORTH"
```

**Implementation:**
- Handle direction-only commands specially
- Extract verb (first token with SYNTAX entry)
- Build noun phrases from remaining tokens

---

### Task 5.7: CommandParser - Noun Phrase Extraction
**Goal:** Group adjectives with nouns

**Test Cases:**
```python
def test_parser_adjective_noun():
    """Parse adjective + noun."""
    cmd = parser.parse(lexer.tokenize("take brass lamp"))
    assert cmd.noun_phrases[0].adjectives == ["BRASS"]
    assert cmd.noun_phrases[0].noun == "LAMP"

def test_parser_multiple_adjectives():
    """Parse multiple adjectives."""
    cmd = parser.parse(lexer.tokenize("take small brass lamp"))
    assert cmd.noun_phrases[0].adjectives == ["SMALL", "BRASS"]
    assert cmd.noun_phrases[0].noun == "LAMP"

def test_parser_preposition_separates_objects():
    """Preposition starts new noun phrase."""
    cmd = parser.parse(lexer.tokenize("put brass lamp in wooden case"))
    assert len(cmd.noun_phrases) == 2
    assert cmd.preposition == "IN"
```

**Implementation:**
- Collect adjectives until noun found
- Preposition marks boundary between noun phrases
- Unknown words become adjectives if before noun, noun otherwise

---

### Task 5.8: SyntaxMatcher - Basic Lookup
**Goal:** Find matching SYNTAX entry for parsed command

**Test Cases:**
```python
def test_matcher_simple_verb():
    """Match verb-only syntax."""
    matcher = SyntaxMatcher(directive_processor.syntax_table)
    entry = matcher.match("QUIT", 0, None)
    assert entry is not None
    assert entry.action == "V-QUIT"

def test_matcher_verb_object():
    """Match VERB OBJECT syntax."""
    entry = matcher.match("TAKE", 1, None)
    assert entry is not None
    assert entry.action == "V-TAKE"

def test_matcher_two_objects_with_prep():
    """Match VERB OBJ PREP OBJ syntax."""
    entry = matcher.match("PUT", 2, "IN")
    assert entry is not None
    assert "IN" in entry.prepositions
```

**Implementation:**
- Delegate to syntax_table.match()
- Return None if no match

---

### Task 5.9: ObjectResolver - Basic Resolution
**Goal:** Resolve noun phrases to game objects

**Test Cases:**
```python
def test_resolver_finds_object_by_synonym():
    """Resolver finds object by synonym."""
    resolver = ObjectResolver(world_state)
    world_state.add_object(lamp)  # lamp.synonyms = ["LAMP", "LANTERN"]
    obj = resolver.resolve(NounPhrase(noun="LAMP"), room)
    assert obj == lamp

def test_resolver_checks_location():
    """Resolver only finds accessible objects."""
    lamp.move_to(other_room)  # Not in player's room
    obj = resolver.resolve(NounPhrase(noun="LAMP"), current_room)
    assert obj is None

def test_resolver_uses_adjective():
    """Resolver uses adjective to disambiguate."""
    brass_lamp.adjectives = ["BRASS"]
    wooden_lamp.adjectives = ["WOODEN"]
    obj = resolver.resolve(NounPhrase(adjectives=["BRASS"], noun="LAMP"), room)
    assert obj == brass_lamp
```

**Implementation:**
- Search accessible objects (room + inventory + in scope)
- Match noun against object synonyms
- Filter by adjectives if present

---

### Task 5.10: ObjectResolver - Accessibility
**Goal:** Check if objects are accessible

**Test Cases:**
```python
def test_accessible_in_room():
    """Objects in current room are accessible."""
    lamp.move_to(current_room)
    assert resolver.is_accessible(lamp, current_room)

def test_accessible_in_inventory():
    """Objects in inventory are accessible."""
    lamp.move_to(player)
    assert resolver.is_accessible(lamp, current_room)

def test_accessible_in_open_container():
    """Objects in open containers are accessible."""
    lamp.move_to(open_case)
    open_case.move_to(current_room)
    assert resolver.is_accessible(lamp, current_room)

def test_not_accessible_in_closed_container():
    """Objects in closed containers not accessible."""
    lamp.move_to(closed_case)
    closed_case.move_to(current_room)
    assert not resolver.is_accessible(lamp, current_room)
```

**Implementation:**
- Check if object is in room, player inventory, or open container
- Recursively check container openness

---

### Task 5.11: ObjectResolver - Disambiguation
**Goal:** Handle multiple matching objects

**Test Cases:**
```python
def test_resolver_returns_multiple_matches():
    """Resolver returns all matches for disambiguation."""
    brass_lamp.move_to(room)
    wooden_lamp.move_to(room)  # Both have "LAMP" synonym
    matches = resolver.find_matches(NounPhrase(noun="LAMP"), room)
    assert len(matches) == 2

def test_resolver_disambiguates_by_adjective():
    """Adjective narrows matches."""
    matches = resolver.find_matches(
        NounPhrase(adjectives=["BRASS"], noun="LAMP"), room
    )
    assert len(matches) == 1
    assert matches[0] == brass_lamp
```

**Implementation:**
- find_matches() returns list of all matching objects
- resolve() returns single object or raises DisambiguationError
- DisambiguationError contains list of candidates

---

### Task 5.12: ParserState - PRSA/PRSO/PRSI Binding
**Goal:** Set parser state globals from resolved command

**Test Cases:**
```python
def test_state_sets_prsa():
    """Sets PRSA to action routine name."""
    state = ParserState(world_state)
    state.bind(syntax_entry, [lamp], None)
    assert world_state.get_global("PRSA") == "V-TAKE"

def test_state_sets_prso():
    """Sets PRSO to direct object."""
    state.bind(syntax_entry, [lamp], None)
    assert world_state.get_global("PRSO") == lamp

def test_state_sets_prsi():
    """Sets PRSI to indirect object."""
    state.bind(syntax_entry, [lamp, case], "IN")
    assert world_state.get_global("PRSO") == lamp
    assert world_state.get_global("PRSI") == case
```

**Implementation:**
- Store action routine as PRSA
- Store first object as PRSO
- Store second object as PRSI (if present)

---

### Task 5.13: CommandProcessor - Full Pipeline
**Goal:** Orchestrate full command processing

**Test Cases:**
```python
def test_processor_simple_command():
    """Process simple command end-to-end."""
    processor = CommandProcessor(directive_processor, world_state)
    result = processor.process("take lamp")
    assert result.success
    assert world_state.get_global("PRSA") == "V-TAKE"
    assert world_state.get_global("PRSO").name == "LAMP"

def test_processor_two_object_command():
    """Process PUT X IN Y command."""
    result = processor.process("put lamp in case")
    assert result.success
    assert world_state.get_global("PRSI").name == "CASE"

def test_processor_direction_command():
    """Process direction command."""
    result = processor.process("north")
    assert result.success
    assert world_state.get_global("PRSA") == "V-WALK"
    assert world_state.get_global("P-DIR") == "NORTH"
```

**Implementation:**
- Combine lexer → parser → matcher → resolver → state
- Return CommandResult with success/failure and any error

---

### Task 5.14: Error Handling - Unknown Verb
**Goal:** Handle unknown verbs gracefully

**Test Cases:**
```python
def test_unknown_verb():
    """Unknown verb returns error."""
    result = processor.process("xyzzy lamp")
    assert not result.success
    assert "don't understand" in result.error.lower()

def test_no_matching_syntax():
    """Syntax mismatch returns error."""
    result = processor.process("quit lamp")  # QUIT takes no objects
    assert not result.success
```

**Implementation:**
- CommandResult.error contains error message
- Return appropriate message for each failure type

---

### Task 5.15: Error Handling - Object Not Found
**Goal:** Handle unresolved objects

**Test Cases:**
```python
def test_object_not_found():
    """Missing object returns error."""
    result = processor.process("take dinosaur")
    assert not result.success
    assert "can't see" in result.error.lower()

def test_object_not_accessible():
    """Inaccessible object returns error."""
    lamp.move_to(other_room)
    result = processor.process("take lamp")
    assert not result.success
```

**Implementation:**
- "I can't see any X here."
- Check accessibility before resolving

---

### Task 5.16: Integration - Zork I Commands
**Goal:** Test with actual Zork I vocabulary

**Test Cases:**
```python
def test_zork_take_command(zork_processor):
    """TAKE works with Zork I SYNTAX."""
    lamp = zork_world.get_object("LAMP")
    lamp.move_to(zork_world.get_current_room())
    result = zork_processor.process("take lamp")
    assert result.success

def test_zork_direction_synonyms(zork_processor):
    """Direction synonyms work."""
    result = zork_processor.process("n")
    assert result.success
    assert zork_world.get_global("P-DIR") == "NORTH"

def test_zork_put_in_command(zork_processor):
    """PUT X IN Y works."""
    result = zork_processor.process("put lamp in case")
    assert result.success
```

**Implementation:**
- Use full DirectiveProcessor with Zork I files loaded
- Test key verbs: TAKE, DROP, LOOK, PUT, OPEN, CLOSE

---

## File Structure

```
zil_interpreter/runtime/
├── command_lexer.py      # Task 5.2-5.5
├── command_parser.py     # Task 5.6-5.7
├── syntax_matcher.py     # Task 5.8
├── object_resolver.py    # Task 5.9-5.11
├── parser_state.py       # Task 5.12
├── command_processor.py  # Task 5.13-5.15
└── command_types.py      # Task 5.1

tests/runtime/
├── test_command_lexer.py
├── test_command_parser.py
├── test_syntax_matcher.py
├── test_object_resolver.py
├── test_parser_state.py
├── test_command_processor.py
└── test_command_types.py

tests/integration/
└── test_zork_commands.py  # Task 5.16
```

---

## Dependencies

- **Chunk 4:** DirectiveProcessor, SyntaxTable, BUZZ words, SYNONYMs
- **Existing:** WorldState, GameObject

---

## Success Criteria

| Test Category | Expected Count |
|--------------|----------------|
| Token types | 8 |
| Lexer | 15 |
| Parser | 12 |
| SyntaxMatcher | 6 |
| ObjectResolver | 12 |
| ParserState | 6 |
| CommandProcessor | 10 |
| Integration | 10 |
| **Total** | **~79** |
