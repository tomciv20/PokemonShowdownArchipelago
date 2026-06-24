from dataclasses import dataclass
from Options import Choice, Range, Toggle, PerGameCommonOptions


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
    """How many Pokémon species are in your pool.
    The actual cap depends on which pools are enabled."""
    display_name = "Pool Size"
    range_start = 40
    range_end = 450
    default = 150


class PoolSource(Choice):
    """Which Pokémon to draw from for your species pool.
    gen9_ou: Gen 9 OU-legal fully evolved Pokémon (Paldea dex, not Uber/AG).
    pokemon_champions: Pokémon Champions Regulation M-A + M-B legal species.
    both: Combined pool from both sources."""
    display_name = "Pool Source"
    option_gen9_ou = 0
    option_pokemon_champions = 1
    option_both = 2
    default = 0


class IncludeLegendaries(Toggle):
    """Include legendary Pokémon (applies to gen9_ou and both pool sources)."""
    display_name = "Include Legendaries"
    default = 1


class IncludeMythicals(Toggle):
    """Include mythical Pokémon (applies to gen9_ou and both pool sources)."""
    display_name = "Include Mythicals"
    default = 0


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
    """If enabled, a Pokémon must have been switched into battle to count as a check — being on the team sheet is not enough."""
    display_name = "Require Send Out"
    default = 0


class RequireKill(Toggle):
    """If enabled, you must also get at least one KO with a Pokémon to check it off, not just win with it on your team."""
    display_name = "Require Kill"
    default = 0


@dataclass
class ShowdownOptions(PerGameCommonOptions):
    starting_pokemon_count: StartingPokemonCount
    goal_percentage: GoalPercentage
    pool_size: PoolSize
    pool_source: PoolSource
    include_legendaries: IncludeLegendaries
    include_mythicals: IncludeMythicals
    include_natures: IncludeNatures
    starting_natures_count: StartingNaturesCount
    include_popular_items: IncludePopularItems
    require_send_out: RequireSendOut
    require_kill: RequireKill
