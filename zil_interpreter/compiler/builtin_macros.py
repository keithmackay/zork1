"""Built-in macro expansion functions for ZIL macros.

This module provides expansion functions for all Zork I built-in macros
except TELL (which has its own module due to complexity).
"""
from typing import List, Any
from ..parser.ast_nodes import Form, Atom, GlobalRef, Number


def expand_enable(args: List[Any]) -> Form:
    """Expand ENABLE macro.

    <ENABLE int> → <PUT int ,C-ENABLED? 1>

    Args:
        args: List containing the interrupt object

    Returns:
        PUT form that enables the interrupt
    """
    if len(args) != 1:
        raise ValueError(f"ENABLE expects 1 argument, got {len(args)}")

    return Form(
        Atom("PUT"),
        [args[0], GlobalRef("C-ENABLED?"), Number(1)]
    )


def expand_disable(args: List[Any]) -> Form:
    """Expand DISABLE macro.

    <DISABLE int> → <PUT int ,C-ENABLED? 0>

    Args:
        args: List containing the interrupt object

    Returns:
        PUT form that disables the interrupt
    """
    if len(args) != 1:
        raise ValueError(f"DISABLE expects 1 argument, got {len(args)}")

    return Form(
        Atom("PUT"),
        [args[0], GlobalRef("C-ENABLED?"), Number(0)]
    )


def expand_rfatal(args: List[Any]) -> Form:
    """Expand RFATAL macro.

    <RFATAL> → <PROG () <PUSH 2> <RSTACK>>

    Args:
        args: Empty list (RFATAL takes no arguments)

    Returns:
        PROG form that performs fatal return stack operation
    """
    if len(args) != 0:
        raise ValueError(f"RFATAL expects 0 arguments, got {len(args)}")

    return Form(
        Atom("PROG"),
        [
            [],
            Form(Atom("PUSH"), [Number(2)]),
            Form(Atom("RSTACK"), [])
        ]
    )


def expand_verb(args: List[Any]) -> Form:
    """Expand VERB? macro.

    <VERB? TAKE> → <EQUAL? ,PRSA ,V?TAKE>
    <VERB? TAKE DROP> → <OR <EQUAL? ,PRSA ,V?TAKE> <EQUAL? ,PRSA ,V?DROP>>

    Args:
        args: List of verb atoms

    Returns:
        EQUAL? form for single verb, OR form for multiple verbs
    """
    if len(args) == 0:
        raise ValueError("VERB? expects at least 1 argument")

    if len(args) == 1:
        # Single verb: <EQUAL? ,PRSA ,V?VERB>
        verb_name = args[0].value if isinstance(args[0], Atom) else str(args[0])
        return Form(
            Atom("EQUAL?"),
            [GlobalRef("PRSA"), GlobalRef(f"V?{verb_name}")]
        )
    else:
        # Multiple verbs: <OR <EQUAL? ...> <EQUAL? ...>>
        comparisons = []
        for verb in args:
            verb_name = verb.value if isinstance(verb, Atom) else str(verb)
            comparisons.append(
                Form(
                    Atom("EQUAL?"),
                    [GlobalRef("PRSA"), GlobalRef(f"V?{verb_name}")]
                )
            )
        return Form(Atom("OR"), comparisons)


def expand_prso(args: List[Any]) -> Form:
    """Expand PRSO? macro.

    <PRSO? LAMP> → <EQUAL? ,PRSO ,LAMP>

    Args:
        args: List containing the object to check

    Returns:
        EQUAL? form checking PRSO
    """
    if len(args) != 1:
        raise ValueError(f"PRSO? expects 1 argument, got {len(args)}")

    obj_name = args[0].value if isinstance(args[0], Atom) else str(args[0])
    return Form(
        Atom("EQUAL?"),
        [GlobalRef("PRSO"), GlobalRef(obj_name)]
    )


def expand_prsi(args: List[Any]) -> Form:
    """Expand PRSI? macro.

    <PRSI? SWORD> → <EQUAL? ,PRSI ,SWORD>

    Args:
        args: List containing the object to check

    Returns:
        EQUAL? form checking PRSI
    """
    if len(args) != 1:
        raise ValueError(f"PRSI? expects 1 argument, got {len(args)}")

    obj_name = args[0].value if isinstance(args[0], Atom) else str(args[0])
    return Form(
        Atom("EQUAL?"),
        [GlobalRef("PRSI"), GlobalRef(obj_name)]
    )


def expand_room(args: List[Any]) -> Form:
    """Expand ROOM? macro.

    <ROOM? LIVING-ROOM> → <EQUAL? ,HERE ,LIVING-ROOM>

    Args:
        args: List containing the room to check

    Returns:
        EQUAL? form checking HERE
    """
    if len(args) != 1:
        raise ValueError(f"ROOM? expects 1 argument, got {len(args)}")

    room_name = args[0].value if isinstance(args[0], Atom) else str(args[0])
    return Form(
        Atom("EQUAL?"),
        [GlobalRef("HERE"), GlobalRef(room_name)]
    )


def expand_bset(args: List[Any]) -> Form:
    """Expand BSET macro.

    <BSET obj FLAG> → <FSET obj ,FLAG>
    <BSET obj F1 F2> → <PROG () <FSET obj ,F1> <FSET obj ,F2>>

    Args:
        args: List containing object followed by flag(s)

    Returns:
        FSET form for single flag, PROG form for multiple flags
    """
    if len(args) < 2:
        raise ValueError(f"BSET expects at least 2 arguments, got {len(args)}")

    obj = args[0]
    flags = args[1:]

    if len(flags) == 1:
        # Single flag: <FSET obj ,FLAG>
        flag_name = flags[0].value if isinstance(flags[0], Atom) else str(flags[0])
        return Form(
            Atom("FSET"),
            [obj, GlobalRef(flag_name)]
        )
    else:
        # Multiple flags: <PROG () <FSET...> <FSET...>>
        fset_forms = []
        for flag in flags:
            flag_name = flag.value if isinstance(flag, Atom) else str(flag)
            fset_forms.append(
                Form(
                    Atom("FSET"),
                    [obj, GlobalRef(flag_name)]
                )
            )
        return Form(Atom("PROG"), [[], *fset_forms])


def expand_bclear(args: List[Any]) -> Form:
    """Expand BCLEAR macro.

    <BCLEAR obj FLAG> → <FCLEAR obj ,FLAG>
    <BCLEAR obj F1 F2> → <PROG () <FCLEAR obj ,F1> <FCLEAR obj ,F2>>

    Args:
        args: List containing object followed by flag(s)

    Returns:
        FCLEAR form for single flag, PROG form for multiple flags
    """
    if len(args) < 2:
        raise ValueError(f"BCLEAR expects at least 2 arguments, got {len(args)}")

    obj = args[0]
    flags = args[1:]

    if len(flags) == 1:
        # Single flag: <FCLEAR obj ,FLAG>
        flag_name = flags[0].value if isinstance(flags[0], Atom) else str(flags[0])
        return Form(
            Atom("FCLEAR"),
            [obj, GlobalRef(flag_name)]
        )
    else:
        # Multiple flags: <PROG () <FCLEAR...> <FCLEAR...>>
        fclear_forms = []
        for flag in flags:
            flag_name = flag.value if isinstance(flag, Atom) else str(flag)
            fclear_forms.append(
                Form(
                    Atom("FCLEAR"),
                    [obj, GlobalRef(flag_name)]
                )
            )
        return Form(Atom("PROG"), [[], *fclear_forms])


def expand_bset_question(args: List[Any]) -> Form:
    """Expand BSET? macro.

    <BSET? obj FLAG> → <FSET? obj ,FLAG>
    <BSET? obj F1 F2> → <OR <FSET? obj ,F1> <FSET? obj ,F2>>

    Args:
        args: List containing object followed by flag(s)

    Returns:
        FSET? form for single flag, OR form for multiple flags
    """
    if len(args) < 2:
        raise ValueError(f"BSET? expects at least 2 arguments, got {len(args)}")

    obj = args[0]
    flags = args[1:]

    if len(flags) == 1:
        # Single flag: <FSET? obj ,FLAG>
        flag_name = flags[0].value if isinstance(flags[0], Atom) else str(flags[0])
        return Form(
            Atom("FSET?"),
            [obj, GlobalRef(flag_name)]
        )
    else:
        # Multiple flags: <OR <FSET?...> <FSET?...>>
        fset_checks = []
        for flag in flags:
            flag_name = flag.value if isinstance(flag, Atom) else str(flag)
            fset_checks.append(
                Form(
                    Atom("FSET?"),
                    [obj, GlobalRef(flag_name)]
                )
            )
        return Form(Atom("OR"), fset_checks)


def expand_flaming(args: List[Any]) -> Form:
    """Expand FLAMING? macro.

    <FLAMING? obj> → <AND <FSET? obj ,FLAMEBIT> <FSET? obj ,ONBIT>>

    Args:
        args: List containing the object to check

    Returns:
        AND form checking both FLAMEBIT and ONBIT
    """
    if len(args) != 1:
        raise ValueError(f"FLAMING? expects 1 argument, got {len(args)}")

    obj = args[0]
    return Form(
        Atom("AND"),
        [
            Form(Atom("FSET?"), [obj, GlobalRef("FLAMEBIT")]),
            Form(Atom("FSET?"), [obj, GlobalRef("ONBIT")])
        ]
    )


def expand_openable(args: List[Any]) -> Form:
    """Expand OPENABLE? macro.

    <OPENABLE? obj> → <OR <FSET? obj ,DOORBIT> <FSET? obj ,CONTBIT>>

    Args:
        args: List containing the object to check

    Returns:
        OR form checking DOORBIT or CONTBIT
    """
    if len(args) != 1:
        raise ValueError(f"OPENABLE? expects 1 argument, got {len(args)}")

    obj = args[0]
    return Form(
        Atom("OR"),
        [
            Form(Atom("FSET?"), [obj, GlobalRef("DOORBIT")]),
            Form(Atom("FSET?"), [obj, GlobalRef("CONTBIT")])
        ]
    )


def expand_abs(args: List[Any]) -> Form:
    """Expand ABS macro.

    <ABS num> → <COND (<L? num 0> <- 0 num>) (T num)>

    Args:
        args: List containing the number expression

    Returns:
        COND form that returns absolute value
    """
    if len(args) != 1:
        raise ValueError(f"ABS expects 1 argument, got {len(args)}")

    num = args[0]
    return Form(
        Atom("COND"),
        [
            [
                Form(Atom("L?"), [num, Number(0)]),
                Form(Atom("-"), [Number(0), num])
            ],
            [Atom("T"), num]
        ]
    )


def expand_prob(args: List[Any]) -> Form:
    """Expand PROB macro.

    <PROB n> → <G? n <RANDOM 100>>
    <PROB n loser> → <ZPROB n>   (when optional LOSER? arg present)

    Args:
        args: List containing the probability threshold and optional loser flag

    Returns:
        G? form comparing threshold to random number, or ZPROB form
    """
    if len(args) < 1:
        raise ValueError(f"PROB expects at least 1 argument, got {len(args)}")

    threshold = args[0]

    # When optional LOSER? argument is present, use ZPROB routine
    if len(args) >= 2:
        return Form(Atom("ZPROB"), [threshold])

    return Form(
        Atom("G?"),
        [threshold, Form(Atom("RANDOM"), [Number(100)])]
    )
