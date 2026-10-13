"""Render showcase screenshots of the Omarchy Bar Widget with fake demo data.

Generates crisp, high-resolution screenshots without exposing any private data:
- screenshots/bar-widget-messages.png (VIP letter badges & inline message reading)
- screenshots/bar-widget-contacts.png (VIP contact picker panel)
"""
from pathlib import Path
import shutil
import subprocess

SCREENSHOTS_DIR = Path(__file__).resolve().parent.parent / "screenshots"


def generate_messages_panel_svg() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" width="900" height="660" viewBox="0 0 900 660" font-family="'JetBrains Mono', 'Fira Code', 'DejaVu Sans', monospace">
  <defs>
    <filter id="shadow" x="-5%" y="-5%" width="115%" height="115%" filterUnits="userSpaceOnUse">
      <feGaussianBlur in="SourceAlpha" stdDeviation="16" />
      <feOffset dx="0" dy="12" />
      <feComponentTransfer><feFuncA type="linear" slope="0.45" /></feComponentTransfer>
      <feMerge>
        <feMergeNode />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
    <linearGradient id="barGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#14181c" />
      <stop offset="100%" stop-color="#0e1114" />
    </linearGradient>
    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#181c20" />
      <stop offset="100%" stop-color="#121518" />
    </linearGradient>
    <linearGradient id="btnGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#2a323a" />
      <stop offset="100%" stop-color="#1f252b" />
    </linearGradient>
  </defs>

  <!-- Background desktop area -->
  <rect width="100%" height="100%" fill="#0a0c0e" />

  <!-- Subtle grid pattern on desktop -->
  <g stroke="#1a2026" stroke-width="1" opacity="0.4">
    <line x1="0" y1="120" x2="900" y2="120" />
    <line x1="0" y1="240" x2="900" y2="240" />
    <line x1="0" y1="360" x2="900" y2="360" />
    <line x1="0" y1="480" x2="900" y2="480" />
    <line x1="0" y1="600" x2="900" y2="600" />
    <line x1="150" y1="0" x2="150" y2="660" />
    <line x1="300" y1="0" x2="300" y2="660" />
    <line x1="450" y1="0" x2="450" y2="660" />
    <line x1="600" y1="0" x2="600" y2="660" />
    <line x1="750" y1="0" x2="750" y2="660" />
  </g>

  <!-- Omarchy Status Bar at top -->
  <rect x="0" y="0" width="900" height="40" fill="url(#barGrad)" stroke="#222830" stroke-width="1" />

  <!-- Bar items left -->
  <text x="20" y="25" fill="#707880" font-size="13">󰣇</text>
  <text x="44" y="25" fill="#4fa6e8" font-size="12" font-weight="bold">1</text>
  <text x="62" y="25" fill="#707880" font-size="12">2</text>
  <text x="80" y="25" fill="#707880" font-size="12">3</text>

  <!-- Bar items center (Clock) -->
  <text x="400" y="25" fill="#cacccc" font-size="12" font-weight="500">Di 13 Okt 09:42</text>

  <!-- Bar items right (Status tray + VIPgram Bar Widget) -->
  <text x="610" y="25" fill="#707880" font-size="13">󰖩</text>
  <text x="635" y="25" fill="#707880" font-size="13">󰕾</text>
  <text x="660" y="25" fill="#707880" font-size="13">󰂄</text>

  <!-- VIPgram Bar Widget in Status Bar -->
  <!-- Active pill around VIP letters in the bar -->
  <rect x="690" y="6" width="60" height="28" rx="6" fill="#1e252c" stroke="#333d47" stroke-width="1" />
  <!-- Letter R (Rae) in Amber -->
  <text x="702" y="25" fill="#e5a442" font-size="13" font-weight="bold">R</text>
  <!-- Letter A (Ada) in Cyan -->
  <text x="724" y="25" fill="#42cbe5" font-size="13" font-weight="bold">A</text>

  <text x="765" y="25" fill="#707880" font-size="13">󰗊</text>
  <text x="795" y="25" fill="#707880" font-size="13">󰅐</text>
  <text x="825" y="25" fill="#707880" font-size="13">󰐥</text>

  <!-- Anchor indicator / connector line from bar letter R down to panel -->
  <line x1="707" y1="36" x2="707" y2="52" stroke="#e5a442" stroke-width="2" stroke-dasharray="3,3" />

  <!-- MessagesPanel Popup Window -->
  <g filter="url(#shadow)">
    <rect x="420" y="52" width="450" height="570" rx="12" fill="url(#cardGrad)" stroke="#333d47" stroke-width="1.5" />

    <!-- Panel Header -->
    <g transform="translate(442, 74)">
      <!-- Avatar Circle (Letter R) -->
      <circle cx="20" cy="20" r="20" fill="#3a2b16" stroke="#e5a442" stroke-width="1.5" />
      <text x="20" y="26" fill="#e5a442" font-size="16" font-weight="bold" text-anchor="middle">R</text>

      <!-- Contact Name & Subtitle -->
      <text x="52" y="16" fill="#ffffff" font-size="16" font-weight="bold">Rae</text>
      <text x="52" y="32" fill="#7a8490" font-size="12">@rae_bbs · 2 ungelesene Nachrichten</text>

      <!-- Header Action Buttons -->
      <!-- Mark Read Icon Button -->
      <rect x="300" y="6" width="28" height="28" rx="6" fill="#20272f" stroke="#323b45" stroke-width="1" />
      <text x="314" y="24" fill="#68c47a" font-size="13" text-anchor="middle">󰄲</text>

      <!-- Manage VIP List Icon Button -->
      <rect x="336" y="6" width="28" height="28" rx="6" fill="#20272f" stroke="#323b45" stroke-width="1" />
      <text x="350" y="24" fill="#a0aab6" font-size="13" text-anchor="middle">󰒓</text>

      <!-- Close Button -->
      <rect x="372" y="6" width="28" height="28" rx="6" fill="#20272f" stroke="#323b45" stroke-width="1" />
      <text x="386" y="24" fill="#a0aab6" font-size="13" text-anchor="middle">󰅖</text>
    </g>

    <!-- Separator -->
    <line x1="442" y1="130" x2="848" y2="130" stroke="#252c34" stroke-width="1" />

    <!-- Multi-VIP Chips Selector Row -->
    <g transform="translate(442, 142)">
      <!-- Selected Chip: Rae -->
      <rect x="0" y="0" width="115" height="28" rx="6" fill="#3d2d18" stroke="#e5a442" stroke-width="1.2" />
      <text x="12" y="18" fill="#e5a442" font-size="12" font-weight="bold">R</text>
      <text x="28" y="18" fill="#ffffff" font-size="11" font-weight="600">Rae (2)</text>

      <!-- Unselected Chip: Ada -->
      <rect x="125" y="0" width="115" height="28" rx="6" fill="#1a2027" stroke="#2d3742" stroke-width="1" />
      <text x="137" y="18" fill="#42cbe5" font-size="12" font-weight="bold">A</text>
      <text x="153" y="18" fill="#8d97a3" font-size="11">Ada (1)</text>
    </g>

    <!-- Message Bubbles Container -->
    <g transform="translate(442, 185)">
      <!-- Message 1 -->
      <rect x="0" y="0" width="406" height="88" rx="8" fill="#1b2128" stroke="#2d3742" stroke-width="1" />
      <text x="390" y="22" fill="#6e7884" font-size="11" text-anchor="end">Gestern 21:10</text>
      <text x="16" y="44" fill="#e4e6eb" font-size="13" font-family="'DejaVu Sans', sans-serif">carrier signal locked, who's up for</text>
      <text x="16" y="66" fill="#e4e6eb" font-size="13" font-family="'DejaVu Sans', sans-serif">a raid tonight?</text>

      <!-- Message 2 -->
      <rect x="0" y="100" width="406" height="72" rx="8" fill="#1b2128" stroke="#2d3742" stroke-width="1" />
      <text x="390" y="122" fill="#6e7884" font-size="11" text-anchor="end">09:04</text>
      <text x="16" y="144" fill="#e4e6eb" font-size="13" font-family="'DejaVu Sans', sans-serif">22:00 sharp, usual channel</text>

      <!-- Message 3 -->
      <rect x="0" y="184" width="406" height="72" rx="8" fill="#1b2128" stroke="#2d3742" stroke-width="1" />
      <text x="390" y="206" fill="#6e7884" font-size="11" text-anchor="end">09:05</text>
      <text x="16" y="228" fill="#e4e6eb" font-size="13" font-family="'DejaVu Sans', sans-serif">bring the good mod files this time</text>

      <!-- Message 4 (GIF attachment) -->
      <rect x="0" y="268" width="406" height="72" rx="8" fill="#1b2128" stroke="#2d3742" stroke-width="1" />
      <text x="390" y="290" fill="#6e7884" font-size="11" text-anchor="end">09:08</text>
      <text x="16" y="312" fill="#a0b4c8" font-size="13" font-family="'DejaVu Sans', sans-serif">🎬 [GIF: dance.gif] lol perfect</text>
    </g>

    <!-- Footer Action Buttons -->
    <g transform="translate(442, 560)">
      <!-- "In Omagram öffnen" button -->
      <rect x="0" y="0" width="235" height="40" rx="8" fill="url(#btnGrad)" stroke="#3e4a56" stroke-width="1" />
      <text x="117" y="25" fill="#ffffff" font-size="13" font-weight="bold" text-anchor="middle">󰗊  In Omagram öffnen</text>

      <!-- "Als gelesen markieren" button -->
      <rect x="247" y="0" width="159" height="40" rx="8" fill="#1a2027" stroke="#333e4b" stroke-width="1" />
      <text x="326" y="25" fill="#68c47a" font-size="13" font-weight="bold" text-anchor="middle">󰄲  Als gelesen</text>
    </g>
  </g>
</svg>
"""


def generate_contacts_panel_svg() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" width="900" height="660" viewBox="0 0 900 660" font-family="'JetBrains Mono', 'Fira Code', 'DejaVu Sans', monospace">
  <defs>
    <filter id="shadow" x="-5%" y="-5%" width="115%" height="115%" filterUnits="userSpaceOnUse">
      <feGaussianBlur in="SourceAlpha" stdDeviation="16" />
      <feOffset dx="0" dy="12" />
      <feComponentTransfer><feFuncA type="linear" slope="0.45" /></feComponentTransfer>
      <feMerge>
        <feMergeNode />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
    <linearGradient id="barGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#14181c" />
      <stop offset="100%" stop-color="#0e1114" />
    </linearGradient>
    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#181c20" />
      <stop offset="100%" stop-color="#121518" />
    </linearGradient>
  </defs>

  <rect width="100%" height="100%" fill="#0a0c0e" />

  <!-- Desktop Grid -->
  <g stroke="#1a2026" stroke-width="1" opacity="0.4">
    <line x1="0" y1="120" x2="900" y2="120" /><line x1="0" y1="240" x2="900" y2="240" />
    <line x1="0" y1="360" x2="900" y2="360" /><line x1="0" y1="480" x2="900" y2="480" />
    <line x1="0" y1="600" x2="900" y2="600" />
    <line x1="150" y1="0" x2="150" y2="660" /><line x1="300" y1="0" x2="300" y2="660" />
    <line x1="450" y1="0" x2="450" y2="660" /><line x1="600" y1="0" x2="600" y2="660" />
    <line x1="750" y1="0" x2="750" y2="660" />
  </g>

  <!-- Status Bar -->
  <rect x="0" y="0" width="900" height="40" fill="url(#barGrad)" stroke="#222830" stroke-width="1" />
  <text x="20" y="25" fill="#707880" font-size="13">󰣇</text>
  <text x="44" y="25" fill="#4fa6e8" font-size="12" font-weight="bold">1</text>
  <text x="62" y="25" fill="#707880" font-size="12">2</text>
  <text x="400" y="25" fill="#cacccc" font-size="12" font-weight="500">Di 13 Okt 09:42</text>
  <text x="690" y="25" fill="#4fa6e8" font-size="14">󰗊</text>
  <text x="720" y="25" fill="#707880" font-size="13">󰕾</text>
  <text x="745" y="25" fill="#707880" font-size="13">󰂄</text>

  <!-- ContactsPanel Popup -->
  <g filter="url(#shadow)">
    <rect x="420" y="52" width="450" height="570" rx="12" fill="url(#cardGrad)" stroke="#333d47" stroke-width="1.5" />

    <!-- Header -->
    <g transform="translate(442, 76)">
      <text x="0" y="20" fill="#ffffff" font-size="18" font-weight="bold">VIPgram · Kontaktauswahl</text>
      <rect x="336" y="2" width="28" height="28" rx="6" fill="#20272f" stroke="#323b45" stroke-width="1" />
      <text x="350" y="20" fill="#a0aab6" font-size="13" text-anchor="middle">󰑐</text>
      <rect x="372" y="2" width="28" height="28" rx="6" fill="#20272f" stroke="#323b45" stroke-width="1" />
      <text x="386" y="20" fill="#a0aab6" font-size="13" text-anchor="middle">󰅖</text>
    </g>

    <text x="442" y="125" fill="#7a8490" font-size="12">2 ausgewählt · 3 ungelesen</text>

    <!-- Search Input -->
    <g transform="translate(442, 140)">
      <rect x="0" y="0" width="406" height="36" rx="6" fill="#14181c" stroke="#2c3540" stroke-width="1" />
      <text x="12" y="23" fill="#606c7a" font-size="12">Name oder @Benutzername suchen …</text>
    </g>

    <!-- Toggle: Nur ausgewählte Kontakte -->
    <g transform="translate(442, 190)">
      <rect x="0" y="0" width="406" height="32" rx="6" fill="#1a2027" stroke="#252c34" stroke-width="1" />
      <text x="14" y="21" fill="#c0c8d2" font-size="12">Nur ausgewählte Kontakte</text>
      <rect x="370" y="7" width="24" height="16" rx="8" fill="#2e3844" />
      <circle cx="378" cy="15" r="6" fill="#808c9a" />
    </g>

    <!-- Contact List Items -->
    <g transform="translate(442, 235)">
      <!-- Item 1: Rae (Checked) -->
      <rect x="0" y="0" width="406" height="58" rx="8" fill="#1d242c" stroke="#e5a442" stroke-width="1" />
      <circle cx="24" cy="29" r="10" fill="#e5a442" />
      <text x="24" y="33" fill="#101315" font-size="11" font-weight="bold" text-anchor="middle">✓</text>
      <text x="46" y="24" fill="#ffffff" font-size="13" font-weight="bold">Rae</text>
      <text x="46" y="42" fill="#e5a442" font-size="11">@rae_bbs · 2 ungelesen</text>

      <!-- Item 2: Ada (Checked) -->
      <rect x="0" y="66" width="406" height="58" rx="8" fill="#1d242c" stroke="#42cbe5" stroke-width="1" />
      <circle cx="24" cy="95" r="10" fill="#42cbe5" />
      <text x="24" y="99" fill="#101315" font-size="11" font-weight="bold" text-anchor="middle">✓</text>
      <text x="46" y="90" fill="#ffffff" font-size="13" font-weight="bold">Ada</text>
      <text x="46" y="108" fill="#42cbe5" font-size="11">@ada_lovelace · 1 ungelesen</text>

      <!-- Item 3: Bob (Unchecked) -->
      <rect x="0" y="132" width="406" height="58" rx="8" fill="#171c22" stroke="#252c34" stroke-width="1" />
      <circle cx="24" cy="161" r="10" fill="#252d36" stroke="#485564" stroke-width="1.5" />
      <text x="46" y="156" fill="#c0c8d2" font-size="13">Bob</text>
      <text x="46" y="174" fill="#687280" font-size="11">@bobby · Keine ungelesenen Nachrichten</text>

      <!-- Item 4: Modem Pool (Unchecked) -->
      <rect x="0" y="198" width="406" height="58" rx="8" fill="#171c22" stroke="#252c34" stroke-width="1" />
      <circle cx="24" cy="227" r="10" fill="#252d36" stroke="#485564" stroke-width="1.5" />
      <text x="46" y="222" fill="#c0c8d2" font-size="13">Modem Pool</text>
      <text x="46" y="240" fill="#687280" font-size="11">Keine ungelesenen Nachrichten</text>
    </g>

    <!-- Info text & Bottom button -->
    <text x="442" y="535" fill="#6c7784" font-size="11" font-family="'DejaVu Sans', sans-serif">Wähle Personen aus, deren Direktnachrichten dich interessieren.</text>

    <g transform="translate(442, 555)">
      <rect x="0" y="0" width="406" height="42" rx="8" fill="#242c36" stroke="#3d4957" stroke-width="1" />
      <text x="203" y="26" fill="#ffffff" font-size="13" font-weight="bold" text-anchor="middle">󰗊  Omagram öffnen</text>
    </g>
  </g>
</svg>
"""


def render():
    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    rsvg_convert = shutil.which("rsvg-convert")
    assert rsvg_convert, "rsvg-convert is required"

    targets = [
        ("bar-widget-messages", generate_messages_panel_svg()),
        ("bar-widget-contacts", generate_contacts_panel_svg()),
    ]

    for name, svg_content in targets:
        svg_file = SCREENSHOTS_DIR / f"{name}.svg"
        png_file = SCREENSHOTS_DIR / f"{name}.png"
        svg_file.write_text(svg_content)
        subprocess.run([rsvg_convert, "-w", "1400", str(svg_file), "-o", str(png_file)], check=True)
        svg_file.unlink()
        print(f"wrote {png_file}")


if __name__ == "__main__":
    render()
