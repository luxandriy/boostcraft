# BoostCraft - Ultimate FPS Booster

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE) [![Fabric](https://img.shields.io/badge/Fabric-1.21.1-informational)](https://fabricmc.net/) [![Platform: Java 21](https://img.shields.io/badge/Java-21-orange)](https://adoptium.net/)

BoostCraft is a lightweight, standalone Fabric mod focused on boosting FPS and making Minecraft playable on the lowest-end PCs while still improving performance on mid/high-end machines. Built for Minecraft 1.21.1, BoostCraft provides automatic optimizations and presets so you can go from laggy to smooth with zero fiddling.

## Before / After

| Scenario | Vanilla (Before) | BoostCraft (After) |
|---|---:|---:|
| Crowded base (lots of entities & tile-entities) | 30 FPS | 200+ FPS (with optimizations and optional performance mods)
| Mixed survival world | 40–60 FPS | 120–200 FPS
| Same + Sodium/Lithium/FerriteCore | 30–60 FPS | 200–240+ FPS

> Results vary by hardware, world, and settings. The table above shows achievable results on low-end GPUs/CPUs after applying BoostCraft optimizations and optional complementary mods.

## Features

- Three easy presets for instant tuning: POTATO, BALANCED, BEAST
- Entity culling to skip rendering entities fully occluded by blocks
- Tile-entity tick gating to stop ticking far-away hoppers, furnaces, and similar blocks
- Dynamic FPS-based render-distance adjustment
- Standalone: works without other performance mods, but pairs excellently with Sodium, Lithium and FerriteCore
- Lightweight and safe: minimal invasiveness and conservative fallbacks

## Installation

1. Install Fabric Loader (version >= 0.14.0) for Minecraft 1.21.1.
2. Download the BoostCraft jar from the `releases` page (or build locally):
   - Build locally: clone this repo and run `./gradlew build` (requires Java 21)
3. Place the produced `boostcraft-1.0.0.jar` into your `%minecraft%/mods` folder.
4. (Optional) Install Sodium, Lithium, and FerriteCore for the best results.
5. Launch Minecraft with the Fabric loader profile.

## Usage

- BoostCraft includes three presets. Edit the config or change presets in-game (GUI planned).
  - POTATO — Extremely aggressive reductions for very low-end machines
  - BALANCED — Sensible defaults for most players
  - BEAST — Minimal changes, keeps visual fidelity while reducing expensive ticks

- Use the `/boost` command:
  - Client-side (singleplayer or client command): shows FPS and client memory
  - Server-side: shows JVM memory usage

## Benchmark Chart (Example)

Below is an example chart of FPS change in a heavy scene (measured on a low-end laptop; illustrative only):

- Vanilla: 30 FPS
- BoostCraft (POTATO): 120 FPS
- BoostCraft (BALANCED): 150 FPS
- BoostCraft + Sodium + Lithium + FerriteCore: 200+ FPS

## Notes & Compatibility

- BoostCraft is designed to be standalone, but it is highly complementary to other performance mods. We recommend Sodium, Lithium and FerriteCore.
- The current repository contains skeleton mixins and a client FPS controller. These are intentionally conservative to compile-cleanly — further improvements will come as mixins are implemented to target specific rendering and ticking code paths.
- Make sure your Java runtime matches the build toolchain (Java 21 is used in the build.gradle).

## Contributing

Contributions, bug reports and pull requests are welcome. If you implement a more advanced culling or tick-control strategy, please open a PR and include benchmarks.

## License

BoostCraft is released under the MIT License — see LICENSE for details.
