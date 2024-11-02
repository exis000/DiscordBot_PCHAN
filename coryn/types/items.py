from enum import Enum, auto


class Items(Enum):
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list) -> int:  # noqa: ARG004
        if name in ("HALBERD", "KATANA", "NINJUTSU_SCROLL"):
            return count + 1
        return count

    ALL = auto()
    USABLE = auto()
    REFINEMENT_SUPPORT = auto()
    PIERCER = auto()
    ONE_HANDED_SWORD = auto()
    TWO_HANDED_SWORD = auto()
    ADDITIONAL = auto()
    ARROW = auto()
    ARMOR = auto()
    BOW = auto()
    BOWGUN = auto()
    DAGGER = auto()
    GEM = auto()
    KNUCKLES = auto()
    MATERIAL = auto()
    MAGIC_DEVICE = auto()
    ORE = auto()
    SHIELD = auto()
    SPECIAL = auto()
    STAFF = auto()
    NORMAL_CRYSTA = auto()
    WEAPON_CRYSTA = auto()
    ARMOR_CRYSTA = auto()
    ADDITIONAL_CRYSTA = auto()
    SPECIAL_CRYSTA = auto()
    HALBERD = auto()
    KATANA = auto()
    NINJUTSU_SCROLL = auto()
