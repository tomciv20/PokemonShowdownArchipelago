from worlds.AutoWorld import World
from .items import item_name
from .locations import location_name


def set_rules(world: World, species_pool: list) -> None:
    for species in species_pool:
        loc = world.multiworld.get_location(location_name(species), world.player)
        unlock = item_name(species)
        loc.access_rule = lambda state, item=unlock: state.has(item, world.player)
