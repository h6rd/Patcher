# Patcher for Dota 2

A tool for installing custom weather, killstreaks, towers, terrains, creeps, HUDs, cursors, and manually adding custom in-game items.

*Powered by [DMCPatcher](https://github.com/DotaModdingCommunity/Dota-2-Patcher). Special thanks to the [DotaModdingCommunity](https://github.com/DotaModdingCommunity).*


> [!CAUTION]
> **Use this script at your own risk.** Modifying game files is technically unsafe. However, it is worth noting that no users have reported being banned for using this specific patching method over a long period of use.

---

## Download

| Platform | Link |
|----------|------|
| **Windows** | [Patcher-Win.zip](https://github.com/h6rd/Patcher/releases/latest/download/Patcher-Win.zip) |
| **Linux** | [Patcher-Linux.zip](https://github.com/h6rd/Patcher/releases/latest/download/Patcher-Linux.zip) |

---

## Usage

1. Launch the script.
2. Select your desired modifications in sections **3 through 9**. 
   * *Tip: You can use the keyboard arrows or number keys to navigate within each section.*
3. Click **Install**.

### Post-Installation Notes
* **Game Updates:** If Dota 2 updates, the game will likely crash on startup. To fix this, simply run the **Install** process again.
* **Matchmaking:** If you encounter a VAC warning, run **Fix MM**.

---

## Custom Skins
When skins are enabled, the script utilizes the contents of the `Custom` folder.
- **You can find the ready-made files here:** *[MOR](https://vk.com/amir4anmods)* / *[MOR Hub](https://vk.com/zzzhub)* / *[Arkadium](https://discord.gg/C7VFuju5WD)*

### Adding Skins from MOR
1. Create your skin in MOR, which will generate an output archive.
2. Navigate to `assets/items/Custom` and create a new folder (naming it after the hero is recommended for organization).
3. Place the script files from the MOR output into this new folder (these are usually named `script 1.txt`, `script 2.txt`, etc.).
4. Extract all remaining files and folders from the MOR archive into `assets/pak01_dir`, **excluding** the `mor_scripts` folder.
*For example, there are the frostbloom ursa claws, you can take a look at their structure*


### Manual Skin Addition

Let's walk through an example: **manually adding the "Golden Full-Bore Bonanza" immortal back item for Sniper**.

#### 1. Extract `items_game.txt`
1. Open [Source 2 Viewer](https://valveresourceformat.github.io/).
2. Navigate to your Dota 2 directory (`Steam\steamapps\common\dota 2 beta\game\dota`).
3. Open `pak01_dir.vpk` and extract the `items_game.txt` file.

#### 2. Locate and Copy the Item Data
1. Open the extracted `items_game.txt` file in a text editor.
2. Search for the item named `Golden Full-Bore Bonanza`.
3. Copy its entire property block, **including** its numerical ID. It should look like this:

```text
       "9455"
        {
            "name"      "Golden Full-Bore Bonanza"
            "prefab"        "wearable"
            "creation_date"     "2017-08-03"
            "event_id"      "EVENT_ID_INTERNATIONAL_2017"
            "hide_tradecraftdelete"     "1"
            "image_inventory"       "econ/items/sniper/sniper_cape_immortal/sniper_cape_immortal1"
            "item_description"      "#DOTA_Item_Desc_Golden_FullBore_Bonanza"
            "item_name"     "#DOTA_Item_Golden_FullBore_Bonanza"
            "item_rarity"       "immortal"
            "item_slot"     "back"
            "item_type_name"        "#DOTA_WearableType_Wearable"
            "model_player"      "models/items/sniper/sniper_cape_immortal/sniper_cape_immortal.vmdl"
            "portraits"
            {
                "icon"
                {
                    "cameras"
                    {
                        "Default"
                        {
                            "PortraitPosition"      "-403.856110 -105.858452 201.133286"
                            "PortraitAngles"        "17.312553 15.001129 0.000000"
                            "PortraitFOV"       "39"
                            "PortraitFar"       "1000"
                        }
                    }
                    "PortraitLightPosition"     "-221.270416 54.274155 186.428131"
                    "PortraitLightAngles"       "35.244141 2.219238 0.000000"
                    "PortraitLightFOV"      "65"
                    "PortraitLightDistance"     "317"
                    "PortraitLightColor"        "254 254 254"
                    "PortraitLightScale"        "1.750000"
                    "PortraitShadowColor"       "97 97 97"
                    "PortraitShadowScale"       "5"
                    "PortraitGroundShadowScale"     "1.500000"
                    "PortraitAmbientDirection"      "39.910 -29.100 -18.910"
                    "PortraitAmbientColor"      "148 148 148"
                    "PortraitAmbientScale"      "4.950000"
                    "PortraitSpecularColor"     "251 74 84"
                    "PortraitSpecularDirection"     "0.000000 0.000000 -1.000000"
                    "PortraitSpecularPower"     "16"
                    "PortraitBackgroundColor1"      "1.000000 1.000000 1.000000"
                    "PortraitBackgroundColor2"      "1.000000 1.000000 1.000000"
                    "PortraitBackgroundColor3"      "1.000000 1.000000 1.000000"
                    "PortraitBackgroundColor4"      "0.000000 0.200000 0.700000"
                    "PortraitBackgroundTexture"     "materials/vgui/econ/item_icon_bg.vmat"
                    "PortraitAnimationActivity"     "ACT_DOTA_IDLE"
                    "PortraitAnimationCycle"        "0"
                    "PortraitAnimationRate"     "0"
                    "PortraitHideHero"      "0"
                    "PortraitHideParticles"     "0"
                    "PortraitHideDropShadow"        "0"
                    "PortraitDesaturateParticles"       "0"
                    "PortraitDesaturateHero"        "1"
                }
            }
            "static_attributes"
            {
                "can_equip_as_ability_effects"
                {
                    "attribute_class"       "can_equip_as_ability_effects"
                    "value"     "2"
                }
            }
            "used_by_heroes"
            {
                "npc_dota_hero_sniper"      "1"
            }
            "visuals"
            {
                "skip_model_combine"        "0"
                "asset_modifier"
                {
                    "type"      "activity"
                    "asset"     "ALL"
                    "modifier"      "immortal_cape"
                    "style"     "0"
                }
                "asset_modifier"
                {
                    "type"      "particle"
                    "asset"     "particles/units/heroes/hero_sniper/sniper_headshot_slow.vpcf"
                    "modifier"      "particles/econ/items/sniper/sniper_immortal_cape_golden/sniper_immortal_cape_golden_headshot_slow.vpcf"
                    "style"     "0"
                    "apply_when_equipped_in_ability_effects_slot"       "2"
                }
                "asset_modifier"
                {
                    "type"      "particle_create"
                    "modifier"      "particles/econ/items/sniper/sniper_immortal_cape_golden/sniper_immortal_cape_golden_ambient.vpcf"
                    "style"     "0"
                }
                "asset_modifier"
                {
                    "type"      "particle"
                    "asset"     "particles/units/heroes/hero_sniper/sniper_headshot_slow_caster.vpcf"
                    "modifier"      "particles/econ/items/sniper/sniper_immortal_cape_golden/sniper_immortal_cape_golden_headshot_slow_caster.vpcf"
                    "style"     "0"
                    "apply_when_equipped_in_ability_effects_slot"       "2"
                }
                "asset_modifier"
                {
                    "type"      "sound"
                    "asset"     "Hero_Sniper.Headshot"
                    "modifier"      "Hero_Sniper.DuckTarget"
                    "style"     "0"
                    "apply_when_equipped_in_ability_effects_slot"       "2"
                }
                "asset_modifier"
                {
                    "type"      "ability_icon"
                    "asset"     "sniper_headshot"
                    "modifier"      "sniper_headshot_immortal_gold"
                    "apply_when_equipped_in_ability_effects_slot"       "2"
                }
                "skin"      "1"
            }
        }
```

#### 3. Edit and Save the Item Script
1. Create a new text file named `back.txt` and paste the copied block into it.
2. **Crucial Step:** You must overwrite the custom item's header with the base (default) item's data so the game replaces the standard equipment.

**Change this:**
```text
        "9455"
        {
            "name"      "Golden Full-Bore Bonanza"
            "prefab"        "wearable"
```

**To this:**
```text
        "282"
        {
            "name"      "Sniper's Cape"
            "prefab"        "default_item"
```

#### 4. Extract and Rename Models
1. Using Source 2 Viewer, find the compiled model file in `pak01_dir.vpk`:
   `models/items/sniper/sniper_cape_immortal/sniper_cape_immortal.vmdl_c`
2. Extract it.
3. Create the folder structure: `models/heroes/sniper`.
4. Place the extracted model inside and rename it to the default model name: `cape.vmdl_c`.

#### 5. Extract and Rename Particles
1. In `pak01_dir.vpk`, locate the following compiled particle files (`_c`):
   * `sniper_immortal_cape_golden_headshot_slow.vpcf_c`
   * `sniper_immortal_cape_golden_headshot_slow_caster.vpcf_c`
2. Extract them.
3. Create the folder structure: `particles/units/heroes/hero_sniper/`.
4. Place the particles inside and rename them to their default names (which you can reference in the `"asset"` lines of the code block above):
   * Rename to `sniper_headshot_slow.vpcf_c`
   * Rename to `sniper_headshot_slow_caster.vpcf_c`

#### 6. Final Placement and Installation
1. Move your newly created `models` and `particles` folders into your Patcher's `assets/pak01_dir` directory.
2. Navigate to `assets/items/Custom` and create a new folder named `sniper`. Place your modified `back.txt` file inside it.
3. Launch the script and click **Install**.

---

## Troubleshooting

### Script Cannot Find Dota 2 Path
If the script fails to locate your Dota 2 directory automatically, you can set it manually:
1. Create a file named `path.txt` inside the `assets` folder.
2. Paste your exact Dota 2 path into this file.

**Examples:**
* `C:\Program Files (x86)\Steam\steamapps\common\dota 2 beta`
* `D:\SteamLibrary\steamapps\common\dota 2 beta`

### Persistent Crashes or VAC Errors
If the game continues to crash or show VAC errors even after running **Install** and **Fix MM**, perform a clean reset:

1. Navigate to `Steam\steamapps\common\dota 2 beta\game\bin\win64` and delete:
   * `dota.signatures`
   * `dota.signatures_backup`
2. Navigate to `Steam\steamapps\common\dota 2 beta\game\dota` and delete:
   * `gameinfo_branchspecific.gi`
   * `gameinfo_branchspecific.gi_backup`
3. Navigate to `Steam\steamapps\common\dota 2 beta\game` and delete the folder:
   * `DotaModdingCommunityMods`
4. Open Steam and **Verify integrity of game files** for Dota 2.
5. Once verification is complete, run the script's **Install** process again.

---
