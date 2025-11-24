"Simple test game"

<GLOBAL SCORE 0>

<OBJECT ROOM
    (DESC "a small room")>

<OBJECT LAMP
    (IN ROOM)
    (SYNONYM LAMP LANTERN)
    (DESC "brass lamp")>

<ROUTINE V-LOOK ()
    <TELL "You are in a small room." CR>>

<ROUTINE V-TAKE ()
    <TELL "Taken." CR>>

<ROUTINE V-INVENTORY ()
    <TELL "You are carrying nothing." CR>>
