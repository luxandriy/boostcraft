#!/usr/bin/env python3
"""
booster-app/booster.py

Detect system RAM/CPU, generate recommended JVM arguments for Minecraft (Java 21),
and optimize the user's Minecraft options.txt for higher FPS.

This script is advisory and conservative: it creates backups before modifying
options.txt and writes recommended JVM args to booster-app/recommended_jvm_args.txt.

Requires: psutil

Usage:
  python booster.py [--dry-run] [--options PATH_TO_OPTIONS.TXT]

--dry-run    : don't modify files, just print changes
--options    : path to options.txt (if not provided the script will attempt common locations)

"""
import os
import sys
import psutil
import argparse
import datetime
from pathlib import Path

RECOMMENDED_KEYS = {
    # key: recommended value (string)
    # "graphics" can be "fast" or "fancy" or "fabulous" depending on client support.
    "graphics": "fast",
    "renderDistance": "8",            # chunks
    "maxFps": "240",                  # set high to avoid artificial cap (or set to your monitor refresh)
    "useVsync": "false",
    "fancyGraphics": "false",        # older clients may use this
    "mipmapLevels": "0",
    "particles": "decreased",        # options: all, decreased, minimal
    "clouds": "off",
    "ambientOcclusion": "false",
    "entityDistance": "6",           # if present, reduce entity render distance
    "simDistance": "8"               # server simulation distance
}

COMMON_OPTIONS_PATHS = [
    Path.home() / ".minecraft" / "options.txt",  # Linux, Windows (via %APPDATA%/.. using home fallback)
    Path(os.getenv("APPDATA", "")) / ".minecraft" / "options.txt",  # Windows explicit
    Path.home() / "Library" / "Application Support" / "minecraft" / "options.txt",  # macOS
]

OUT_JVM_PATH = Path("booster-app") / "recommended_jvm_args.txt"


def detect_system():
    mem = psutil.virtual_memory()
    total_ram_mb = int(mem.total / 1024 / 1024)
    cpu_count = psutil.cpu_count(logical=False) or psutil.cpu_count(logical=True) or 1
    cpu_logical = psutil.cpu_count(logical=True) or cpu_count
    load = None
    try:
        load = os.getloadavg()
    except Exception:
        pass

    return {
        "total_ram_mb": total_ram_mb,
        "cpu_physical_cores": cpu_count,
        "cpu_logical_cores": cpu_logical,
        "load_avg": load,
    }


def choose_heap_mb(total_ram_mb):
    # Heuristic: reserve at least 2 GB for OS + other apps, allocate ~60-75% of remaining to Minecraft.
    reserve_mb = 2048
    usable = max(1024, total_ram_mb - reserve_mb)
    # prefer around 60-75% of usable, clamp to common sensible limits
    heap = int(max(1024, min(12288, usable * 0.7)))
    # If machine is very small, ensure at least 1.5GB
    heap = max(heap, 1536)
    return heap


def choose_gc(total_ram_mb):
    # Suggest ZGC for very large heaps (if available), otherwise use G1GC for broad compatibility.
    if total_ram_mb >= 16000:
        return "ZGC"
    return "G1"


def build_jvm_args(heap_mb, gc):
    args = []
    args.append(f"-Xms{heap_mb}m")
    args.append(f"-Xmx{heap_mb}m")

    if gc == "ZGC":
        # ZGC flags (Java 11+ with ZGC available). Note: ZGC availability depends on JVM build.
        args += ["-XX:+UseZGC"]
    else:
        # G1 is a safe default across recent OpenJDK builds
        args += [
            "-XX:+UseG1GC",
            "-XX:MaxGCPauseMillis=50",
            "-XX:+UnlockExperimentalVMOptions",
            "-XX:+DisableExplicitGC",
            "-XX:+G1SummarizeConcMark",
            "-XX:+G1ReservePercent=20",
            "-XX:InitiatingHeapOccupancyPercent=35",
            "-XX:+ParallelRefProcEnabled",
        ]
        # String deduplication can help with memory but requires G1
        args.append("-XX:+UseStringDeduplication")

    # Other runtime flags that are usually safe
    args += [
        "-XX:+AlwaysPreTouch",  # can improve performance on some systems
        "-Djava.net.preferIPv4Stack=true",
    ]

    return args


def find_options_txt(provided_path: str = None):
    if provided_path:
        p = Path(provided_path).expanduser()
        if p.exists():
            return p
        return None

    for p in COMMON_OPTIONS_PATHS:
        if p and p.exists():
            return p
    return None


def read_options(path: Path):
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return None


def write_options(path: Path, lines):
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def optimize_options_lines(lines, recommendations):
    # Parse key:value lines and replace values for keys we know.
    kv = {}
    others = []

    for line in lines:
        if ":" in line:
            k, v = line.split(":", 1)
            kv[k] = v
        else:
            others.append(line)

    changed = False
    for k, v in recommendations.items():
        if k in kv:
            if kv[k] != v:
                kv[k] = v
                changed = True
        else:
            # append to end if not present
            kv[k] = v
            changed = True

    out_lines = []
    # Reconstruct lines preserving original order roughly: start with original keys
    seen = set()
    for line in lines:
        if ":" in line:
            k, _ = line.split(":", 1)
            out_lines.append(f"{k}:{kv[k]}")
            seen.add(k)
        else:
            out_lines.append(line)

    # Append any new keys not in original
    for k in recommendations.keys():
        if k not in seen:
            out_lines.append(f"{k}:{kv[k]}")

    return out_lines, changed


def main():
    parser = argparse.ArgumentParser(description="BoostCraft helper: suggest JVM args and optimize Minecraft options.txt for FPS")
    parser.add_argument("--dry-run", action="store_true", help="Don't modify files; print recommended changes")
    parser.add_argument("--options", type=str, help="Path to options.txt")
    args = parser.parse_args()

    sys_info = detect_system()
    total_ram_mb = sys_info["total_ram_mb"]
    cpu_cores = sys_info["cpu_physical_cores"]

    heap_mb = choose_heap_mb(total_ram_mb)
    gc = choose_gc(total_ram_mb)
    jvm_args = build_jvm_args(heap_mb, gc)

    print("Detected system:")
    print(f"  Total RAM: {total_ram_mb} MB")
    print(f"  CPU physical cores: {cpu_cores}")
    if sys_info.get("load_avg"):
        print(f"  Load avg: {sys_info['load_avg']}")

    print("\nRecommended JVM arguments:")
    print(" ".join(jvm_args))

    # Ensure output directory exists
    OUT_JVM_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not args.dry_run:
        OUT_JVM_PATH.write_text(" ".join(jvm_args) + "\n", encoding="utf-8")
        print(f"Wrote recommended JVM args to {OUT_JVM_PATH}")

    # Attempt to locate options.txt
    options_path = find_options_txt(args.options)
    if not options_path:
        print("\nCould not locate options.txt automatically. Pass --options /path/to/options.txt to modify it.")
        return 0

    print(f"\nFound options.txt at: {options_path}")

    # Read original
    orig_lines = read_options(options_path)
    if orig_lines is None:
        print("Failed to read options.txt")
        return 1

    new_lines, changed = optimize_options_lines(orig_lines, RECOMMENDED_KEYS)

    if not changed:
        print("No changes required for options.txt (values already match recommendations)")
        return 0

    if args.dry_run:
        print("\nDry run: the following changes would be applied to options.txt:")
        for a, b in zip(orig_lines, new_lines):
            if a != b:
                print(f"- {a}")
                print(f"+ {b}")
        # print any appended lines
        if len(new_lines) > len(orig_lines):
            for line in new_lines[len(orig_lines):]:
                print(f"+ {line}")
        return 0

    # Backup and write
    backup = options_path.with_name(options_path.name + ".bak")
    try:
        # create timestamped backup copy
        ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        backup = options_path.with_name(options_path.name + ".bak." + ts)
        options_path.replace(backup)
        print(f"Backed up original options.txt to {backup}")

        # write new options to original path
        write_options(options_path, new_lines)
        print(f"Wrote optimized options.txt to {options_path}")

    except Exception as e:
        print(f"Failed to backup/modify options.txt: {e}")
        return 1

    print("\nOptimization complete. Launch Minecraft and test FPS. Consider combining with Sodium/Lithium/FerriteCore for best results.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
