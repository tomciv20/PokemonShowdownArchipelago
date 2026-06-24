from typing import Dict

ITEM_ID_BASE = 386000


def item_name(species: str) -> str:
    return f"Unlock {species.replace('-', ' ').title()}"


def nature_item_name(nature: str) -> str:
    return f"Unlock {nature.title()} Nature"


def popular_item_name(item: str) -> str:
    return "Unlock " + item.replace("-", " ").title()


def get_item_table(species_pool: list) -> Dict[str, int]:
    return {item_name(s): ITEM_ID_BASE + i for i, s in enumerate(species_pool)}


FILLER_ITEMS = {"Bonus PP": ITEM_ID_BASE - 1}


def get_full_item_table() -> Dict[str, int]:
    from .pokemon_data import ALL_POKEMON, CHAMPIONS_POKEMON, NATURES, POPULAR_ITEMS
    seen, full = set(), []
    for s in ALL_POKEMON + CHAMPIONS_POKEMON:
        if s not in seen:
            seen.add(s)
            full.append(s)
    table = {**FILLER_ITEMS, **get_item_table(full)}
    offset = len(full)
    for i, n in enumerate(NATURES):
        table[nature_item_name(n)] = ITEM_ID_BASE + offset + i
    offset += len(NATURES)
    for i, it in enumerate(POPULAR_ITEMS):
        table[popular_item_name(it)] = ITEM_ID_BASE + offset + i
    return table
