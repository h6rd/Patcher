import os
import sys
import json
import re
import shutil
import subprocess
import time
import hashlib
import zlib
import struct
import vpk
from rich.console import Console
from rich.text import Text
from rich.live import Live
from rich.console import Group
from pathlib import Path

IS_WINDOWS = sys.platform == 'win32'

if IS_WINDOWS:
    import winreg

    def clear():
        os.system('cls')

    def bin_subdir():
        return 'win64'

    def find_steam_dota_path():
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"SOFTWARE\WOW6432Node\Valve\Steam")
            steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
            winreg.CloseKey(key)
            candidate = os.path.join(steam_path, "steamapps", "common", "dota 2 beta")
            if os.path.exists(candidate):
                return candidate
            libraryfolders_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
            if os.path.exists(libraryfolders_path):
                with open(libraryfolders_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                for path in re.findall(r'"path"\s+"([^"]+)"', content):
                    path = path.replace('\\\\', '\\').replace('/', '\\')
                    c = os.path.join(path, "steamapps", "common", "dota 2 beta")
                    if os.path.exists(c):
                        return c
        except Exception:
            pass
        return None

    def platform_launch_dota2():
        subprocess.Popen(
            ['cmd.exe', '/c', 'START', '', 'steam://rungameid/570'],
            shell=True
        )

else:
    def clear():
        os.system('clear')

    def bin_subdir():
        if dota_path:
            bin_root = Path(dota_path) / 'game' / 'bin'
            for candidate in ('linuxsteamrt64', 'win64'):
                if (bin_root / candidate / 'dota.signatures').exists():
                    return candidate
            for candidate in ('linuxsteamrt64', 'win64'):
                if (bin_root / candidate).exists():
                    return candidate
        return 'linuxsteamrt64'

    def get_steam_roots():
        candidates = [
            Path.home() / '.steam' / 'steam',
            Path.home() / '.local' / 'share' / 'Steam',
        ]
        steam_root_link = Path.home() / '.steam' / 'root'
        if steam_root_link.exists():
            candidates.insert(0, steam_root_link.resolve())
        return candidates

    def dota_from_steam_root(steam_root):
        libraryfolders_path = steam_root / 'steamapps' / 'libraryfolders.vdf'
        search_roots = [steam_root]
        if libraryfolders_path.exists():
            try:
                with open(libraryfolders_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                for p in re.findall(r'"path"\s+"([^"]+)"', content):
                    search_roots.append(Path(p.replace('\\\\', '/').replace('\\', '/')))
            except Exception:
                pass
        for root in search_roots:
            candidate = root / 'steamapps' / 'common' / 'dota 2 beta'
            if candidate.exists():
                return str(candidate)
        return None

    def find_steam_dota_path():
        for steam_root in get_steam_roots():
            if steam_root.exists():
                result = dota_from_steam_root(steam_root)
                if result:
                    return result
        return None

    def platform_launch_dota2():
        subprocess.Popen(['xdg-open', 'steam://rungameid/570'])


if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

ASSETS_DIR       = BASE_DIR   / 'assets'
PATH_FILE        = ASSETS_DIR / 'path.txt'
ITEMS_DIR        = ASSETS_DIR / 'items'
CUSTOM_ITEMS_DIR = ITEMS_DIR  / 'Custom'
PAK_DIR          = ASSETS_DIR / 'pak01_dir'
CONFIG_FILE      = ASSETS_DIR / 'config.json'
VPK_OUTPUT       = ASSETS_DIR / 'pak01_dir.vpk'
LOG_FILE         = ASSETS_DIR / 'install.log'

if IS_WINDOWS:
    import msvcrt

    def start_listener():
        pass

    def read_key(timeout=0.05):
        deadline = time.time() + timeout
        while time.time() < deadline:
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch in ('\x00', '\xe0'):
                    ch2 = msvcrt.getwch()
                    if ch2 == 'H':
                        return 'up'
                    if ch2 == 'P':
                        return 'down'
                    if ch2 == 'K':
                        return 'left'
                    if ch2 == 'M':
                        return 'right'
                    return None
                if ch == '\r':
                    return 'enter'
                if ch == '\x1b':
                    return 'esc'
                if ch == '\x08':
                    return 'backspace'
                if ch.lower() == 'w':
                    return 'up'
                if ch.lower() == 's':
                    return 'down'
                return ch
            time.sleep(0.01)
        return None

else:
    import termios
    import tty
    import select
    import atexit

    stdin_fd = sys.stdin.fileno()
    old_term_settings = None

    def restore_terminal():
        global old_term_settings
        if old_term_settings is not None:
            try:
                termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_term_settings)
            except Exception:
                pass
            old_term_settings = None

    def start_listener():
        global old_term_settings
        if old_term_settings is not None:
            return
        try:
            old_term_settings = termios.tcgetattr(stdin_fd)
            tty.setcbreak(stdin_fd)
            atexit.register(restore_terminal)
        except (termios.error, ValueError, OSError):
            old_term_settings = None

    def read_key(timeout=0.05):
        try:
            r, _, _ = select.select([stdin_fd], [], [], timeout)
        except (OSError, ValueError):
            return None
        if not r:
            return None
        ch = os.read(stdin_fd, 1).decode(errors='ignore')
        if ch == '':
            return None
        if ch == '\x1b':
            r2, _, _ = select.select([stdin_fd], [], [], 0.05)
            if not r2:
                return 'esc'
            ch2 = os.read(stdin_fd, 1).decode(errors='ignore')
            if ch2 not in ('[', 'O'):
                return 'esc'
            r3, _, _ = select.select([stdin_fd], [], [], 0.05)
            if not r3:
                return None
            ch3 = os.read(stdin_fd, 1).decode(errors='ignore')
            return {'A': 'up', 'B': 'down', 'C': 'right', 'D': 'left'}.get(ch3)
        if ch in ('\r', '\n'):
            return 'enter'
        if ch in ('\x7f', '\x08'):
            return 'backspace'
        if ch.lower() == 'w':
            return 'up'
        if ch.lower() == 's':
            return 'down'
        return ch

PURPLE = "#B486FF"
BLUE   = "#7FD0FF"
GREEN  = "#50FA7B"
RED    = "#FF5555"
YELLOW = "#F1FA8C"
GRAY   = "#828282"
WHITE  = "white"


console = Console()

log_messages: list = []

def log_line(msg: str = ''):
    log_messages.append(msg)

config = {
    'selected_weather':    'Default',
    'selected_killstreak': 'Default',
    'selected_towers':     'Default',
    'selected_creeps':     'Default',
    'selected_terrain':    'Default',
    'selected_hud':        'Default',
    'selected_cursor':     'Default',
    'skins_enabled':       True,
}
dota_path           = None
items_game_content  = None

def load_config():
    global config
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                loaded = json.load(f)
                config.update(loaded)
        else:
            save_config()
    except Exception as e:
        print_warning(f"Could not load config: {e}")

def save_config():
    try:
        ASSETS_DIR.mkdir(exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print_warning(f"Could not save config: {e}")

def save_install_log(lines: list):
    try:
        ASSETS_DIR.mkdir(exist_ok=True)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            f.write(f"=== Install run: {timestamp} ===\n")
            for line in lines:
                f.write(line + '\n')
    except Exception as e:
        print_warning(f"Could not save install log: {e}")


def load_last_log() -> list:
    try:
        if LOG_FILE.exists():
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                return f.read().splitlines()
    except Exception:
        pass
    return []

def toggle_skins():
    currently_enabled = config.get('skins_enabled', True)
    new_state         = not currently_enabled

    if CUSTOM_ITEMS_DIR.exists():
        if new_state:
            for fp in CUSTOM_ITEMS_DIR.rglob('*.txt.disabled'):
                fp.rename(fp.with_suffix(''))
        else:
            for fp in CUSTOM_ITEMS_DIR.rglob('*.txt'):
                fp.rename(str(fp) + '.disabled')

    config['skins_enabled'] = new_state
    save_config()

def print_ascii_art():
    width = console.size.width
    lines = [
        "██████╗  █████╗ ████████╗ ██████╗██╗  ██╗███████╗██████╗ ",
        "██╔══██╗██╔══██╗╚══██╔══╝██╔════╝██║  ██║██╔════╝██╔══██╗",
        "██████╔╝███████║   ██║   ██║     ███████║█████╗  ██████╔╝",
        "██╔═══╝ ██╔══██║   ██║   ██║     ██╔══██║██╔══╝  ██╔══██╗",
        "██║     ██║  ██║   ██║   ╚██████╗██║  ██║███████╗██║  ██║",
        "╚═╝     ╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝",
        "by @dota2pornfx"
    ]
    console.print()
    for line in lines[:-1]:
        console.print(Text(line.center(width), style=PURPLE))
    console.print(Text(lines[-1].center(width), style=WHITE))
    console.print()

def separator(title=None):
    if title:
        console.rule(f"[bold {PURPLE}]{title}[/bold {PURPLE}]", style=BLUE)
    else:
        console.rule(style=BLUE)

def print_success(message): console.print(f"[{GREEN}]✓[/{GREEN}] {message}")
def print_error(message):   console.print(f"[{RED}]✗[/{RED}] {message}")
def print_warning(message): console.print(f"[{YELLOW}]⚠[/{YELLOW}] {message}")
def print_info(message):    console.print(f"[{BLUE}]🛈[/{BLUE}] {message}")

def get_available_items_grouped(folder_name):
    folder_path = ITEMS_DIR / folder_name
    if not folder_path.exists():
        return ['Default']

    items = ['Default']

    if folder_name in ['Creeps', 'Towers']:
        item_groups = {}
        for file_path in folder_path.glob('*.txt'):
            file_name = file_path.stem
            if '_' in file_name:
                base_name = '_'.join(file_name.split('_')[:-1])
                suffix    = file_name.split('_')[-1]
                if suffix in ['Radiant', 'Dire']:
                    item_groups.setdefault(base_name, []).append(suffix)
                elif file_name not in items:
                    items.append(file_name)
            elif file_name not in items:
                items.append(file_name)
        for base_name, suffixes in item_groups.items():
            if len(suffixes) >= 2:
                items.append(base_name)
            else:
                for suffix in suffixes:
                    full_name = f"{base_name}_{suffix}"
                    if full_name not in items:
                        items.append(full_name)
    else:
        for file_path in folder_path.glob('*.txt'):
            items.append(file_path.stem)

    return items

def get_item_file_paths(folder_name, item_name):
    if item_name == "Default":
        return []
    folder_path = ITEMS_DIR / folder_name
    if not folder_path.exists():
        return []
    if folder_name in ['Creeps', 'Towers']:
        radiant = folder_path / f"{item_name}_Radiant.txt"
        dire    = folder_path / f"{item_name}_Dire.txt"
        if radiant.exists() and dire.exists():
            return [radiant, dire]
        single = folder_path / f"{item_name}.txt"
        return [single] if single.exists() else []
    else:
        single = folder_path / f"{item_name}.txt"
        return [single] if single.exists() else []

PREVIEW_LINKS = {
    'Weather':    'https://dota2.fandom.com/wiki/Weather_Effects',
    'Killstreak': 'https://www.youtube.com/watch?v=dFFWunvryFI',
    'Towers':     'https://dota2.fandom.com/wiki/Custom_Towers',
    'Creeps':     'https://dota2.fandom.com/wiki/Custom_Creeps',
    'Terrain':    'https://dota2.fandom.com/wiki/Custom_Terrain',
    'Hud':        'https://dota2.fandom.com/wiki/HUD_Skins',
    'Cursor':     'https://dota2.fandom.com/wiki/Cursor_Pack',
}


def show_item_selection(category_name, folder_name, current_selection):
    available_items = get_available_items_grouped(folder_name)

    if not available_items or len(available_items) == 1:
        clear()
        print_ascii_art()
        print_error(f"No items found in {folder_name} folder")
        time.sleep(2)
        return current_selection

    needs_multi_digit = len(available_items) > 10

    try:
        cursor = available_items.index(current_selection)
    except ValueError:
        cursor = 0

    input_str = ""

    def build_renderable(input_buf=""):
        lines = []
        lines.append(Text(f"{category_name} Selection\n", style=f"bold {PURPLE}"))

        if category_name in PREVIEW_LINKS:
            preview_text = Text()
            preview_text.append("Preview: ", style=BLUE)
            preview_text.append(PREVIEW_LINKS[category_name], style=GRAY)
            lines.append(preview_text)
            lines.append(Text(""))

        for idx, item in enumerate(available_items):
            is_selected = item == current_selection
            is_cursor_  = idx == cursor
            marker = "→ " if is_selected else "  "
            row = Text()
            if is_cursor_:
                row.append(f"{marker}{idx}. {item}", style="bold white on #3A2F5A")
            else:
                row.append(marker, style="white")
                row.append(f"{idx}. ", style="white")
                row.append(item, style=PURPLE)
            lines.append(row)

        lines.append(Text(""))

        if input_buf:
            hint = Text()
            hint.append("Typing: ", style=GRAY)
            hint.append(input_buf, style="bold white")
            hint.append("  — Enter to confirm, ESC to cancel", style=GRAY)
        else:
            hint = Text("↑↓ or w/s + Enter  |  Type number + Enter  |  ESC to cancel", style=GRAY)
        lines.append(hint)

        return Group(*lines)

    clear()
    print_ascii_art()

    with Live(build_renderable(), console=console, refresh_per_second=30, transient=False) as live:
        while True:
            k = read_key(timeout=0.05)
            if k is None:
                continue

            if k == 'esc':
                return current_selection

            elif k == 'up':
                cursor = (cursor - 1) % len(available_items)
                input_str = ""
                live.update(build_renderable())

            elif k == 'down':
                cursor = (cursor + 1) % len(available_items)
                input_str = ""
                live.update(build_renderable())

            elif k == 'enter':
                if input_str:
                    try:
                        idx = int(input_str)
                        if 0 <= idx < len(available_items):
                            return available_items[idx]
                    except ValueError:
                        pass
                    input_str = ""
                    live.update(build_renderable())
                else:
                    return available_items[cursor]

            elif k == 'backspace':
                if input_str:
                    input_str = input_str[:-1]
                    live.update(build_renderable(input_str))

            elif k and k.isdigit():
                if not needs_multi_digit:
                    idx = int(k)
                    if 0 <= idx < len(available_items):
                        return available_items[idx]
                else:
                    input_str += k
                    live.update(build_renderable(input_str))

def load_items_from_folder():
    replacements = {}

    if not ITEMS_DIR.exists():
        print_error(f"Items directory not found: {ITEMS_DIR}")
        return replacements

    print("\n📂 Loading items from folder...")

    for file_path in ITEMS_DIR.glob('*.txt'):
        load_single_item(file_path, replacements)

    if CUSTOM_ITEMS_DIR.exists():
        for file_path in CUSTOM_ITEMS_DIR.rglob('*.txt'):
            load_single_item(file_path, replacements)

    optional_folders = {
        'Weather':    config['selected_weather'],
        'Killstreak': config['selected_killstreak'],
        'Towers':     config['selected_towers'],
        'Creeps':     config['selected_creeps'],
        'Terrain':    config['selected_terrain'],
        'Hud':        config['selected_hud'],
        'Cursor':     config['selected_cursor'],
    }

    for folder_name, selected_item in optional_folders.items():
        if selected_item != "Default":
            load_category_items(folder_name, selected_item, replacements)

    log_line(f"Loaded {len(replacements)} item replacements")
    return replacements

def load_single_item(file_path, replacements):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        match = re.match(r'^"(\d+)"', content.strip())
        if match:
            item_id = match.group(1)
            replacements[item_id] = {
                'description': file_path.stem,
                'content':     content,
                'match_by':    'id',
            }
            log_line(f"  Loaded: {file_path.name} (ID: {item_id})")
        else:
            name_match = re.search(r'"name"\s+"([^"]+)"', content)
            if name_match:
                item_name = name_match.group(1)
                replacements[item_name] = {
                    'description': file_path.stem,
                    'content':     content,
                    'match_by':    'name',
                }
                log_line(f"  Loaded: {file_path.name} (Name: {item_name})")
            else:
                print_warning(f"Could not extract item ID or name from {file_path.name}")
    except Exception as e:
        print_warning(f"Error loading {file_path.name}: {e}")

def load_category_items(folder_name, selected_item, replacements):
    file_paths = get_item_file_paths(folder_name, selected_item)

    if not file_paths:
        print_warning(f"Selected file(s) not found for: {folder_name}/{selected_item}")
        return

    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            match = re.match(r'^"(\d+)"', content.strip())
            if match:
                item_id   = match.group(1)
                new_entry = {
                    'description': f"{folder_name}: {file_path.stem}",
                    'content':     content,
                    'match_by':    'id',
                }
                if item_id in replacements:
                    old_lines = replacements[item_id]['content'].strip().split('\n')
                    new_lines = content.strip().split('\n')
                    if (old_lines[0].strip() == f'"{item_id}"'
                            and new_lines[0].strip() == f'"{item_id}"'):
                        replacements[item_id] = new_entry
                        log_line(f"  Replaced: {folder_name}/{file_path.name} (ID: {item_id})")
                    else:
                        print_warning(f"Block structure mismatch for ID {item_id}")
                else:
                    replacements[item_id] = new_entry
                    log_line(f"  Loaded: {folder_name}/{file_path.name} (ID: {item_id})")
            else:
                print_warning(f"Could not extract item ID from {folder_name}/{file_path.name}")
        except Exception as e:
            print_warning(f"Error loading {folder_name}/{file_path.name}: {e}")

DOTA2_APP_ID   = '570'
DOTA2_FOLDER   = 'dota 2 beta'

def find_via_steampathfinder():
    if not IS_WINDOWS:
        return None
    try:
        from SteamPathFinder import get_steam_path, get_app_path, get_game_path
        steam_path = get_steam_path()
        if not steam_path:
            return None
        game_path = get_game_path(steam_path, DOTA2_APP_ID, DOTA2_FOLDER)
        if game_path and os.path.exists(game_path):
            return game_path
        app_path = get_app_path(steam_path, DOTA2_APP_ID)
        if app_path and os.path.exists(app_path):
            return app_path
    except Exception:
        pass
    return None


def find_dota2_path(use_cached=True):
    global dota_path

    if use_cached and PATH_FILE.exists():
        try:
            with open(PATH_FILE, 'r', encoding='utf-8') as f:
                cached_path = f.read().strip()
            if os.path.exists(cached_path):
                dota_path = cached_path
                log_line(f"Using cached Dota 2 path: {dota_path}")
                return True
            print_warning("Cached path invalid, searching again...")
            log_line("Cached path invalid, searching again...")
        except Exception as e:
            print_warning(f"Error reading cached path: {e}")
            log_line(f"Error reading cached path: {e}")

    log_line("Searching for Dota 2 installation...")

    found = find_via_steampathfinder()
    if found:
        dota_path = found
        save_dota_path()
        log_line(f"Found Dota 2 (SteamPathFinder): {dota_path}")
        return True

    found = find_steam_dota_path()
    if found:
        dota_path = found
        save_dota_path()
        log_line(f"Found Dota 2: {dota_path}")
        return True

    print_warning("Dota 2 not found automatically")
    log_line("Dota 2 not found automatically")
    print("\nPlease enter your Dota 2 installation path:")
    manual_path = input("\nPath: ").strip().strip('"')

    if os.path.exists(manual_path):
        dota_path = manual_path
        save_dota_path()
        log_line(f"Found Dota 2 (manual): {dota_path}")
        return True

    print_error("Invalid path provided")
    log_line("ERROR: Invalid path provided")
    return False

def save_dota_path():
    try:
        ASSETS_DIR.mkdir(exist_ok=True)
        with open(PATH_FILE, 'w', encoding='utf-8') as f:
            f.write(dota_path)
    except Exception as e:
        print_warning(f"Could not save path cache: {e}")

def gameinfo_path():
    return Path(dota_path) / 'game' / 'dota' / 'gameinfo_branchspecific.gi'

def signatures_path():
    return Path(dota_path) / 'game' / 'bin' / bin_subdir() / 'dota.signatures'

def mod_dir():
    return Path(dota_path) / 'game' / 'DotaModdingCommunityMods'

def calculate_hashes(gameinfo):
    sha1_hasher = hashlib.sha1()
    crc_value   = 0
    with open(gameinfo, 'rb') as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            sha1_hasher.update(chunk)
            crc_value = zlib.crc32(chunk, crc_value)
    crc_value &= 0xFFFFFFFF
    sha1_hex  = sha1_hasher.hexdigest().upper()
    crc_hex   = struct.pack('<I', crc_value).hex().upper()
    return sha1_hex, crc_hex

def validate_patch_state(gameinfo, signatures):
    gameinfo_patched   = False
    signatures_patched = False
    try:
        with open(gameinfo, 'r', encoding='utf-8', errors='ignore') as f:
            if 'Patched by DotaModdingCommunity Patcher' in f.read():
                gameinfo_patched = True
    except Exception as e:
        print_warning(f"Cannot read gameinfo: {e}")
    try:
        with open(signatures, 'r', encoding='utf-8', errors='ignore') as f:
            contents = f.read()
        last_line = contents.strip().splitlines()[-1] if contents.strip() else ''
        if last_line.startswith('...'):
            actual_sha1, actual_crc32 = calculate_hashes(gameinfo)
            info_part   = last_line.split('~', 1)[1]
            sha1_part, crc_part = info_part.split(';', 1)
            stored_sha1 = sha1_part.split(':', 1)[1].strip()
            stored_crc  = crc_part.split(':', 1)[1].strip()
            if actual_sha1 == stored_sha1 and actual_crc32 == stored_crc:
                signatures_patched = True
    except Exception as e:
        print_warning(f"Cannot read dota.signatures: {e}")
    return gameinfo_patched, signatures_patched

def backup_file(src, backup_ext):
    backup = src.with_suffix(backup_ext)
    if not backup.exists():
        shutil.copy2(src, backup)

def modify_gameinfo(gameinfo):
    with open(gameinfo, 'r', encoding='utf-8', errors='ignore') as f:
        contents = f.read()
    fs_idx = contents.find('FileSystem')
    if fs_idx == -1:
        raise RuntimeError("Could not find 'FileSystem' in gameinfo")
    prefix     = contents[:fs_idx]
    rest       = contents[fs_idx:]
    bracket_idx = rest.find('}')
    if bracket_idx == -1:
        raise RuntimeError("Could not find closing '}' in FileSystem block")
    body   = rest[:bracket_idx]
    suffix = rest[bracket_idx:]
    insert = r"""
        SearchPaths // Patched by DotaModdingCommunity Patcher
        {
            Game_Language		dota_*LANGUAGE*

            Game_LowViolence	dota_lv

            Game				DotaModdingCommunityMods
            Game				dota
            Game				core

            Mod					DotaModdingCommunityMods
            Mod					dota

            Write				dota

            AddonRoot_Language	dota_*LANGUAGE*_addons

            AddonRoot			dota_addons

            PublicContent		dota_core
            PublicContent		core
        }
    """
    with open(gameinfo, 'w', encoding='utf-8') as f:
        f.write(prefix + body + insert + suffix)

def modify_signatures(signatures, sha1, crc32):
    with open(signatures, 'r', encoding='utf-8', errors='ignore') as f:
        contents = f.read()
    patch_line = r'...\..\..\dota\gameinfo_branchspecific.gi~SHA1:' + sha1 + ';CRC:' + crc32
    with open(signatures, 'w', encoding='utf-8') as f:
        f.write(contents.rstrip('\n') + '\n' + patch_line)

def dmc_patcher():
    if not dota_path:
        print_error("Dota 2 path not set")
        return False

    gameinfo   = gameinfo_path()
    signatures = signatures_path()
    mod_dir_path    = mod_dir()

    if not gameinfo.exists():
        print_error(f"gameinfo not found: {gameinfo}")
        return False
    if not signatures.exists():
        print_error(f"dota.signatures not found: {signatures}")
        return False

    print("\n🔧 Running DMC Patcher...")
    try:
        gameinfo_patched, sigs_patched = validate_patch_state(gameinfo, signatures)

        if not gameinfo_patched:
            backup_file(gameinfo, '.gi_backup')
            modify_gameinfo(gameinfo)
            log_line("gameinfo_branchspecific.gi patched")
        else:
            log_line("gameinfo_branchspecific.gi already patched")

        if not sigs_patched:
            backup_file(signatures, '.signatures_backup')
            sha1, crc32 = calculate_hashes(gameinfo)
            modify_signatures(signatures, sha1, crc32)
            log_line("dota.signatures patched")
        else:
            log_line("dota.signatures already patched")

        mod_dir_path.mkdir(parents=True, exist_ok=True)
        log_line(f"Mod directory ready: {mod_dir_path}")
        return True

    except Exception as e:
        print_error(f"Patcher error: {e}")
        log_line(f"ERROR: Patcher error: {e}")
        import traceback
        traceback.print_exc()
        return False

def extract_items_game():
    global items_game_content
    try:
        vpk_path = os.path.join(dota_path, "game", "dota", "pak01_dir.vpk")
        if not os.path.exists(vpk_path):
            print_error(f"VPK file not found: {vpk_path}")
            log_line(f"ERROR: VPK file not found: {vpk_path}")
            return False
        log_line(f"Opening VPK: {vpk_path}")
        pak = vpk.open(vpk_path)
        file_path = "scripts/items/items_game.txt"
        if file_path in pak:
            items_game_content = pak.get_file(file_path).read().decode('utf-8', errors='ignore')
            log_line("Extracted items_game.txt")
            return True
        print_error(f"{file_path} not found in VPK")
        log_line(f"ERROR: {file_path} not found in VPK")
        return False
    except Exception as e:
        print_error(f"Error extracting items_game.txt: {e}")
        log_line(f"ERROR: extracting items_game.txt: {e}")
        import traceback
        traceback.print_exc()
        return False

def normalize_indentation(text):
    lines      = text.split('\n')
    normalized = []
    for line in lines:
        stripped = line.lstrip(' ')
        spaces   = len(line) - len(stripped)
        normalized.append('\t' * (spaces // 4) + stripped)
    return '\n'.join(normalized)

def apply_replacements(replacements):
    global items_game_content
    if not items_game_content:
        print_error("items_game.txt content not loaded")
        return False

    print("\n🛠️ Applying replacements...")

    items_section_start = 0
    pricepoints_end = items_game_content.find('"store_currency_pricepoints"')
    if pricepoints_end != -1:
        brace_count   = 0
        found_opening = False
        for i in range(pricepoints_end, len(items_game_content)):
            if items_game_content[i] == '{':
                brace_count += 1
                found_opening = True
            elif items_game_content[i] == '}':
                brace_count -= 1
                if found_opening and brace_count == 0:
                    items_section_start = i + 1
                    break

    replacement_data = []
    printed_heroes   = set()

    for item_key, replacement in replacements.items():
        try:
            new_value = replacement.get('content')
            if not new_value:
                continue
            new_value      = normalize_indentation(new_value)
            search_content = items_game_content[items_section_start:]
            match_by       = replacement.get('match_by', 'id')

            if match_by == 'id':
                match = re.search(rf'^\s*"{item_key}"\s*\{{', search_content, re.MULTILINE)
                if match:
                    start_pos, end_pos = find_block_bounds(items_section_start, match)
                    if end_pos > start_pos:
                        hero_name = replacement.get('description', f'Item {item_key}').split('_')[0].split(':')[0].strip()
                        if hero_name not in printed_heroes:
                            log_line(f"  Applied: {hero_name}")
                            printed_heroes.add(hero_name)
                        replacement_data.append((start_pos, end_pos, new_value))
                    else:
                        print_warning(f"Item {item_key} - could not find closing brace")
                        log_line(f"WARNING: Item {item_key} - could not find closing brace")
                else:
                    print_warning(f"Item {item_key} not found in items section")
                    log_line(f"WARNING: Item {item_key} not found in items section")

            else:
                for match in re.finditer(r'^\s*"(\d+)"\s*\{', search_content, re.MULTILINE):
                    start_pos, end_pos = find_block_bounds(items_section_start, match)
                    if end_pos <= start_pos:
                        continue
                    block = items_game_content[start_pos:end_pos]
                    block_name_match = re.search(r'"name"\s+"([^"]+)"', block)
                    if not block_name_match or block_name_match.group(1) != item_key:
                        continue
                    original_id       = match.group(1)
                    new_content_match = re.search(r'\{(.*)\}', new_value, re.DOTALL)
                    if new_content_match:
                        inner_content  = new_content_match.group(1)
                        id_line_match  = re.search(r'^(\s*)"' + original_id + r'"', block, re.MULTILINE)
                        indent         = id_line_match.group(1) if id_line_match else '\t'
                        reconstructed  = f'{indent}"{original_id}"\n{indent}{{{inner_content}{indent}}}'
                        hero_name      = replacement.get('description', f'Item {item_key}').split('_')[0].split(':')[0].strip()
                        if hero_name not in printed_heroes:
                            log_line(f"  Applied (by name): {hero_name}")
                            printed_heroes.add(hero_name)
                        replacement_data.append((start_pos, end_pos, reconstructed))
                    else:
                        print_warning(f"Could not extract content from replacement for {item_key}")
                        log_line(f"WARNING: Could not extract content from replacement for {item_key}")
                    break

        except Exception as e:
            print_error(f"Error processing item {item_key}: {e}")

    replacement_data.sort(key=lambda x: x[0], reverse=True)
    modified_content = items_game_content
    changes_count    = 0
    for start_pos, end_pos, new_value in replacement_data:
        try:
            modified_content = modified_content[:start_pos] + new_value + modified_content[end_pos:]
            changes_count += 1
        except Exception as e:
            print_error(f"Error applying replacement at position {start_pos}: {e}")

    items_game_content = modified_content
    log_line(f"Total replacements applied: {changes_count}")
    return changes_count > 0


def find_block_bounds(items_section_start, match):
    start_pos   = items_section_start + match.start()
    brace_count = 0
    end_pos     = start_pos
    for i in range(start_pos, len(items_game_content)):
        char = items_game_content[i]
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end_pos = i + 1
                break
    return start_pos, end_pos


def create_pak_structure():
    try:
        scripts_dir = PAK_DIR / 'scripts' / 'items'
        scripts_dir.mkdir(parents=True, exist_ok=True)
        with open(scripts_dir / 'items_game.txt', 'w', encoding='utf-8', newline='') as f:
            f.write(items_game_content)
        return True
    except Exception as e:
        print_error(f"Error creating pak structure: {e}")
        import traceback
        traceback.print_exc()
        return False


def pack_vpk():
    try:
        print("\n📦 Packing VPK file...")
        if VPK_OUTPUT.exists():
            VPK_OUTPUT.unlink()

        newpak = vpk.new(str(VPK_OUTPUT))

        if config.get('skins_enabled', True):
            newpak.read_dir(str(PAK_DIR))
            log_line("VPK: packing full pak01_dir (skins enabled)")
            newpak.save(str(VPK_OUTPUT))
        else:
            import tempfile
            scripts_dir = PAK_DIR / 'scripts'
            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                if scripts_dir.exists():
                    shutil.copytree(str(scripts_dir), str(tmp_path / 'scripts'))
                newpak.read_dir(tmp)
                newpak.save(str(VPK_OUTPUT))
            log_line("VPK: packing scripts/ only (skins disabled)")

        log_line(f"VPK created: {VPK_OUTPUT}")
        return True
    except Exception as e:
        print_error(f"Error creating VPK: {e}")
        log_line(f"ERROR: creating VPK: {e}")
        import traceback
        traceback.print_exc()
        return False


def move_to_install_dir():
    try:
        print("\n📁 Moving to install directory...")
        dest_dir = Path(dota_path) / 'game' / 'DotaModdingCommunityMods'
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(VPK_OUTPUT, dest_dir / 'pak01_dir.vpk')
        log_line(f"Moved to: {dest_dir / 'pak01_dir.vpk'}")
        try:
            VPK_OUTPUT.unlink()
            log_line("Cleaned up temporary VPK")
        except Exception as e:
            log_line(f"WARNING: Could not delete temporary VPK: {e}")
        return True
    except Exception as e:
        print_error(f"Error moving file: {e}")
        log_line(f"ERROR: moving file: {e}")
        return False

def kill_dota2():
    try:
        if IS_WINDOWS:
            for name in ("dota2.exe",):
                subprocess.run(
                    ["taskkill", "/F", "/T", "/IM", name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
        else:
            for name in ("dota2", "dota2.exe"):
                subprocess.run(
                    ["pkill", "-9", "-x", name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        time.sleep(1)
    except FileNotFoundError:
        pass
    except Exception as e:
        print_warning(f"Could not close Dota 2 process: {e}")


def launch_dota2():
    try:
        print("\n🎮 Launching Dota 2...")
        platform_launch_dota2()
        return True
    except Exception as e:
        print_error(f"Error launching Dota 2: {e}")
        log_line(f"ERROR: launching Dota 2: {e}")
        return False

def show_menu():
    print_ascii_art()
    console.print()
    console.print(f"[white]1.[/white] [bold {PURPLE}]Install[/bold {PURPLE}]")
    console.print(f"[white]2.[/white] [bold {PURPLE}]Fix MM[/bold {PURPLE}]")
    print()

    categories = [
        ('3', 'Weather',    'selected_weather'),
        ('4', 'Killstreak', 'selected_killstreak'),
        ('5', 'Towers',     'selected_towers'),
        ('6', 'Creeps',     'selected_creeps'),
        ('7', 'Terrain',    'selected_terrain'),
        ('8', 'Hud',        'selected_hud'),
        ('9', 'Cursor',     'selected_cursor'),
    ]

    for number, display_name, config_key in categories:
        value = config[config_key]
        color = GRAY if value == "Default" else BLUE
        console.print(f"[white]{number}.[/white] [bold {PURPLE}]{display_name}: [{color}]{value}[/{color}][/bold {PURPLE}]")

    skins_on    = config.get('skins_enabled', True)
    skins_color = GREEN if skins_on else RED
    skins_label = "Enabled" if skins_on else "Disabled"
    console.print(f"\n[white]/.[/white] [bold {PURPLE}]Skins: [{skins_color}]{skins_label}[/{skins_color}][/bold {PURPLE}]")

    print()
    console.print(f"[white]0.[/white] [bold {PURPLE}]Uninstall[/bold {PURPLE}]")

    console.print(f"\n[bold white]Press number...[/bold white]")

    while True:
        k = read_key(timeout=0.1)
        if k is None:
            continue
        if k in ('up', 'down', 'esc', 'enter', 'backspace'):
            continue
        if k in '1234567890':
            console.print(f"\n[white]Selected: [{PURPLE}]{k}[/{PURPLE}][/white]")
            return k
        if k == '/':
            return '/'

def install():
    global log_messages
    log_messages = []
    success = False
    try:
        print()
        separator("INSTALLATION")
        log_line("=== INSTALLATION START ===")
        kill_dota2()
        if not find_dota2_path():    return False
        if not extract_items_game(): return False
        replacements = load_items_from_folder()
        if not replacements:
            print_error("No item replacements found in items folder")
            log_line("ERROR: No item replacements found in items folder")
            return False
        if not apply_replacements(replacements):
            print_error("Failed to apply replacements")
            log_line("ERROR: Failed to apply replacements")
            return False
        if not create_pak_structure(): return False
        if not pack_vpk():             return False
        if not move_to_install_dir():  return False
        if not dmc_patcher():          return False
        launch_dota2()
        print()
        separator("INSTALLATION COMPLETE")
        log_line("=== INSTALLATION COMPLETE ===")
        success = True
        return True
    finally:
        if not success:
            log_line("=== INSTALLATION FAILED ===")
        save_install_log(log_messages)
        log_messages = []


def fix_mm():
    print()
    separator("FIX MM")
    kill_dota2()
    if not find_dota2_path(): return False

    print("\n🗑️ Removing old modded files...")
    bin_dir = bin_subdir()

    backup_files = [
        (os.path.join(dota_path, "game", "dota", "gameinfo_branchspecific.gi_backup"),
         os.path.join(dota_path, "game", "dota", "gameinfo_branchspecific.gi")),
        (os.path.join(dota_path, "game", "bin", bin_dir, "dota.signatures_backup"),
         os.path.join(dota_path, "game", "bin", bin_dir, "dota.signatures")),
    ]
    for backup_file, original_file in backup_files:
        try:
            if os.path.exists(backup_file):
                if os.path.exists(original_file):
                    os.remove(original_file)
                os.rename(backup_file, original_file)
                print_success(f"Restored: {os.path.basename(original_file)}")
            elif os.path.exists(original_file):
                print_info(f"No backup for {os.path.basename(original_file)}, keeping as-is")
        except Exception as e:
            print_error(f"Error restoring {os.path.basename(original_file)}: {e}")

    if not dmc_patcher(): return False
    launch_dota2()
    print()
    separator("FIX MM COMPLETE")
    return True

def uninstall():
    print()
    separator("UNINSTALL")
    print()
    kill_dota2()
    if not find_dota2_path(): return False

    print("\n🗑️ Removing modded files...")
    bin_dir = bin_subdir()

    backup_files = [
        (os.path.join(dota_path, "game", "dota", "gameinfo_branchspecific.gi_backup"),
         os.path.join(dota_path, "game", "dota", "gameinfo_branchspecific.gi")),
        (os.path.join(dota_path, "game", "bin", bin_dir, "dota.signatures_backup"),
         os.path.join(dota_path, "game", "bin", bin_dir, "dota.signatures")),
    ]
    for backup_file, original_file in backup_files:
        try:
            if os.path.exists(backup_file):
                if os.path.exists(original_file):
                    os.remove(original_file)
                os.rename(backup_file, original_file)
                print_success(f"Restored: {os.path.basename(original_file)}")
            elif os.path.exists(original_file):
                os.remove(original_file)
                print_success(f"Deleted: {os.path.basename(original_file)}")
        except Exception as e:
            print_error(f"Error restoring {os.path.basename(original_file)}: {e}")

    mod_dir_path = os.path.join(dota_path, "game", "DotaModdingCommunityMods")
    try:
        if os.path.exists(mod_dir_path):
            shutil.rmtree(mod_dir_path)
            console.print(f"  [{GREEN}]✓[/{GREEN}] Deleted: DotaModdingCommunityMods")
        else:
            print_info("Not found: DotaModdingCommunityMods")
    except Exception as e:
        print_error(f"Error deleting DotaModdingCommunityMods: {e}")

    print()
    separator("UNINSTALL COMPLETE")
    return True

def main():
    start_listener()
    load_config()

    while True:
        clear()
        choice = show_menu()

        if choice == '1':
            install()
            print("\nClosing...")
            time.sleep(3)
            break

        elif choice == '2':
            fix_mm()
            print("\nClosing...")
            time.sleep(3)
            break

        elif choice == '3':
            config['selected_weather'] = show_item_selection("Weather", "Weather", config['selected_weather'])
            save_config()

        elif choice == '4':
            config['selected_killstreak'] = show_item_selection("Killstreak", "Killstreak", config['selected_killstreak'])
            save_config()

        elif choice == '5':
            config['selected_towers'] = show_item_selection("Towers", "Towers", config['selected_towers'])
            save_config()

        elif choice == '6':
            config['selected_creeps'] = show_item_selection("Creeps", "Creeps", config['selected_creeps'])
            save_config()

        elif choice == '7':
            config['selected_terrain'] = show_item_selection("Terrain", "Terrain", config['selected_terrain'])
            save_config()

        elif choice == '8':
            config['selected_hud'] = show_item_selection("Hud", "Hud", config['selected_hud'])
            save_config()

        elif choice == '9':
            config['selected_cursor'] = show_item_selection("Cursor", "Cursor", config['selected_cursor'])
            save_config()

        elif choice == '/':
            toggle_skins()
            time.sleep(1)

        elif choice == '0':
            uninstall()
            print("\nClosing...")
            time.sleep(3)
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
