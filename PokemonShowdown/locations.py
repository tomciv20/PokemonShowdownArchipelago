from typing import Dict

LOCATION_ID_BASE = 386000
ACHIEVEMENT_LOCATION_BASE = 387000


def location_name(species: str) -> str:
    return f"Win with {species.replace('-', ' ').title()}"


def get_location_table(species_pool: list) -> Dict[str, int]:
    return {location_name(s): LOCATION_ID_BASE + i for i, s in enumerate(species_pool)}


def get_achievement_location_table() -> Dict[str, int]:
    from .pokemon_data import ACHIEVEMENTS
    return {ach: ACHIEVEMENT_LOCATION_BASE + i for i, ach in enumerate(ACHIEVEMENTS)}
