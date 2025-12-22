from enum import IntEnum


class AnalyzerMode(IntEnum):
    MSequence = (0, "M-Sequences")
    ProcessData = (1, "ProcessData")
    Diagnosis = (2, "Diagnosis")
    Page = (3, "Page")
    ISDU = (4, "ISDU")

    def __new__(cls, value, description):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj

    @staticmethod
    def descriptions():
        return [mode.description for mode in sorted(AnalyzerMode, key=lambda m: m.value)]

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value_norm = value.strip().lower()
            for member in cls:
                if member.description.lower() == value_norm:
                    return member

        raise ValueError(f"{value!r} is not a valid {cls.__name__}")