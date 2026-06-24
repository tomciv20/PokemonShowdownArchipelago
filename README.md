# Pokémon Showdown — Archipelago World

An [Archipelago](https://archipelago.gg) multiworld integration for [Pokémon Showdown](https://pokemonshowdown.com).

Win battles on Pokémon Showdown using unlocked species to send checks to other players' games. Receive Pokémon unlocks from the multiworld as other players complete their own goals.

---

## How It Works

- **Items you receive:** `Unlock [Species]` — adds a Pokémon to your usable roster
- **Checks you send:** `Win with [Species]` — win a Showdown battle with that Pokémon on your team
- **Goal:** Win battles with a configurable percentage of your species pool (default 80%)
- **Validation:** Submit a Showdown replay URL; the client parses it automatically to verify your win and legal species usage

You play on the honor system — only use Pokémon (and natures/items, if those options are on) that you have unlocked.

---

## Installation

### Requirements
- [Archipelago 0.6.0+](https://github.com/ArchipelagoMW/Archipelago/releases)

### Steps

1. Download `PokemonShowdown.apworld` from the [Releases](../../releases) page
2. Place it in your Archipelago `custom_worlds` folder:
   - Windows: `C:\ProgramData\Archipelago\custom_worlds\`
3. Copy `PokemonShowdown.yaml` to your Archipelago folder and edit it with your settings
4. Generate a multiworld using the Archipelago Launcher as normal

---

## Playing

1. Open the **Archipelago Launcher**
2. Click **Pokémon Showdown Client**
3. Connect to your Archipelago server (e.g. `archipelago.gg:12345`)
4. Enter your slot name when prompted — **this must match your Pokémon Showdown username exactly**
5. Play battles on Pokémon Showdown using only your unlocked species
6. After winning, copy the replay URL and submit it with `/submit <url>`

### Client Commands

| Command | Description |
|---|---|
| `/submit <url>` | Submit a Showdown replay URL to check for new location checks |
| `/progress` | Show how many species you've won with toward your goal |
| `/unlocked` | List all currently unlocked Pokémon species |
| `/natures` | List unlocked natures (if natures option is on) |
| `/locked-natures` | List natures you haven't unlocked yet |
| `/items` | List unlocked competitive items (if items option is on) |
| `/locked-items` | List competitive items you haven't unlocked yet |
| `/achievements` | Show active achievement goals and which are completed |

---

## Configuration Options

Edit `PokemonShowdown.yaml` to customize your experience. All options support Archipelago's weighted random system.

### Core Options

| Option | Default | Description |
|---|---|---|
| `starting_pokemon_count` | 6 | How many Pokémon you start with unlocked |
| `goal_percentage` | 80 | % of your pool you need to win with to complete your goal |
| `pool_size` | 150 | Number of Pokémon species in your pool |
| `pool_source` | `gen9_ou` | Which Pokémon to draw from (`gen9_ou`, `pokemon_champions`, or `both`) |
| `include_legendaries` | on | Include legendaries in the gen9_ou pool |
| `include_mythicals` | off | Include mythicals in the gen9_ou pool |

### Pool Sources

- **`gen9_ou`** — Gen 9 OU-legal fully evolved Pokémon from the Paldea dex (not Uber/AG). Legendaries and mythicals controlled separately.
- **`pokemon_champions`** — Pokémon Champions Regulation M-A and M-B legal species, spanning all generations.
- **`both`** — Combined pool from both sources, giving the largest possible variety.

### Bonus Options & Achievement System

| Option | Default | Description |
|---|---|---|
| `include_natures` | off | Add all 25 natures as unlock items. Honor system: only use natures you've received. |
| `starting_natures_count` | 1 | How many natures you start with (rest must be received) |
| `include_popular_items` | off | Add 15 competitive items as unlocks (Air Balloon, Choice Band, Focus Sash, etc.) |
| `require_send_out` | off | Pokémon must be switched into battle to count as a check |
| `require_kill` | off | You must get at least one KO with a Pokémon for it to count |

#### How Natures & Items Fit Into the Pool

Natures and popular items first **replace filler slots** in your item pool (the Bonus PP items you'd otherwise receive for your starting Pokémon). If there are more bonus items than filler slots, the overflow creates **achievement-style locations** added to your world — things like:

- Win 5 / 10 / 15 / ... / 50 battles
- Win a battle without any of your Pokémon fainting
- Win with 3 or fewer Pokémon sent out
- One-hit KO a Pokémon
- Deal 69% damage in one hit
- Win a battle using specific moves (Trick Room, Stealth Rock, Explosion, etc.)
- Win a battle in 10 / 12 / 14 / 16 / 18 turns or fewer
- One Pokémon gets 3 or 4 KOs in a single battle
- Win 2 or 3 battles in a row

Achievements are chosen randomly each seed from a pool of 43 possible goals and are **tracked automatically** by the client when you submit replays. Use `/achievements` to see which ones are active for your seed.

Enabling natures and items does **not** reduce your species count — your Pokémon pool stays the same size.

---

## Building from Source

If you want to modify the apworld yourself:

1. Clone this repository
2. Make your changes inside the `PokemonShowdown/` folder
3. Zip the `PokemonShowdown/` folder so that the files are inside a `PokemonShowdown/` subdirectory in the archive:

**Windows (PowerShell):**
```powershell
$src = "path\to\PokemonShowdown"
$out = "path\to\PokemonShowdown.apworld"

Remove-Item $out -ErrorAction SilentlyContinue
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::Open($out, 'Create')
Get-ChildItem $src -File | ForEach-Object {
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $_.FullName, "PokemonShowdown/$($_.Name)") | Out-Null
}
$zip.Dispose()
```

**Important:** The zip must contain files under a `PokemonShowdown/` subfolder (e.g. `PokemonShowdown/__init__.py`), not at the root. This is required by Archipelago's apworld loader.

4. Place the resulting `PokemonShowdown.apworld` in your `custom_worlds` folder

---

## Notes

- Your Archipelago slot name **must match your Pokémon Showdown username exactly** (case-insensitive). The client reads your name from the replay to verify you were a participant and identify which side you played.
- Replays must be publicly accessible on `replay.pokemonshowdown.com`.
- The same replay URL can be submitted multiple times safely — already-checked locations are ignored.
- Win streaks and battle counts for achievement milestones are saved automatically and persist across client restarts, stored in `~/Archipelago/showdown_stats/`.
