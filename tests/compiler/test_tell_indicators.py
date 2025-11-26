"""Tests for TELL macro indicators (D, N, C, A) - Task 3.4."""
import pytest
from zil_interpreter.compiler.tell_macro import expand_tell
from zil_interpreter.parser.ast_nodes import Form, Atom, String, GlobalRef, LocalRef, Number


class TestTellIndicators:
    """Tests for TELL indicator expansion (Task 3.4)."""

    def test_d_indicator(self):
        """D expands to PRINTD."""
        # <TELL D ,LAMP>
        args = [Atom("D"), GlobalRef("LAMP")]
        result = expand_tell(args)
        # <PROG () <PRINTD ,LAMP>>
        assert result.operator.value == "PROG"
        assert len(result.args) == 2  # () + PRINTD
        body = result.args[1]
        assert body.operator.value == "PRINTD"
        assert isinstance(body.args[0], GlobalRef)
        assert body.args[0].name == "LAMP"

    def test_desc_indicator(self):
        """DESC is synonym for D."""
        args = [Atom("DESC"), GlobalRef("LAMP")]
        result = expand_tell(args)
        body = result.args[1]
        assert body.operator.value == "PRINTD"
        assert body.args[0].name == "LAMP"

    def test_o_indicator(self):
        """O is synonym for D (object description)."""
        args = [Atom("O"), GlobalRef("LAMP")]
        result = expand_tell(args)
        body = result.args[1]
        assert body.operator.value == "PRINTD"

    def test_obj_indicator(self):
        """OBJ is synonym for D."""
        args = [Atom("OBJ"), GlobalRef("LAMP")]
        result = expand_tell(args)
        body = result.args[1]
        assert body.operator.value == "PRINTD"

    def test_n_indicator(self):
        """N expands to PRINTN."""
        # <TELL N .COUNT>
        args = [Atom("N"), LocalRef("COUNT")]
        result = expand_tell(args)
        # <PROG () <PRINTN .COUNT>>
        body = result.args[1]
        assert body.operator.value == "PRINTN"
        assert isinstance(body.args[0], LocalRef)
        assert body.args[0].name == "COUNT"

    def test_num_indicator(self):
        """NUM is synonym for N."""
        args = [Atom("NUM"), Number(42)]
        result = expand_tell(args)
        body = result.args[1]
        assert body.operator.value == "PRINTN"
        assert body.args[0].value == 42

    def test_n_with_form(self):
        """N with form expression."""
        # <TELL N <RANDOM 10>>
        args = [Atom("N"), Form(Atom("RANDOM"), [Number(10)])]
        result = expand_tell(args)
        body = result.args[1]
        assert body.operator.value == "PRINTN"
        random_form = body.args[0]
        assert random_form.operator.value == "RANDOM"

    def test_c_indicator(self):
        """C expands to PRINTC."""
        args = [Atom("C"), Number(65)]  # ASCII 'A'
        result = expand_tell(args)
        body = result.args[1]
        assert body.operator.value == "PRINTC"
        assert body.args[0].value == 65

    def test_chr_indicator(self):
        """CHR is synonym for C."""
        args = [Atom("CHR"), Number(66)]
        result = expand_tell(args)
        body = result.args[1]
        assert body.operator.value == "PRINTC"

    def test_char_indicator(self):
        """CHAR is synonym for C."""
        args = [Atom("CHAR"), Number(67)]
        result = expand_tell(args)
        body = result.args[1]
        assert body.operator.value == "PRINTC"

    def test_a_indicator(self):
        """A expands to PRINTA (article)."""
        args = [Atom("A"), GlobalRef("LAMP")]
        result = expand_tell(args)
        body = result.args[1]
        assert body.operator.value == "PRINTA"
        assert body.args[0].name == "LAMP"

    def test_an_indicator(self):
        """AN is synonym for A."""
        args = [Atom("AN"), GlobalRef("APPLE")]
        result = expand_tell(args)
        body = result.args[1]
        assert body.operator.value == "PRINTA"
        assert body.args[0].name == "APPLE"

    def test_property_indicator(self):
        """Unknown indicator treated as property lookup."""
        # <TELL LDESC ,TROLL>  -> <PROG () <PRINT <GETP ,TROLL LDESC>>>
        args = [Atom("LDESC"), GlobalRef("TROLL")]
        result = expand_tell(args)
        body = result.args[1]
        assert body.operator.value == "PRINT"
        assert len(body.args) == 1

        getp = body.args[0]
        assert isinstance(getp, Form)
        assert getp.operator.value == "GETP"
        assert len(getp.args) == 2
        assert isinstance(getp.args[0], GlobalRef)
        assert getp.args[0].name == "TROLL"
        assert isinstance(getp.args[1], Atom)
        assert getp.args[1].value == "LDESC"

    def test_custom_property_indicator(self):
        """Custom property names work as indicators."""
        # <TELL ACTION ,DOOR>  -> <PRINT <GETP ,DOOR ACTION>>
        args = [Atom("ACTION"), GlobalRef("DOOR")]
        result = expand_tell(args)
        body = result.args[1]
        assert body.operator.value == "PRINT"
        getp = body.args[0]
        assert getp.operator.value == "GETP"
        assert getp.args[1].value == "ACTION"

    def test_multiple_indicators(self):
        """Multiple indicators in sequence."""
        # <TELL D ,LAMP N ,COUNT C 65>
        args = [
            Atom("D"), GlobalRef("LAMP"),
            Atom("N"), GlobalRef("COUNT"),
            Atom("C"), Number(65)
        ]
        result = expand_tell(args)
        assert len(result.args) == 4  # () + 3 prints

        assert result.args[1].operator.value == "PRINTD"
        assert result.args[2].operator.value == "PRINTN"
        assert result.args[3].operator.value == "PRINTC"

    def test_case_insensitive_indicators(self):
        """Indicators are case-insensitive."""
        # Test lowercase
        args_lower = [Atom("d"), GlobalRef("LAMP")]
        result_lower = expand_tell(args_lower)
        assert result_lower.args[1].operator.value == "PRINTD"

        # Test mixed case
        args_mixed = [Atom("Desc"), GlobalRef("LAMP")]
        result_mixed = expand_tell(args_mixed)
        assert result_mixed.args[1].operator.value == "PRINTD"
