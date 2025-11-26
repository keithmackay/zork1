"""Tests for TELL with mixed content types - Task 3.5."""
import pytest
from zil_interpreter.compiler.tell_macro import expand_tell
from zil_interpreter.parser.ast_nodes import Form, Atom, String, GlobalRef, LocalRef, Number


class TestTellMixed:
    """Tests for complex TELL expansions (Task 3.5)."""

    def test_string_and_object(self):
        """String followed by D indicator."""
        # <TELL "The " D ,LAMP " is here.">
        args = [
            String("The "),
            Atom("D"), GlobalRef("LAMP"),
            String(" is here.")
        ]
        result = expand_tell(args)
        # <PROG () <PRINTI "The "> <PRINTD ,LAMP> <PRINTI " is here.">>
        assert result.operator.value == "PROG"
        assert len(result.args) == 4  # () + 3 prints
        assert result.args[0] == []

        # Check first PRINTI
        assert result.args[1].operator.value == "PRINTI"
        assert result.args[1].args[0].value == "The "

        # Check PRINTD
        assert result.args[2].operator.value == "PRINTD"
        assert result.args[2].args[0].name == "LAMP"

        # Check second PRINTI
        assert result.args[3].operator.value == "PRINTI"
        assert result.args[3].args[0].value == " is here."

    def test_full_sentence_with_cr(self):
        """Complete sentence with CR."""
        # <TELL "You see a " D ,PRSO " here." CR>
        args = [
            String("You see a "),
            Atom("D"), GlobalRef("PRSO"),
            String(" here."),
            Atom("CR")
        ]
        result = expand_tell(args)
        # <PROG () <PRINTI "You see a "> <PRINTD ,PRSO> <PRINTI " here."> <CRLF>>
        assert len(result.args) == 5  # () + 4 forms
        assert result.args[1].operator.value == "PRINTI"
        assert result.args[2].operator.value == "PRINTD"
        assert result.args[3].operator.value == "PRINTI"
        assert result.args[4].operator.value == "CRLF"

    def test_expression_argument(self):
        """Form expression wrapped in PRINT."""
        # <TELL <GET-DESC ,LAMP>>
        args = [Form(Atom("GET-DESC"), [GlobalRef("LAMP")])]
        result = expand_tell(args)
        # <PROG () <PRINT <GET-DESC ,LAMP>>>
        assert len(result.args) == 2  # () + PRINT
        body = result.args[1]
        assert body.operator.value == "PRINT"
        assert len(body.args) == 1

        get_desc = body.args[0]
        assert isinstance(get_desc, Form)
        assert get_desc.operator.value == "GET-DESC"
        assert get_desc.args[0].name == "LAMP"

    def test_multiple_numbers(self):
        """Multiple N indicators."""
        # <TELL "Score: " N ,SCORE " Moves: " N ,MOVES CR>
        args = [
            String("Score: "),
            Atom("N"), GlobalRef("SCORE"),
            String(" Moves: "),
            Atom("N"), GlobalRef("MOVES"),
            Atom("CR")
        ]
        result = expand_tell(args)
        # <PROG () <PRINTI "Score: "> <PRINTN ,SCORE>
        #          <PRINTI " Moves: "> <PRINTN ,MOVES> <CRLF>>
        assert len(result.args) == 6  # () + 5 forms
        assert result.args[1].operator.value == "PRINTI"
        assert result.args[1].args[0].value == "Score: "
        assert result.args[2].operator.value == "PRINTN"
        assert result.args[3].operator.value == "PRINTI"
        assert result.args[3].args[0].value == " Moves: "
        assert result.args[4].operator.value == "PRINTN"
        assert result.args[5].operator.value == "CRLF"

    def test_article_with_strings(self):
        """Article indicator with surrounding strings."""
        # <TELL "You see " A ,LAMP " on the table." CR>
        args = [
            String("You see "),
            Atom("A"), GlobalRef("LAMP"),
            String(" on the table."),
            Atom("CR")
        ]
        result = expand_tell(args)
        assert len(result.args) == 5
        assert result.args[1].operator.value == "PRINTI"
        assert result.args[2].operator.value == "PRINTA"
        assert result.args[3].operator.value == "PRINTI"
        assert result.args[4].operator.value == "CRLF"

    def test_complex_mixed_content(self):
        """Complex mix of strings, indicators, and forms."""
        # <TELL "There " <VERB WALK> " " N .COUNT " " D ,PRSO " here." CR>
        args = [
            String("There "),
            Form(Atom("VERB"), [Atom("WALK")]),
            String(" "),
            Atom("N"), LocalRef("COUNT"),
            String(" "),
            Atom("D"), GlobalRef("PRSO"),
            String(" here."),
            Atom("CR")
        ]
        result = expand_tell(args)
        # Should have: () + PRINTI + PRINT + PRINTI + PRINTN + PRINTI + PRINTD + PRINTI + CRLF
        assert len(result.args) == 9
        assert result.args[1].operator.value == "PRINTI"
        assert result.args[2].operator.value == "PRINT"
        assert result.args[3].operator.value == "PRINTI"
        assert result.args[4].operator.value == "PRINTN"
        assert result.args[5].operator.value == "PRINTI"
        assert result.args[6].operator.value == "PRINTD"
        assert result.args[7].operator.value == "PRINTI"
        assert result.args[8].operator.value == "CRLF"

    def test_property_with_strings(self):
        """Property indicator with surrounding text."""
        # <TELL "The description is: " LDESC ,TROLL CR>
        args = [
            String("The description is: "),
            Atom("LDESC"), GlobalRef("TROLL"),
            Atom("CR")
        ]
        result = expand_tell(args)
        assert len(result.args) == 4
        assert result.args[1].operator.value == "PRINTI"
        assert result.args[2].operator.value == "PRINT"
        getp = result.args[2].args[0]
        assert getp.operator.value == "GETP"
        assert result.args[3].operator.value == "CRLF"

    def test_character_in_sentence(self):
        """Character indicator within sentence."""
        # <TELL "Grade: " C 65 CR>
        args = [
            String("Grade: "),
            Atom("C"), Number(65),
            Atom("CR")
        ]
        result = expand_tell(args)
        assert len(result.args) == 4
        assert result.args[1].operator.value == "PRINTI"
        assert result.args[2].operator.value == "PRINTC"
        assert result.args[3].operator.value == "CRLF"

    def test_all_indicators_together(self):
        """All indicator types in one TELL."""
        # <TELL D ,OBJ1 N .NUM C 88 A ,OBJ2 PROP ,OBJ3>
        args = [
            Atom("D"), GlobalRef("OBJ1"),
            Atom("N"), LocalRef("NUM"),
            Atom("C"), Number(88),
            Atom("A"), GlobalRef("OBJ2"),
            Atom("PROP"), GlobalRef("OBJ3")
        ]
        result = expand_tell(args)
        assert len(result.args) == 6  # () + 5 forms
        assert result.args[1].operator.value == "PRINTD"
        assert result.args[2].operator.value == "PRINTN"
        assert result.args[3].operator.value == "PRINTC"
        assert result.args[4].operator.value == "PRINTA"
        assert result.args[5].operator.value == "PRINT"
        # Last one should be GETP
        getp = result.args[5].args[0]
        assert getp.operator.value == "GETP"

    def test_nested_forms(self):
        """Multiple nested forms in TELL."""
        # <TELL <FIRST-LINE> <SECOND-LINE> CR>
        args = [
            Form(Atom("FIRST-LINE"), []),
            Form(Atom("SECOND-LINE"), []),
            Atom("CR")
        ]
        result = expand_tell(args)
        assert len(result.args) == 4
        assert result.args[1].operator.value == "PRINT"
        assert result.args[1].args[0].operator.value == "FIRST-LINE"
        assert result.args[2].operator.value == "PRINT"
        assert result.args[2].args[0].operator.value == "SECOND-LINE"
        assert result.args[3].operator.value == "CRLF"

    def test_real_world_example(self):
        """Real-world example from Zork I."""
        # <TELL "The " D ,LAMP " is " <COND (<FSET? ,LAMP ONBIT> "on") (T "off")> "." CR>
        cond_form = Form(Atom("COND"), [
            [Form(Atom("FSET?"), [GlobalRef("LAMP"), Atom("ONBIT")]), String("on")],
            [Atom("T"), String("off")]
        ])
        args = [
            String("The "),
            Atom("D"), GlobalRef("LAMP"),
            String(" is "),
            cond_form,
            String("."),
            Atom("CR")
        ]
        result = expand_tell(args)
        assert len(result.args) == 7  # () + 6 forms
        assert result.args[1].operator.value == "PRINTI"
        assert result.args[1].args[0].value == "The "
        assert result.args[2].operator.value == "PRINTD"
        assert result.args[3].operator.value == "PRINTI"
        assert result.args[3].args[0].value == " is "
        assert result.args[4].operator.value == "PRINT"
        assert result.args[4].args[0].operator.value == "COND"
        assert result.args[5].operator.value == "PRINTI"
        assert result.args[5].args[0].value == "."
        assert result.args[6].operator.value == "CRLF"
