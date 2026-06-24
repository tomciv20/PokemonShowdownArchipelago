from __future__ import annotations

import asyncio
import json
import re
import urllib.request
from pathlib import Path

_STATS_DIR = Path.home() / "Archipelago" / "showdown_stats"


def _stats_path(slot: str, server: str) -> Path:
    safe = re.sub(r"[^\w.-]", "_", f"{slot}_{server}")
    return _STATS_DIR / f"{safe}.json"


def _load_stats(slot: str, server: str) -> dict:
    try:
        return json.loads(_stats_path(slot, server).read_text())
    except Exception:
        return {"session_wins": 0, "session_streak": 0}


def _save_stats(slot: str, server: str, wins: int, streak: int) -> None:
    try:
        _STATS_DIR.mkdir(parents=True, exist_ok=True)
        _stats_path(slot, server).write_text(
            json.dumps({"session_wins": wins, "session_streak": streak})
        )
    except Exception:
        pass

from CommonClient import CommonContext, gui_enabled, server_loop, console_loop, ClientCommandProcessor, logger

try:
    from NetUtils import ClientStatus
except Exception:
    ClientStatus = None  # type: ignore

# Build plain-dict name tables from the World's ID tables so we don't depend on NameLookupDict.
def _build_name_tables():
    try:
        from worlds.PokemonShowdown import ShowdownWorld
        item_id_to_name = {v: k for k, v in ShowdownWorld.item_name_to_id.items()}
        loc_id_to_name = {v: k for k, v in ShowdownWorld.location_name_to_id.items()}
        return item_id_to_name, loc_id_to_name
    except Exception:
        return {}, {}

_ITEM_ID_TO_NAME, _LOC_ID_TO_NAME = _build_name_tables()
_LOC_NAME_TO_ID = {v: k for k, v in _LOC_ID_TO_NAME.items()}

_FORME_MAP = {
    "shaymin-sky": "shaymin",
    "arceus-ground": "arceus", "arceus-fire": "arceus", "arceus-water": "arceus",
    "arceus-electric": "arceus", "arceus-grass": "arceus", "arceus-ice": "arceus",
    "arceus-fighting": "arceus", "arceus-poison": "arceus", "arceus-psychic": "arceus",
    "arceus-ghost": "arceus", "arceus-dragon": "arceus", "arceus-dark": "arceus",
    "arceus-steel": "arceus", "arceus-fairy": "arceus", "arceus-flying": "arceus",
    "arceus-bug": "arceus", "arceus-rock": "arceus",
    "calyrex-ice": "calyrex", "calyrex-shadow": "calyrex",
    "oricorio-pom-pom": "oricorio", "oricorio-pau": "oricorio", "oricorio-sensu": "oricorio",
    "lycanroc-midnight": "lycanroc", "lycanroc-dusk": "lycanroc",
    "toxtricity-low-key": "toxtricity",
    "indeedee-f": "indeedee",
    "morpeko-hangry": "morpeko",
    "eiscue-noice": "eiscue",
    "gourgeist-small": "gourgeist", "gourgeist-large": "gourgeist", "gourgeist-super": "gourgeist",
    "tatsugiri-droopy": "tatsugiri", "tatsugiri-stretchy": "tatsugiri",
    "maushold-four": "maushold",
    "squawkabilly-blue": "squawkabilly", "squawkabilly-yellow": "squawkabilly",
    "squawkabilly-white": "squawkabilly",
    "palafin-hero": "palafin",
    "rotom-heat": "rotom", "rotom-wash": "rotom", "rotom-frost": "rotom",
    "rotom-fan": "rotom", "rotom-mow": "rotom",
    "urshifu-rapid-strike": "urshifu-rapid-strike",
    "tauros-paldea-combat": "tauros-paldea-combat",
    "tauros-paldea-blaze": "tauros-paldea-blaze",
    "tauros-paldea-aqua": "tauros-paldea-aqua",
}


def _normalize(raw: str) -> str:
    key = raw.strip().lower().replace(" ", "-")
    return _FORME_MAP.get(key, key)


def _loc_name(species: str) -> str:
    return "Win with " + species.replace("-", " ").title()


def _parse_hp_field(hp_field: str):
    """Return (current, max) from '150/300' or '0 fnt' or '150/300 brn'. max is None for faint."""
    token = hp_field.split()[0]
    if "/" in token:
        cur, mx = token.split("/")
        return int(cur), int(mx)
    return int(token), None


class ShowdownCommandProcessor(ClientCommandProcessor):
    def _cmd_submit(self, url: str = "") -> None:
        """Submit a Showdown replay URL. Usage: /submit https://replay.pokemonshowdown.com/..."""
        url = url.strip().rstrip("/")
        if not url.endswith(".json"):
            url += ".json"
        asyncio.create_task(self.ctx.fetch_and_process(url))

    def _cmd_unlocked(self) -> None:
        """List all currently unlocked Pokemon."""
        ctx = self.ctx
        if ctx.unlocked:
            self.output(f"Unlocked ({len(ctx.unlocked)}): {', '.join(sorted(ctx.unlocked))}")
        else:
            self.output("No Pokemon unlocked yet.")

    def _cmd_natures(self) -> None:
        """List all currently unlocked natures."""
        from .pokemon_data import NATURES
        ctx = self.ctx
        if ctx.unlocked_natures:
            self.output(f"Unlocked natures ({len(ctx.unlocked_natures)}/{len(NATURES)}): {', '.join(sorted(ctx.unlocked_natures))}")
        else:
            self.output("No natures unlocked yet.")

    def _cmd_locked_natures(self) -> None:
        """List natures not yet unlocked."""
        from .pokemon_data import NATURES
        ctx = self.ctx
        locked = sorted(n for n in NATURES if n not in ctx.unlocked_natures)
        if locked:
            self.output(f"Locked natures ({len(locked)}): {', '.join(locked)}")
        else:
            self.output("All natures unlocked!")

    def _cmd_items(self) -> None:
        """List all currently unlocked competitive items."""
        from .pokemon_data import POPULAR_ITEMS
        ctx = self.ctx
        if ctx.unlocked_items:
            self.output(f"Unlocked items ({len(ctx.unlocked_items)}/{len(POPULAR_ITEMS)}): {', '.join(sorted(ctx.unlocked_items))}")
        else:
            self.output("No items unlocked yet.")

    def _cmd_locked_items(self) -> None:
        """List competitive items not yet unlocked."""
        from .pokemon_data import POPULAR_ITEMS
        ctx = self.ctx
        locked = sorted(it for it in POPULAR_ITEMS if it not in ctx.unlocked_items)
        if locked:
            self.output(f"Locked items ({len(locked)}): {', '.join(locked)}")
        else:
            self.output("All items unlocked!")

    def _cmd_progress(self) -> None:
        """Show win progress toward goal."""
        ctx = self.ctx
        suffix = " (kill required)" if ctx.require_kill else ""
        self.output(f"Progress: {len(ctx.won)}/{ctx.goal_count or '?'} species won with{suffix}.")

    def _cmd_achievements(self) -> None:
        """Show active achievements and which are checked."""
        ctx = self.ctx
        if not ctx.active_achievements:
            self.output("No achievements in this session (no overflow bonus items).")
            return
        lines = []
        done_count = 0
        for name, loc_id in ctx.active_achievements.items():
            done = loc_id in ctx.checked_locations
            if done:
                done_count += 1
            lines.append(f"  {'[x]' if done else '[ ]'} {name}")
        self.output(f"Achievements ({done_count}/{len(ctx.active_achievements)}):\n" + "\n".join(lines))


class ShowdownContext(CommonContext):
    game = "Pokemon Showdown"
    items_handling = 0b111

    def __init__(self, server_address, password):
        super().__init__(server_address, password)
        self.command_processor = ShowdownCommandProcessor
        self.unlocked: set = set()
        self.unlocked_natures: set = set()
        self.unlocked_items: set = set()
        self.won: set = set()
        self.goal_count: int = 0
        self.goal_sent: bool = False
        self.require_send_out: bool = False
        self.require_kill: bool = False
        self.active_achievements: dict = {}

        # Session-scoped stats (reset each client restart).
        self.session_wins: int = 0
        self.session_streak: int = 0

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict):
        super().on_package(cmd, args)

        if cmd == "Connected":
            slot_data = args.get("slot_data", {})
            self.goal_count = slot_data.get("goal_count", 0)
            self.require_send_out = slot_data.get("require_send_out", False)
            self.require_kill = slot_data.get("require_kill", False)
            self.active_achievements = slot_data.get("active_achievements", {})
            for loc_id in args.get("checked_locations", []):
                name = _LOC_ID_TO_NAME.get(loc_id, "")
                if name.startswith("Win with "):
                    self.won.add(_normalize(name[len("Win with "):]))
            # Load persistent win stats for this slot+server.
            server_key = self.server_address or "local"
            stats = _load_stats(self.auth or "unknown", server_key)
            self.session_wins = stats["session_wins"]
            self.session_streak = stats["session_streak"]
            kill_note = " | Kill required per Pokemon" if self.require_kill else ""
            ach_note = f" | {len(self.active_achievements)} achievement(s)" if self.active_achievements else ""
            logger.info(f"Connected! Goal: {self.goal_count} species. "
                        f"Progress: {len(self.won)}/{self.goal_count}{kill_note}{ach_note}. "
                        f"Wins: {self.session_wins} | Streak: {self.session_streak}.")

        elif cmd == "ReceivedItems":
            for item in args["items"]:
                name = _ITEM_ID_TO_NAME.get(item.item, "")
                if not name.startswith("Unlock "):
                    continue
                payload = name[len("Unlock "):]
                if payload.endswith(" Nature"):
                    nat = payload[:-len(" Nature")].lower()
                    if nat not in self.unlocked_natures:
                        self.unlocked_natures.add(nat)
                        logger.info(f"Unlocked nature: {payload}")
                else:
                    from .pokemon_data import POPULAR_ITEMS
                    as_item_key = payload.lower().replace(" ", "-")
                    if as_item_key in POPULAR_ITEMS:
                        if as_item_key not in self.unlocked_items:
                            self.unlocked_items.add(as_item_key)
                            logger.info(f"Unlocked item: {payload}")
                    else:
                        normalized = _normalize(payload)
                        if normalized not in self.unlocked:
                            self.unlocked.add(normalized)
                            logger.info(f"Unlocked: {name}")

        elif cmd == "RoomUpdate":
            for loc_id in args.get("checked_locations", []):
                name = _LOC_ID_TO_NAME.get(loc_id, "")
                if name.startswith("Win with "):
                    self.won.add(_normalize(name[len("Win with "):]))

    async def fetch_and_process(self, url: str):
        logger.info(f"Fetching {url} ...")
        try:
            loop = asyncio.get_event_loop()
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            raw = await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=10).read())
            data = json.loads(raw)
        except Exception as e:
            logger.error(f"Failed to fetch replay: {e}")
            return

        try:
            stats = self._parse_replay(data)
        except Exception as e:
            logger.error(f"Replay parse error: {e}")
            return

        if not stats["did_win"]:
            logger.warning("You did not win this battle - no checks sent.")
            self.session_streak = 0
            _save_stats(self.auth or "unknown", self.server_address or "local",
                        self.session_wins, self.session_streak)
            return

        sent_out = stats["sent_out"]

        self.session_wins += 1
        self.session_streak += 1
        _save_stats(self.auth or "unknown", self.server_address or "local",
                    self.session_wins, self.session_streak)
        await self._check_achievements(stats)

        eligible = list(stats["team"])
        if self.require_send_out:
            skipped = [s for s in eligible if s not in sent_out]
            if skipped:
                logger.info(f"Never sent out: {skipped} - skipping those.")
            eligible = [s for s in eligible if s in sent_out]

        if self.require_kill:
            skipped = [s for s in eligible if s not in stats["kills"]]
            if skipped:
                logger.info(f"No KO recorded for: {skipped} - skipping those.")
            eligible = [s for s in eligible if s in stats["kills"]]

        if not eligible:
            logger.info("No eligible Pokemon (win confirmed but no qualifying KOs).")
            return

        logger.info(f"Win confirmed. Eligible team: {eligible}")

        illegal = [s for s in eligible if s not in self.unlocked]
        if illegal:
            logger.warning(f"Invalid - used locked species: {illegal}")
            return

        new_checks = []
        for species in eligible:
            lid = _LOC_NAME_TO_ID.get(_loc_name(species))
            if lid is not None and lid not in self.checked_locations:
                new_checks.append(lid)
                self.won.add(species)

        if new_checks:
            await self.send_msgs([{"cmd": "LocationChecks", "locations": new_checks}])
            logger.info(f"Sent {len(new_checks)} check(s).")
            await self._check_goal()
        else:
            logger.info("No new checks from this replay.")

    async def _check_achievements(self, stats: dict):
        if not self.active_achievements:
            return

        sent_out = stats["sent_out"]
        kills = stats["kills"]
        kills_per_pokemon = stats["kills_per_pokemon"]
        my_faints = stats["my_faints"]
        turn_count = stats["turn_count"]
        ohko = stats["ohko"]
        nice_hit = stats["nice_hit"]
        moves_used = stats["moves_used"]
        max_kills_by_one = max(kills_per_pokemon.values(), default=0)

        ach_checks = []
        for name, loc_id in self.active_achievements.items():
            if loc_id in self.checked_locations:
                continue
            met = False

            if name == "Win 5 battles":
                met = self.session_wins >= 5
            elif name == "Win 10 battles":
                met = self.session_wins >= 10
            elif name == "Win 15 battles":
                met = self.session_wins >= 15
            elif name == "Win 20 battles":
                met = self.session_wins >= 20
            elif name == "Win 25 battles":
                met = self.session_wins >= 25
            elif name == "Win 30 battles":
                met = self.session_wins >= 30
            elif name == "Win 35 battles":
                met = self.session_wins >= 35
            elif name == "Win 40 battles":
                met = self.session_wins >= 40
            elif name == "Win 45 battles":
                met = self.session_wins >= 45
            elif name == "Win 50 battles":
                met = self.session_wins >= 50
            elif name == "Win a battle without any of your Pokemon fainting":
                met = my_faints == 0
            elif name == "Win with 3 or fewer Pokemon sent out":
                met = len(sent_out) <= 3
            elif name == "Win a battle using 6 different Pokemon":
                met = len(sent_out) >= 6
            elif name == "Win a battle with one Pokemon getting 3 KOs":
                met = max_kills_by_one >= 3
            elif name == "Win a battle with one Pokemon getting 4 KOs":
                met = max_kills_by_one >= 4
            elif name == "Win a battle in 10 turns or fewer":
                met = turn_count <= 10
            elif name == "Win a battle in 12 turns or fewer":
                met = turn_count <= 12
            elif name == "Win a battle in 14 turns or fewer":
                met = turn_count <= 14
            elif name == "Win a battle in 16 turns or fewer":
                met = turn_count <= 16
            elif name == "Win a battle in 18 turns or fewer":
                met = turn_count <= 18
            elif name == "Win 2 battles in a row":
                met = self.session_streak >= 2
            elif name == "Win 3 battles in a row":
                met = self.session_streak >= 3
            elif name == "One-hit KO a Pokemon":
                met = ohko
            elif name == "Deal 69% damage in one hit":
                met = nice_hit
            elif name.startswith("Win a battle using "):
                move = name[len("Win a battle using "):]
                met = move in moves_used

            if met:
                ach_checks.append(loc_id)
                logger.info(f"Achievement unlocked: {name}")

        if ach_checks:
            await self.send_msgs([{"cmd": "LocationChecks", "locations": ach_checks}])

    async def _check_goal(self):
        if not self.goal_sent and self.goal_count and len(self.won) >= self.goal_count:
            if ClientStatus:
                await self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
            self.goal_sent = True
            logger.info("Goal complete!")

    def _parse_replay(self, data: dict) -> dict:
        log = data.get("log", "")
        lines = log.split("\n")
        my_name = (self.auth or "").strip().lower()

        p1, p2 = None, None
        for line in lines:
            parts = line.split("|")
            if len(parts) >= 4 and parts[1] == "player" and parts[3].strip():
                if parts[2] == "p1":
                    p1 = parts[3].strip().lower()
                elif parts[2] == "p2":
                    p2 = parts[3].strip().lower()

        p1 = p1 or data.get("p1", "").strip().lower()
        p2 = p2 or data.get("p2", "").strip().lower()

        if my_name == p1:
            my_side, opp_side = "p1", "p2"
        elif my_name == p2:
            my_side, opp_side = "p2", "p1"
        else:
            raise ValueError(
                f"Slot name '{self.auth}' not found in replay "
                f"(p1='{p1}', p2='{p2}'). "
                "Your AP slot name must match your Showdown username."
            )

        winner = None
        team: set = set()
        sent_out: set = set()
        kills: set = set()
        kills_per_pokemon: dict = {}  # my species -> kill count
        my_active = None
        my_faints = 0
        turn_count = 0
        moves_used: set = set()
        ohko = False
        nice_hit = False

        # HP tracking for opponent slots: slot_key -> (current, max)
        opp_curr: dict = {}
        opp_max: dict = {}

        for line in lines:
            parts = line.split("|")
            if len(parts) < 2:
                continue
            cmd = parts[1]

            if cmd == "win" and len(parts) >= 3:
                winner = parts[2].strip().lower()

            elif cmd == "turn":
                turn_count += 1

            elif cmd == "poke" and len(parts) >= 4 and parts[2] == my_side:
                team.add(_normalize(parts[3].split(",")[0]))

            elif cmd == "switch" and len(parts) >= 5:
                slot = parts[2].split(":")[0]
                species = _normalize(parts[3].split(",")[0])
                if slot.startswith(my_side):
                    team.add(species)
                    sent_out.add(species)
                    my_active = species
                elif slot.startswith(opp_side):
                    cur, mx = _parse_hp_field(parts[4])
                    opp_curr[slot] = cur
                    if mx is not None:
                        opp_max[slot] = mx

            elif cmd == "move" and len(parts) >= 4:
                actor_slot = parts[2].split(":")[0]
                move_name = parts[3].strip()
                if actor_slot.startswith(my_side):
                    moves_used.add(move_name)

            elif cmd == "-damage" and len(parts) >= 4:
                slot = parts[2].split(":")[0]
                if slot.startswith(opp_side):
                    prev_cur = opp_curr.get(slot)
                    prev_max = opp_max.get(slot)
                    new_cur, new_mx = _parse_hp_field(parts[3])
                    if new_mx is not None:
                        opp_max[slot] = new_mx
                        prev_max = prev_max or new_mx
                    opp_curr[slot] = new_cur
                    if prev_cur is not None and prev_max:
                        damage = prev_cur - new_cur
                        if damage > 0:
                            ratio = damage / prev_max
                            if prev_cur == prev_max and new_cur == 0:
                                ohko = True
                            if 0.68 <= ratio <= 0.70:
                                nice_hit = True

            elif cmd == "-heal" and len(parts) >= 4:
                slot = parts[2].split(":")[0]
                if slot.startswith(opp_side):
                    cur, mx = _parse_hp_field(parts[3])
                    opp_curr[slot] = cur
                    if mx is not None:
                        opp_max[slot] = mx

            elif cmd == "faint" and len(parts) >= 3:
                slot = parts[2].split(":")[0]
                if slot.startswith(opp_side):
                    if my_active:
                        kills.add(my_active)
                        kills_per_pokemon[my_active] = kills_per_pokemon.get(my_active, 0) + 1
                elif slot.startswith(my_side):
                    my_faints += 1

        return {
            "did_win": winner == my_name,
            "team": list(team),
            "sent_out": sent_out,
            "kills": kills,
            "kills_per_pokemon": kills_per_pokemon,
            "my_faints": my_faints,
            "turn_count": turn_count,
            "ohko": ohko,
            "nice_hit": nice_hit,
            "moves_used": moves_used,
        }


async def _main():
    ctx = ShowdownContext(None, None)
    if gui_enabled:
        ctx.run_gui()
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
        await ctx.exit_event.wait()
        await ctx.shutdown()
    else:
        console_loop(ctx)
        await server_loop(ctx)


def run_showdown_client(*args: str) -> None:
    asyncio.run(_main())
