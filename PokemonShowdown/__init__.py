from typing import List, Dict, Any

from BaseClasses import Item, ItemClassification, Location, Region, Tutorial
from worlds.AutoWorld import World, WebWorld

from .items import (item_name, nature_item_name, popular_item_name,
                    get_item_table, get_full_item_table, ITEM_ID_BASE, FILLER_ITEMS)
from .locations import (location_name, get_location_table, get_achievement_location_table,
                        LOCATION_ID_BASE, ACHIEVEMENT_LOCATION_BASE)
from .options import ShowdownOptions
from .pokemon_data import (OU_POKEMON, UU_POKEMON, RU_POKEMON, NU_POKEMON, PU_POKEMON,
                            CHAMPIONS_POKEMON, NATURES, POPULAR_ITEMS, ACHIEVEMENTS)


class ShowdownItem(Item):
    game = "Pokemon Showdown"


class ShowdownLocation(Location):
    game = "Pokemon Showdown"


class ShowdownWebWorld(WebWorld):
    theme = "ocean"
    tutorials = []


class ShowdownWorld(World):
    """
    Pokémon Showdown Archipelago integration. Win battles using unlocked Pokémon
    to send items to other players' games. Receive Pokémon unlocks from other players.
    """

    game = "Pokemon Showdown"
    options_dataclass = ShowdownOptions
    options: ShowdownOptions
    web = ShowdownWebWorld()

    item_name_to_id: Dict[str, int] = {}
    location_name_to_id: Dict[str, int] = {}

    @classmethod
    def _load_tables(cls):
        cls.item_name_to_id = get_full_item_table()
        seen, full = set(), []
        all_lists = OU_POKEMON + UU_POKEMON + RU_POKEMON + NU_POKEMON + PU_POKEMON + CHAMPIONS_POKEMON
        for s in all_lists:
            if s not in seen:
                seen.add(s)
                full.append(s)
        cls.location_name_to_id = {
            **get_location_table(full),
            **get_achievement_location_table(),
        }

    def _build_species_pool(self) -> List[str]:
        seen, pool = set(), []

        def add(lst):
            for s in lst:
                if s not in seen:
                    seen.add(s)
                    pool.append(s)

        if self.options.include_ou:
            add(OU_POKEMON)
        if self.options.include_uu:
            add(UU_POKEMON)
        if self.options.include_ru:
            add(RU_POKEMON)
        if self.options.include_nu:
            add(NU_POKEMON)
        if self.options.include_pu:
            add(PU_POKEMON)
        if self.options.include_champions:
            add(CHAMPIONS_POKEMON)

        size = min(self.options.pool_size.value, len(pool))
        return self.random.sample(pool, size)

    def generate_early(self) -> None:
        self.species_pool = self._build_species_pool()
        n = len(self.species_pool)

        self.starters_count = min(self.options.starting_pokemon_count.value, n)

        # Determine starting natures now so create_items and create_regions agree.
        self.starting_natures: List[str] = []
        if self.options.include_natures:
            sn = min(self.options.starting_natures_count.value, len(NATURES))
            self.starting_natures = self.random.sample(NATURES, sn)

        filler_slots = self.starters_count + len(self.starting_natures)

        # Build the ordered list of non-precollected bonus items.
        starting_nat_names = {nature_item_name(nat) for nat in self.starting_natures}
        bonus: List[str] = []
        if self.options.include_natures:
            bonus += [nature_item_name(nat) for nat in NATURES
                      if nature_item_name(nat) not in starting_nat_names]
        if self.options.include_popular_items:
            bonus += [popular_item_name(it) for it in POPULAR_ITEMS]
        self.random.shuffle(bonus)

        bonus_in_filler = min(len(bonus), filler_slots)
        overflow = len(bonus) - bonus_in_filler
        ach_count = min(overflow, len(ACHIEVEMENTS))

        self.bonus_in_filler: List[str] = bonus[:bonus_in_filler]
        self.bonus_in_achievement: List[str] = bonus[bonus_in_filler:bonus_in_filler + ach_count]
        self.selected_achievements: List[str] = (
            self.random.sample(ACHIEVEMENTS, ach_count) if ach_count > 0 else []
        )

        # Species items = n minus the filler slots (starters PP + starting_natures PP).
        # Bonus items only swap out those PP slots and fill achievement slots — species count
        # is unaffected, keeping goal calculation stable.
        self.species_item_count = n - filler_slots

    def create_items(self) -> None:
        pool = self.species_pool
        n = len(pool)

        # Precollect starters.
        starters = set(self.random.sample(pool, self.starters_count))
        for s in starters:
            self.multiworld.push_precollected(self.create_item(item_name(s)))

        # Precollect starting natures.
        for nat in self.starting_natures:
            self.multiworld.push_precollected(self.create_item(nature_item_name(nat)))

        filler_slots = self.starters_count + len(self.starting_natures)
        pp_count = filler_slots - len(self.bonus_in_filler)

        non_starters = [s for s in pool if s not in starters]
        species_items = [item_name(s) for s in non_starters[:self.species_item_count]]

        item_list: List[str] = (
            ["Bonus PP"] * pp_count
            + list(self.bonus_in_filler)
            + species_items
            + list(self.bonus_in_achievement)
        )

        # Safety pad (should never be needed).
        total_locs = n + len(self.selected_achievements)
        while len(item_list) < total_locs:
            item_list.append("Bonus PP")

        for iname in item_list:
            self.multiworld.itempool.append(self.create_item(iname))

    def create_regions(self) -> None:
        menu = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(menu)

        main = Region("Showdown", self.player, self.multiworld)
        self.multiworld.regions.append(main)

        for species in self.species_pool:
            loc = ShowdownLocation(self.player, location_name(species),
                                   self.location_name_to_id[location_name(species)], main)
            main.locations.append(loc)

        ach_table = get_achievement_location_table()
        for ach in self.selected_achievements:
            loc = ShowdownLocation(self.player, ach, ach_table[ach], main)
            main.locations.append(loc)

        menu.connect(main)

    def set_rules(self) -> None:
        from .rules import set_rules as apply_rules
        apply_rules(self, self.species_pool)
        goal_pct = max(1, round(len(self.species_pool) * self.options.goal_percentage.value / 100))
        goal_count = min(goal_pct, self.species_item_count)
        self.multiworld.completion_condition[self.player] = lambda state: sum(
            state.has(item_name(s), self.player) for s in self.species_pool
        ) >= goal_count

    def get_filler_item_name(self) -> str:
        return "Bonus PP"

    def create_item(self, name: str) -> ShowdownItem:
        if name == "Bonus PP":
            classification = ItemClassification.filler
        elif name.endswith(" Nature"):
            classification = ItemClassification.useful
        else:
            inner = name[len("Unlock "):] if name.startswith("Unlock ") else ""
            if inner.replace(" ", "-").lower() in POPULAR_ITEMS:
                classification = ItemClassification.useful
            else:
                classification = ItemClassification.progression
        return ShowdownItem(name, classification, self.item_name_to_id[name], self.player)

    def fill_slot_data(self) -> Dict[str, Any]:
        goal_pct = max(1, round(len(self.species_pool) * self.options.goal_percentage.value / 100))
        goal_count = min(goal_pct, self.species_item_count)
        ach_table = get_achievement_location_table()
        return {
            "species_pool": self.species_pool,
            "goal_count": goal_count,
            "require_send_out": bool(self.options.require_send_out.value),
            "require_kill": bool(self.options.require_kill.value),
            "include_natures": bool(self.options.include_natures.value),
            "include_popular_items": bool(self.options.include_popular_items.value),
            "active_achievements": {ach: ach_table[ach] for ach in self.selected_achievements},
        }


ShowdownWorld._load_tables()


# --- Launcher integration ---

def _launch_showdown_client(*args: str) -> None:
    from worlds import LauncherComponents
    from .client import run_showdown_client
    LauncherComponents.launch(run_showdown_client, name="Pokemon Showdown Client", args=args)


def _register_launcher_component() -> None:
    try:
        from worlds.LauncherComponents import Component, components
        components.append(Component(
            display_name="Pokemon Showdown Client",
            func=_launch_showdown_client,
            description="Submit Showdown replays to send location checks.",
        ))
    except Exception:
        pass


_register_launcher_component()
