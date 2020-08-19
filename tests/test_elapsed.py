from contextlib import redirect_stdout
from io import StringIO

from jashin import elapsed


def test_elapsed() -> None:

    e = elapsed.Elapsed()

    def test() -> None:
        a = 1
        for i in range(10):
            with e("block1"):
                a += 1
                for j in range(10):
                    with e("block2"):
                        a += 1

                for k in range(20):
                    e.begin("block3")
                    a += 1
                    e.end()

    test()

    assert e._map["block1"][1] == 10
    assert e._map["block2"][1] == 100
    assert e._map["block3"][1] == 200

    e.print()

    f = StringIO()
    with redirect_stdout(f):
        e.print()

    s = f.getvalue().strip().split("\n")
    assert len(s) == 3

    f = StringIO()
    with redirect_stdout(f):
        e.print("block1")

    s = f.getvalue().strip().split("\n")
    assert len(s) == 1

    f = StringIO()
    with redirect_stdout(f):
        e.print("block-not-exists")

    s = f.getvalue().strip().split("\n")
    assert len(s) == 1
