from dataclasses import dataclass
from Options import Range, Toggle, PerGameCommonOptions


class StartingPokemonCount(Range):
    """Number of Pokémon you start the game with unlocked."""
    display_name = "Starting Pokémon Count"
    range_start = 6
    range_end = 20
    default = 6


class GoalPercentage(Range):
    """Percentage of your Pokémon pool you need to win with to complete your goal."""
    display_name = "Goal Percentage"
    range_start = 10
    range_end = 100
    default = 80


class PoolSize(Range):
    """How many Pokémon species are in your pool (randomly sampled from enabled tiers)."""
    display_name = "Pool Size"
    range_start = 10
    range_end = 450
    default = 50


class IncludeOU(Toggle):
    """Include Gen 9 OU-tier Pokémon in the pool."""
    display_name = "Include OU"
    default = 1


class IncludeUU(Toggle):
    """Include Gen 9 UU-tier Pokémon in the pool."""
    display_name = "Include UU"
    default = 0


class IncludeRU(Toggle):
    """Include Gen 9 RU-tier Pokémon in the pool."""
    display_name = "Include RU"
    default = 0


class IncludeNU(Toggle):
    """Include Gen 9 NU-tier Pokémon in the pool."""
    display_name = "Include NU"
    default = 0


class IncludePU(Toggle):
    """Include Gen 9 PU-tier Pokémon in the pool."""
    display_name = "Include PU"
    default = 0


class IncludeChampions(Toggle):
    """Include Pokémon Champions Regulation M-A/M-B legal species in the pool."""
    display_name = "Include Champions"
    default = 0


class IncludeLegendaries(Toggle):
    """Include legendary and mythical Pokémon from the enabled tiers."""
    display_name = "Include Legendaries"
    default = 1


class IncludeNatures(Toggle):
    """Add all 25 natures as unlock items. You must use only unlocked natures (honor system)."""
    display_name = "Include Natures"
    default = 0


class StartingNaturesCount(Range):
    """How many natures you start with unlocked (only applies if Include Natures is on)."""
    display_name = "Starting Natures Count"
    range_start = 1
    range_end = 5
    default = 1


class IncludePopularItems(Toggle):
    """Add popular competitive items as unlock items. You must use only unlocked items (honor system)."""
    display_name = "Include Popular Items"
    default = 0


class RequireSendOut(Toggle):
    """If enabled, a Pokémon must have been switched into battle to count as a check."""
    display_name = "Require Send Out"
    default = 0


class RequireKill(Toggle):
    """If enabled, you must get at least one KO with a Pokémon to check it off."""
    display_name = "Require Kill"
    default = 0


@dataclass
class ShowdownOptions(PerGameCommonOptions):
    starting_pokemon_count: StartingPokemonCount
    goal_percentage: GoalPercentage
    pool_size: PoolSize
    include_ou: IncludeOU
    include_uu: IncludeUU
    include_ru: IncludeRU
    include_nu: IncludeNU
    include_pu: IncludePU
    include_champions: IncludeChampions
    include_legendaries: IncludeLegendaries
    include_natures: IncludeNatures
    starting_natures_count: StartingNaturesCount
    include_popular_items: IncludePopularItems
    require_send_out: RequireSendOut
    require_kill: RequireKill
