#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path
import yaml

# -----------------------------------------------------------------------------
# Colors
# -----------------------------------------------------------------------------
class Colors:
    RESET = "\033[0m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"

def info(msg): print(f"{Colors.GREEN}✔ {msg}{Colors.RESET}")
def error(msg): print(f"{Colors.RED}✘ {msg}{Colors.RESET}", file=sys.stderr)
def debug(msg, enabled):
    if enabled:
        print(f"{Colors.CYAN}[DEBUG]{Colors.RESET} {msg}")

# -----------------------------------------------------------------------------
# Colourised Help Formatter
# -----------------------------------------------------------------------------
class ColorHelpFormatter(argparse.RawTextHelpFormatter):
    def start_section(self, heading):
        heading = f"{Colors.CYAN}{heading.capitalize()}:{Colors.RESET}"
        super().start_section(heading)

# -----------------------------------------------------------------------------
# Quoted YAML handling
# -----------------------------------------------------------------------------
class QuotedString(str): pass

def quoted_presenter(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')

yaml.add_representer(QuotedString, quoted_presenter)

# -----------------------------------------------------------------------------
# Run command helper
# -----------------------------------------------------------------------------
def run_command(cmd, cwd, debug_enabled):
    debug(f"Running: {cmd}", debug_enabled)
    result = subprocess.run(
        cmd, shell=True, text=True, capture_output=True, cwd=cwd
    )

    if result.returncode != 0:
        stderr = result.stderr.strip()
        if "doesn't exist" in stderr:
            error(stderr)   # Magento already gives a clear message
        else:
            error(f"Command failed: {cmd}\n{stderr}")
        sys.exit(1)

    return result.stdout.strip().splitlines()

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        prog="magento-config-exporter",
        description=f"{Colors.GREEN}Export selected Magento configuration values into YAML.{Colors.RESET}",
        usage="magento-config-exporter [options] PATHS_FILE",
        epilog=(
            f"{Colors.YELLOW}Examples:{Colors.RESET}\n"
            "  magento-config-exporter paths.yaml\n"
            "  magento-config-exporter paths.yaml --scope stores --scope-code english\n"
            "  magento-config-exporter paths.yaml --magento-dir /var/www/magento --no-interaction\n"
        ),
        formatter_class=ColorHelpFormatter,
    )

    # Positional (required)
    parser.add_argument(
        "paths_file",
        metavar="PATHS_FILE",
        type=str,
        help="YAML file with list of config path prefixes (key: 'paths')",
    )

    # Options
    parser.add_argument("-d", "--magento-dir", type=str, default=".", help="Path to Magento installation (default: current directory)")
    parser.add_argument("-s", "--scope", type=str, default="default", choices=("default", "stores", "websites"), help="Config scope (default: default)")
    parser.add_argument("-c", "--scope-code", type=str, help="Optional scope code (e.g. 'english')")
    parser.add_argument("-o", "--output-dir", type=str, help="Override output directory (default: {magento-dir}/var/magento-config-exporter/)")
    parser.add_argument("-y", "--no-interaction", action="store_true", help="Do not ask for confirmation before exporting")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")

    args = parser.parse_args()

    magento_dir = Path(args.magento_dir).resolve()
    magento_bin = magento_dir / "bin" / "magento"

    if not magento_bin.exists():
        error(f"No Magento CLI found at {magento_bin}")
        sys.exit(1)

    # Load paths from YAML
    paths_file = Path(args.paths_file).resolve()
    if not paths_file.exists():
        error(f"Paths file not found: {paths_file}")
        parser.print_help()
        sys.exit(1)

    with open(paths_file) as f:
        data = yaml.safe_load(f) or {}
    paths = data.get("paths", [])
    if not paths:
        error("No 'paths' key or empty list in paths YAML file")
        parser.print_help()
        sys.exit(1)

    debug(f"Loaded {len(paths)} paths", args.debug)

    # Build base command
    base_cmd = [str(magento_bin), "config:show", f"--scope={args.scope}"]
    if args.scope_code:
        base_cmd.append(f"--scope-code={args.scope_code}")

    # Run once and get all config lines
    all_lines = run_command(" ".join(base_cmd), magento_dir, args.debug)

    # Collect results
    export_data = {}
    scope_name = args.scope_code if args.scope_code else args.scope
    export_data[QuotedString(scope_name)] = {}

    for line in all_lines:
        if " - " not in line:
            continue
        key, value = line.split(" - ", 1)
        key = key.strip()
        value = value.strip()

        # Only include keys that start with one of the requested paths
        for path in paths:
            if key.startswith(path):
                export_data[QuotedString(scope_name)][QuotedString(key)] = QuotedString(value)

    # Determine output directory (default to {magento-dir}/var/magento-config-exporter)
    if args.output_dir:
        output_dir = Path(args.output_dir).resolve()
    else:
        output_dir = magento_dir / "var" / "magento-config-exporter"

    # Ensure output dir exists
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
        info(f"Created output directory: {output_dir}")

    # Determine file name
    if args.scope_code:
        filename = f"{args.scope}-{args.scope_code}.yaml"
    else:
        filename = f"{args.scope}.yaml"

    output_file = output_dir / filename

    # Show plan
    print("")
    print(f"Using input:   {paths_file}")
    print(f"Exporting to:  {output_file}")
    print("")

    if not args.no_interaction:
        confirm = input("Continue? [y/N]: ").strip().lower()
        if confirm not in ("y", "yes"):
            error("Aborted by user")
            sys.exit(1)

    # Write YAML
    with open(output_file, "w") as f:
        yaml.dump(export_data, f, sort_keys=True, allow_unicode=True)

    info(f"Exported {len(export_data[scope_name])} values → {output_file}")


if __name__ == "__main__":
    main()