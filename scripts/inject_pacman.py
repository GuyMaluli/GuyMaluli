from pathlib import Path
import re
import sys


TERMINAL_PATH = Path("assets/maluliterminal.svg")
PACMAN_PATH = Path("dist/pacman-contribution-graph-dark.svg")


def get_attribute(tag: str, name: str, default: str) -> str:
    match = re.search(rf'\b{name}="([^"]+)"', tag)
    return match.group(1) if match else default


def main() -> None:
    if not TERMINAL_PATH.exists():
        raise FileNotFoundError(
            f"Terminal SVG not found: {TERMINAL_PATH}"
        )

    if not PACMAN_PATH.exists():
        raise FileNotFoundError(
            f"Generated Pac-Man SVG not found: {PACMAN_PATH}"
        )

    terminal = TERMINAL_PATH.read_text(encoding="utf-8")
    pacman = PACMAN_PATH.read_text(encoding="utf-8")
 
    pacman = re.sub(
        r"^\s*<\?xml[^>]*\?>\s*",
        "",
        pacman,
    )

    pacman_match = re.search(
        r"<svg\b([^>]*)>(.*)</svg>\s*$",
        pacman,
        flags=re.DOTALL,
    )

    if not pacman_match:
        raise ValueError("Could not parse generated Pac-Man SVG")

    pacman_attributes = pacman_match.group(1)
    pacman_content = pacman_match.group(2)

    viewbox_match = re.search(
        r'viewBox="([^"]+)"',
        pacman_attributes,
    )

    pacman_viewbox = (
        viewbox_match.group(1)
        if viewbox_match
        else "0 0 1166 184"
    )

    anchor_position = terminal.find("run pacman.exe")

    if anchor_position == -1:
        raise ValueError(
            'Could not find "run pacman.exe" inside maluliterminal.svg'
        )

    svg_start = terminal.find("<svg", anchor_position)

    if svg_start == -1:
        raise ValueError(
            "Could not find the embedded Pac-Man SVG"
        )

    opening_tag_match = re.match(
        r"<svg\b[^>]*>",
        terminal[svg_start:],
    )

    if not opening_tag_match:
        raise ValueError("Could not read embedded SVG opening tag")

    old_opening_tag = opening_tag_match.group(0)

    svg_tags = re.finditer(
        r"</?svg\b[^>]*>",
        terminal,
        flags=re.IGNORECASE,
    )

    depth = 0
    svg_end = None

    for tag_match in svg_tags:
        if tag_match.start() < svg_start:
            continue

        tag = tag_match.group(0)

        if tag.startswith("</"):
            depth -= 1

            if depth == 0:
                svg_end = tag_match.end()
                break
        else:
            depth += 1

    if svg_end is None:
        raise ValueError(
            "Could not locate the end of the old Pac-Man SVG"
        )

    x = get_attribute(old_opening_tag, "x", "55")
    y = get_attribute(old_opening_tag, "y", "1250")
    width = get_attribute(old_opening_tag, "width", "990")
    height = get_attribute(old_opening_tag, "height", "180")

    updated_pacman = f"""<svg
  x="{x}"
  y="{y}"
  width="{width}"
  height="{height}"
  viewBox="{pacman_viewbox}"
  preserveAspectRatio="xMidYMid meet"
>
{pacman_content}
</svg>"""

    updated_terminal = (
        terminal[:svg_start]
        + updated_pacman
        + terminal[svg_end:]
    )

    TERMINAL_PATH.write_text(
        updated_terminal,
        encoding="utf-8",
    )

    print("Pac-Man was successfully updated inside the terminal.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
