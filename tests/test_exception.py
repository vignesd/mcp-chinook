def one():
    try:
        int("abc")
    except ValueError:
        raise RuntimeError("INVALID_ARGUMENT: Invalid album ID.")


def two():
    try:
        int("abc")
    except ValueError as exc:
        raise RuntimeError(
            "INVALID_ARGUMENT: Invalid album ID."
        ) from exc


def three():
    try:
        int("abc")
    except ValueError:
        raise RuntimeError(
            "INVALID_ARGUMENT: Invalid album ID."
        ) from None


if __name__ == "__main__":
    # one()
    # print("+"*50)
    # two()
    # print("+"*50)
    three()
