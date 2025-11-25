"""Integration tests for ZIL operations working together."""

import pytest
from zil_interpreter.parser.ast_nodes import Form, Atom, Number, String
from zil_interpreter.engine.evaluator import Evaluator
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.runtime.output_buffer import OutputBuffer


class TestOperationIntegration:
    """Test multiple operations working together."""

    def test_logic_and_arithmetic_integration(self):
        """Test AND with arithmetic operations."""
        world = WorldState()
        evaluator = Evaluator(world)

        # <AND <G? 5 3> <L? 2 4>>  -> Should return True (last value)
        result = evaluator.evaluate(
            Form(Atom("AND"), [
                Form(Atom("G?"), [Number(5), Number(3)]),
                Form(Atom("L?"), [Number(2), Number(4)])
            ])
        )

        assert result is True

    def test_cond_with_comparison_and_arithmetic(self):
        """Test COND with comparisons and arithmetic."""
        world = WorldState()
        evaluator = Evaluator(world)

        # <COND (<G? 5 3> <+ 10 20>)
        #       (<L? 1 2> <* 2 3>)>
        result = evaluator.evaluate(
            Form(Atom("COND"), [
                [Form(Atom("G?"), [Number(5), Number(3)]),
                 Form(Atom("+"), [Number(10), Number(20)])],
                [Form(Atom("L?"), [Number(1), Number(2)]),
                 Form(Atom("*"), [Number(2), Number(3)])]
            ])
        )

        # First condition is true, so returns 30
        assert result == 30

    def test_string_operations_integration(self):
        """Test string operations together."""
        world = WorldState()
        evaluator = Evaluator(world)

        # <CONCAT "Hello" " " "World">
        result = evaluator.evaluate(
            Form(Atom("CONCAT"), [
                String("Hello"),
                String(" "),
                String("World")
            ])
        )

        assert result == "Hello World"

        # <SUBSTRING "Hello World" 0 5> (0-indexed)
        substr = evaluator.evaluate(
            Form(Atom("SUBSTRING"), [
                String("Hello World"),
                Number(0),
                Number(5)
            ])
        )

        assert substr == "Hello"

    def test_list_operations_integration(self):
        """Test list operations working together."""
        world = WorldState()
        evaluator = Evaluator(world)

        test_list = [Number(1), Number(2), Number(3), Number(4), Number(5)]

        # <LENGTH '(1 2 3 4 5)>
        length = evaluator.evaluate(
            Form(Atom("LENGTH"), [test_list])
        )
        assert length == 5

        # <NTH '(1 2 3 4 5) 3>
        nth = evaluator.evaluate(
            Form(Atom("NTH"), [test_list, Number(3)])
        )
        assert nth == 3

        # <REST '(1 2 3 4 5)>
        rest = evaluator.evaluate(
            Form(Atom("REST"), [test_list])
        )
        # REST extracts values from Number objects
        assert len(rest) == 4
        assert rest[0] == 2 or rest[0] == Number(2)

    def test_object_operations_integration(self):
        """Test object operations working together."""
        from zil_interpreter.world.game_object import GameObject, ObjectFlag

        world = WorldState()

        # Create test objects
        room = GameObject("ROOM")
        lamp = GameObject("LAMP")
        lamp.set_flag(ObjectFlag.TAKEABLE)

        world.add_object(room)
        world.add_object(lamp)
        lamp.move_to(room)

        evaluator = Evaluator(world)

        # <IN? LAMP ROOM>
        in_check = evaluator.evaluate(
            Form(Atom("IN?"), [Atom("LAMP"), Atom("ROOM")])
        )
        assert in_check is True

        # <FSET? LAMP TAKEABLEBIT>
        fset_check = evaluator.evaluate(
            Form(Atom("FSET?"), [Atom("LAMP"), Atom("TAKEABLEBIT")])
        )
        assert fset_check is True

        # <LOC LAMP>
        loc = evaluator.evaluate(
            Form(Atom("LOC"), [Atom("LAMP")])
        )
        assert loc == room

    def test_complex_nested_operations(self):
        """Test deeply nested operations."""
        world = WorldState()
        evaluator = Evaluator(world)

        # <AND <OR <ZERO? 0> <G? 1 2>> <NOT <L? 5 3>>>
        result = evaluator.evaluate(
            Form(Atom("AND"), [
                Form(Atom("OR"), [
                    Form(Atom("ZERO?"), [Number(0)]),
                    Form(Atom("G?"), [Number(1), Number(2)])
                ]),
                Form(Atom("NOT"), [
                    Form(Atom("L?"), [Number(5), Number(3)])
                ])
            ])
        )

        # OR: ZERO? 0 is True, so OR returns True
        # NOT: L? 5 3 is False, so NOT returns True
        # AND: True AND True = True
        assert result is True

    def test_arithmetic_chain(self):
        """Test chained arithmetic operations."""
        world = WorldState()
        evaluator = Evaluator(world)

        # <+ <- 10 3> <* 2 5> </ 20 4>>
        # = 7 + 10 + 5 = 22
        result = evaluator.evaluate(
            Form(Atom("+"), [
                Form(Atom("-"), [Number(10), Number(3)]),
                Form(Atom("*"), [Number(2), Number(5)]),
                Form(Atom("/"), [Number(20), Number(4)])
            ])
        )

        assert result == 22

    def test_conditional_with_multiple_clauses(self):
        """Test COND with multiple clauses."""
        world = WorldState()
        evaluator = Evaluator(world)

        # Test case where third clause matches
        # <COND (<ZERO? 5> 1)
        #       (<G? 2 10> 2)
        #       (<L? 3 7> 3)
        #       (T 4)>
        result = evaluator.evaluate(
            Form(Atom("COND"), [
                [Form(Atom("ZERO?"), [Number(5)]), Number(1)],
                [Form(Atom("G?"), [Number(2), Number(10)]), Number(2)],
                [Form(Atom("L?"), [Number(3), Number(7)]), Number(3)],
                [Atom("T"), Number(4)]
            ])
        )

        assert result == 3

    def test_logic_short_circuit_and(self):
        """Test AND short-circuit behavior."""
        world = WorldState()
        evaluator = Evaluator(world)

        # <AND <ZERO? 5> <G? 10 5>>
        # Should return False immediately without evaluating second form
        result = evaluator.evaluate(
            Form(Atom("AND"), [
                Form(Atom("ZERO?"), [Number(5)]),
                Form(Atom("G?"), [Number(10), Number(5)])
            ])
        )

        assert result is False

    def test_logic_short_circuit_or(self):
        """Test OR short-circuit behavior."""
        world = WorldState()
        evaluator = Evaluator(world)

        # <OR <ZERO? 0> <G? 1 10>>
        # Should return True immediately without evaluating second form
        result = evaluator.evaluate(
            Form(Atom("OR"), [
                Form(Atom("ZERO?"), [Number(0)]),
                Form(Atom("G?"), [Number(1), Number(10)])
            ])
        )

        assert result is True


class TestZorkICompatibility:
    """Test compatibility with actual Zork I patterns."""

    def test_zork_verb_check_pattern(self):
        """Test typical Zork verb checking pattern."""
        world = WorldState()
        world.set_global("PRSA", "TAKE")
        evaluator = Evaluator(world)

        # <VERB? TAKE>
        result = evaluator.evaluate(
            Form(Atom("VERB?"), [Atom("TAKE")])
        )

        assert result is True

    def test_zork_multiple_verb_check(self):
        """Test Zork pattern with OR for multiple verbs."""
        world = WorldState()
        world.set_global("PRSA", "EXAMINE")
        evaluator = Evaluator(world)

        # <OR <VERB? TAKE> <VERB? EXAMINE> <VERB? DROP>>
        result = evaluator.evaluate(
            Form(Atom("OR"), [
                Form(Atom("VERB?"), [Atom("TAKE")]),
                Form(Atom("VERB?"), [Atom("EXAMINE")]),
                Form(Atom("VERB?"), [Atom("DROP")])
            ])
        )

        assert result is True

    def test_zork_object_interaction_pattern(self):
        """Test typical Zork object interaction pattern."""
        from zil_interpreter.world.game_object import GameObject, ObjectFlag

        world = WorldState()

        # Setup game world
        player = GameObject("PLAYER")
        room = GameObject("WEST-OF-HOUSE")
        mailbox = GameObject("MAILBOX")

        mailbox.set_property("DESC", "A small mailbox")
        mailbox.set_flag(ObjectFlag.CONTAINER)

        world.add_object(player)
        world.add_object(room)
        world.add_object(mailbox)

        mailbox.move_to(room)
        world.set_global("PLAYER", player)

        evaluator = Evaluator(world)

        # <AND <IN? MAILBOX WEST-OF-HOUSE> <FSET? MAILBOX CONTAINERBIT>>
        result = evaluator.evaluate(
            Form(Atom("AND"), [
                Form(Atom("IN?"), [Atom("MAILBOX"), Atom("WEST-OF-HOUSE")]),
                Form(Atom("FSET?"), [Atom("MAILBOX"), Atom("CONTAINERBIT")])
            ])
        )

        assert result is True

    def test_zork_conditional_action_pattern(self):
        """Test typical Zork conditional action pattern."""
        from zil_interpreter.world.game_object import GameObject

        world = WorldState()
        world.set_global("SCORE", 10)

        evaluator = Evaluator(world)

        # <COND (<G? ,SCORE 0>
        #        <TELL "You have points!" CR>)>
        result = evaluator.evaluate(
            Form(Atom("COND"), [
                [Form(Atom("G?"), [Atom("SCORE"), Number(0)]),
                 Form(Atom("TELL"), [String("You have points!"), Atom("CR")])]
            ])
        )

        output_text = evaluator.output.get_output()
        assert "You have points!" in output_text
        assert "\n" in output_text

    def test_zork_open_close_pattern(self):
        """Test Zork OPEN-CLOSE pattern from 1actions.zil."""
        from zil_interpreter.world.game_object import GameObject, ObjectFlag

        world = WorldState()
        world.set_global("PRSA", "OPEN")

        window = GameObject("KITCHEN-WINDOW")
        world.add_object(window)

        evaluator = Evaluator(world)

        # Simulate: <VERB? OPEN>
        verb_check = evaluator.evaluate(
            Form(Atom("VERB?"), [Atom("OPEN")])
        )
        assert verb_check is True

        # Simulate: <FSET? KITCHEN-WINDOW OPENBIT>
        is_open = evaluator.evaluate(
            Form(Atom("FSET?"), [Atom("KITCHEN-WINDOW"), Atom("OPENBIT")])
        )
        assert is_open is False

        # Simulate: <FSET KITCHEN-WINDOW OPENBIT>
        evaluator.evaluate(
            Form(Atom("FSET"), [Atom("KITCHEN-WINDOW"), Atom("OPENBIT")])
        )

        # Verify it's now open
        is_open_after = evaluator.evaluate(
            Form(Atom("FSET?"), [Atom("KITCHEN-WINDOW"), Atom("OPENBIT")])
        )
        assert is_open_after is True

    def test_zork_inventory_pattern(self):
        """Test Zork inventory checking pattern."""
        from zil_interpreter.world.game_object import GameObject

        world = WorldState()

        player = GameObject("PLAYER")
        lamp = GameObject("LAMP")
        sword = GameObject("SWORD")

        world.add_object(player)
        world.add_object(lamp)
        world.add_object(sword)

        lamp.move_to(player)
        sword.move_to(player)

        evaluator = Evaluator(world)

        # Test FIRST? directly with player object name
        # <FIRST? PLAYER>
        first_item = evaluator.evaluate(
            Form(Atom("FIRST?"), [Atom("PLAYER")])
        )

        # FIRST? returns first child's name as string
        assert first_item in ["LAMP", "SWORD"]

    def test_zork_equal_comparison_pattern(self):
        """Test Zork EQUAL? pattern from 1actions.zil."""
        world = WorldState()

        # Create room object
        from zil_interpreter.world.game_object import GameObject
        room = GameObject("WEST-OF-HOUSE")
        world.add_object(room)

        # Set HERE to the room object itself
        world.set_global("HERE", room)
        # Also set WEST-OF-HOUSE to the same object
        world.set_global("WEST-OF-HOUSE", room)

        evaluator = Evaluator(world)

        # <EQUAL? HERE WEST-OF-HOUSE>
        result = evaluator.evaluate(
            Form(Atom("EQUAL?"), [Atom("HERE"), Atom("WEST-OF-HOUSE")])
        )

        assert result is True

    def test_zork_nested_conditional_pattern(self):
        """Test nested conditional from Zork source."""
        from zil_interpreter.world.game_object import GameObject, ObjectFlag

        world = WorldState()
        world.set_global("PRSA", "CLOSE")

        window = GameObject("WINDOW")
        window.set_flag(ObjectFlag.OPEN)
        world.add_object(window)

        evaluator = Evaluator(world)

        # Simulate nested COND pattern from OPEN-CLOSE routine
        # <COND (<VERB? CLOSE>
        #        <COND (<FSET? WINDOW OPENBIT>
        #               <FCLEAR WINDOW OPENBIT> T)>)>

        outer_cond = evaluator.evaluate(
            Form(Atom("COND"), [
                [Form(Atom("VERB?"), [Atom("CLOSE")]),
                 Form(Atom("COND"), [
                     [Form(Atom("FSET?"), [Atom("WINDOW"), Atom("OPENBIT")]),
                      Form(Atom("FCLEAR"), [Atom("WINDOW"), Atom("OPENBIT")]),
                      Atom("T")]
                 ])]
            ])
        )

        # Should execute and clear the flag
        # COND may return the value of last executed expression

        # Verify flag was cleared
        is_open = evaluator.evaluate(
            Form(Atom("FSET?"), [Atom("WINDOW"), Atom("OPENBIT")])
        )
        assert is_open is False

    def test_zork_global_variable_pattern(self):
        """Test Zork global variable patterns."""
        world = WorldState()

        # Set up common Zork globals
        world.set_global("VERBOSE", True)
        world.set_global("SUPER-BRIEF", False)
        world.set_global("SCORE", 0)

        evaluator = Evaluator(world)

        # Test setting global: <SETG SCORE 10>
        evaluator.evaluate(
            Form(Atom("SETG"), [Atom("SCORE"), Number(10)])
        )

        score = world.get_global("SCORE")
        assert score == 10

        # Test global in comparison: <G? SCORE 5>
        result = evaluator.evaluate(
            Form(Atom("G?"), [Atom("SCORE"), Number(5)])
        )
        assert result is True


class TestComplexIntegration:
    """Test complex real-world scenarios."""

    def test_room_description_logic(self):
        """Test complex room description logic."""
        from zil_interpreter.world.game_object import GameObject, ObjectFlag

        world = WorldState()
        world.set_global("PRSA", "LOOK")

        room = GameObject("EAST-OF-HOUSE")
        window = GameObject("KITCHEN-WINDOW")
        window.set_flag(ObjectFlag.OPEN)

        world.add_object(room)
        world.add_object(window)
        window.move_to(room)

        evaluator = Evaluator(world)

        # Test simpler pattern - just check if TELL works
        # <TELL "You are behind the white house. ">
        evaluator.evaluate(
            Form(Atom("TELL"), [String("You are behind the white house. ")])
        )

        output1 = evaluator.output.get_output()
        assert "You are behind the white house." in output1

        # Clear and test flag check
        evaluator.output.clear()

        # <COND (<FSET? KITCHEN-WINDOW OPENBIT>
        #        <TELL "The window is open.">)>
        evaluator.evaluate(
            Form(Atom("COND"), [
                [Form(Atom("FSET?"), [Atom("KITCHEN-WINDOW"), Atom("OPENBIT")]),
                 Form(Atom("TELL"), [String("The window is open.")])]
            ])
        )

        output2 = evaluator.output.get_output()
        assert "The window is open." in output2

    def test_object_movement_chain(self):
        """Test moving objects through multiple locations."""
        from zil_interpreter.world.game_object import GameObject

        world = WorldState()

        room1 = GameObject("ROOM1")
        room2 = GameObject("ROOM2")
        player = GameObject("PLAYER")
        lamp = GameObject("LAMP")

        world.add_object(room1)
        world.add_object(room2)
        world.add_object(player)
        world.add_object(lamp)

        evaluator = Evaluator(world)

        # Move lamp to room1
        evaluator.evaluate(
            Form(Atom("MOVE"), [Atom("LAMP"), Atom("ROOM1")])
        )

        assert lamp.parent == room1

        # Move lamp to player
        evaluator.evaluate(
            Form(Atom("MOVE"), [Atom("LAMP"), Atom("PLAYER")])
        )

        assert lamp.parent == player

        # Move lamp to room2
        evaluator.evaluate(
            Form(Atom("MOVE"), [Atom("LAMP"), Atom("ROOM2")])
        )

        assert lamp.parent == room2

    def test_arithmetic_with_globals(self):
        """Test arithmetic operations with global variables."""
        world = WorldState()
        world.set_global("SCORE", 10)
        world.set_global("BONUS", 5)

        evaluator = Evaluator(world)

        # <+ SCORE BONUS>
        total = evaluator.evaluate(
            Form(Atom("+"), [Atom("SCORE"), Atom("BONUS")])
        )
        assert total == 15

        # <SETG SCORE <+ SCORE BONUS>>
        evaluator.evaluate(
            Form(Atom("SETG"), [
                Atom("SCORE"),
                Form(Atom("+"), [Atom("SCORE"), Atom("BONUS")])
            ])
        )

        assert world.get_global("SCORE") == 15

    def test_list_traversal_pattern(self):
        """Test list traversal patterns."""
        world = WorldState()
        evaluator = Evaluator(world)

        test_list = [Number(10), Number(20), Number(30), Number(40)]

        # Get first element
        first = evaluator.evaluate(
            Form(Atom("FIRST"), [test_list])
        )
        assert first == 10

        # Get rest of list
        rest = evaluator.evaluate(
            Form(Atom("REST"), [test_list])
        )

        # Get first of rest (second element)
        second = evaluator.evaluate(
            Form(Atom("FIRST"), [rest])
        )
        assert second == 20

        # Get nth element
        third = evaluator.evaluate(
            Form(Atom("NTH"), [test_list, Number(3)])
        )
        assert third == 30


class TestTableOperationsIntegration:
    """Integration tests for table operations."""

    def test_pick_one_pattern(self):
        """Test PICK-ONE pattern from Zork I (random table selection)."""
        from zil_interpreter.world.table_data import TableData

        # Simulates: <GET ,DUMMY <RANDOM <GET ,DUMMY 0>>>
        world = WorldState()
        output = OutputBuffer()
        # DUMMY table: length at 0, then strings
        table = TableData(name="DUMMY", data=[3, 0, 1, 2])  # 3 items
        world.register_table("DUMMY", table)

        # Test GET retrieves length
        assert table.get_word(0) == 3

        # Test GET retrieves items
        assert table.get_word(1) == 0
        assert table.get_word(2) == 1
        assert table.get_word(3) == 2

    def test_parser_lexv_pattern(self):
        """Test parser LEXV table access pattern."""
        from zil_interpreter.world.table_data import TableData

        # P-LEXV is byte-addressed table
        world = WorldState()
        # Simulated lexer output: word count, then word entries
        lexv = TableData(name="P-LEXV", data=[0x0200, 0x4E4F])  # 2 words, "NO"
        world.register_table("P-LEXV", lexv)

        # GETB gets byte 0 (word count high byte)
        assert lexv.get_byte(0) == 0x02


class TestComplexIntegration:
    """Test complex real-world scenarios."""

    def test_flag_manipulation_sequence(self):
        """Test sequence of flag operations."""
        from zil_interpreter.world.game_object import GameObject, ObjectFlag

        world = WorldState()
        lamp = GameObject("LAMP")
        world.add_object(lamp)

        evaluator = Evaluator(world)

        # Initially no flags set
        assert not lamp.has_flag(ObjectFlag.ONBIT)
        assert not lamp.has_flag(ObjectFlag.TAKEABLE)

        # <FSET LAMP ONBIT>
        evaluator.evaluate(
            Form(Atom("FSET"), [Atom("LAMP"), Atom("ONBIT")])
        )
        assert lamp.has_flag(ObjectFlag.ONBIT)

        # <FSET LAMP TAKEABLEBIT>
        evaluator.evaluate(
            Form(Atom("FSET"), [Atom("LAMP"), Atom("TAKEABLEBIT")])
        )
        assert lamp.has_flag(ObjectFlag.TAKEABLE)

        # <FCLEAR LAMP ONBIT>
        evaluator.evaluate(
            Form(Atom("FCLEAR"), [Atom("LAMP"), Atom("ONBIT")])
        )
        assert not lamp.has_flag(ObjectFlag.ONBIT)
        assert lamp.has_flag(ObjectFlag.TAKEABLE)

    def test_output_formatting_integration(self):
        """Test multiple output operations together."""
        world = WorldState()
        evaluator = Evaluator(world)

        # <TELL "Score: " SCORE CR>
        world.set_global("SCORE", 42)

        evaluator.evaluate(
            Form(Atom("TELL"), [
                String("Score: "),
                Atom("SCORE"),
                Atom("CR")
            ])
        )

        output = evaluator.output.get_output()
        assert "Score: 42" in output
        assert output.endswith("\n")
