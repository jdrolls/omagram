# Rust-Portierungsplan für Omagram

## Entscheidung

Kein Big-Bang-Port. Omagram ist vor allem Netzwerk- und Terminal-I/O; Rust ist
hier kein automatisch messbarer Geschwindigkeitsgewinn. Die riskanten Teile
sind die vollständige MTProto-Funktionsparität und das terminalabhängige
Bild-Rendering. Der Port beginnt deshalb mit einem zeitlich begrenzten Spike
und wird nur bei nachgewiesener Funktionsparität fortgesetzt.

Die Python-Version bleibt bis zur bestanden Abnahme produktiv. `BarWidget.qml`,
`manifest.json` und die Bedienung bleiben unverändert; `run-omagram` wechselt
erst im letzten Schritt zum Rust-Binary.

## Ist-Zustand und Zielgrenzen

| Bereich | Python heute | Rust-Ziel |
| --- | --- | --- |
| Telegram | `telegram_tui/client.py`, Telethon | `grammers-client` auf Tokio; nur wenn der Spike alle unten genannten Aufrufe abdeckt |
| TUI | `telegram_tui/app.py`, Textual | Ratatui + Crossterm, neu implementierte Zustandsmaschine |
| Medien | Sixel, Textual TGP, Halfcell | Halfcell zuerst; Sixel/Kitty nur nach isoliertem Protokolltest |
| Sicherheit | `security.py`, 483 Zeilen | `rustix` und `OwnedFd`; keine Abschwächung der `openat`-basierten Prüfungen |
| Konfiguration/Logs | `.env`, private Dateien | `.env`-Kompatibilität mit `dotenvy`; `tracing` mit privaten, rotationsfähigen Logs |

Die Datentypen `Dialog`, `DialogTab`, `Message` und `RecentGif` aus
`telegram_tui/client.py` sind die fachliche Schnittstelle. Sie werden als
Rust-Structs beibehalten. Textual-Klassen, Telethon-Objekte und die Telethon-
Sessiondatei werden nicht portiert. Nach dem Wechsel ist eine erneute Telegram-
Anmeldung erforderlich.

## Phase 0 – Machbarkeitsspitze (Freigabekriterium)

Ein einzelnes, nicht auslieferbares Rust-Binary bauen, das gegen ein Testkonto
folgendes nachweist:

1. QR-Login sowie Telefon-Code und 2FA; eine neue Session sicher speichern.
2. Dialoge, Telegram-Ordner (`GetDialogFilters`), Nachrichten und New-Message-
   Updates laden.
3. Lokale Datei und gespeichertes GIF senden; gespeicherte GIFs und deren
   Thumbnail laden.
4. Medien-Download vorab nach deklarierter Größe und während des Streams bei
   2 GiB abbrechen.
5. Ein JPEG als Halfcell ausgeben und in Foot ein Sixel-Bild korrekt platzieren.

Abbruchregel: Fehlt eine dieser MTProto-Operationen in `grammers` oder verlangt
sie unvertretbare Low-Level-Protokollarbeit, bleibt der produktive Client
Python/Telethon. Kein eigener MTProto-Stack für Omagram.

## Phase 1 – Fundament ohne UI

Ein einziges Cargo-Paket `omagram` anlegen, kein Workspace und keine
Abstraktionsschicht. Module: `security`, `config`, `logging`, `telegram`,
`model`, `main`.

Minimale Abhängigkeiten nach bestandenem Spike: `tokio`, `grammers-client`,
`grammers-tl-types`, `ratatui`, `crossterm`, `rustix`, `serde`, `toml`,
`dotenvy`, `tracing`, `tracing-subscriber`, `image`, `qrcode`, `sha2` und
`uuid`. `clap` nur wenn die vorhandenen Befehle `run`, `auth`, `setup` nicht
mit einer kleinen manuellen Argumentauswertung klarer bleiben.

Zuerst die sicherheitsrelevanten Invarianten aus `security.py`, `config.py` und
`logging_config.py` übertragen: vertrauenswürdige Binärpfade, kontrolliertes
`PATH`, keine Symlinks, privat erzeugte Verzeichnisse/Dateien, atomare Writes
und Größenlimits. Die vorhandenen Security- und Config-Tests werden als
Rust-Tests portiert, bevor Telegram-Code darauf schreibt.

## Phase 2 – Telegram-Backend

`telegram` implementiert nur die vorhandene Fachschnittstelle: Verbindung,
Authentifizierung, Dialoge/Ordner, Nachrichten, Senden, gespeicherte GIFs,
Thumbnails, Download und New-Message-Callback. Die UI erhält nie Bibliotheks-
spezifische Telegram-Typen.

Die bestehenden Tests zu Dialogfiltern, Uploads und Medienlimits werden gegen
einen Fake-Transport neu geschrieben. Der Live-Test bleibt ein separater,
nicht automatischer Test gegen ein Testkonto.

## Phase 3 – TUI ohne Pixelgrafik

Mit Ratatui erst die bedienbare Basis liefern: Chatliste, Ordnerwechsel,
Nachrichtenansicht, Composer, Reload, Sidebar, Escape-Verhalten und Fehler-
meldungen. Zustand zentral in einer `AppState`-Struktur halten; jede Eingabe
und jedes Telegram-Event aktualisiert diesen Zustand, danach rendert Ratatui.

Die verhaltensstarken Fälle aus `tests/test_app_media_upload.py` sind die
Spezifikation: ein gestarteter Upload behält seinen Empfänger, ein fehlgeschla-
gener Send verliert keinen Entwurf, und veraltete Ladeantworten überschreiben
den aktuellen Chat nicht.

## Phase 4 – Medien und Integrationen

Halfcell mit `image` zuerst als universellen Fallback implementieren. Danach
Sixel für Foot und Kitty-Graphics getrennt hinter einer Capability-Erkennung
testen; keine ungeprüfte Bildbibliothek zum Kernbestand machen. Für GIF/Video
bleibt `mpv`, sonst `xdg-open`; Prozesse verwenden weiter ausschließlich den
kontrollierten Binärsuchpfad. Omarchy-Dateiauswahl und Theme-`colors.toml`
kommen erst nach der textbasierten TUI.

## Phase 5 – Abnahme und Umschalten

1. Alle portierten Unit-Tests, `cargo fmt --check`, `cargo clippy -- -D warnings`
   und `cargo test` sind grün.
2. Manuell prüfen: Erstlogin, 2FA, Ordner, Upload-Abbruch, GIF-Auswahl,
   Foot-Sixel, kleiner Terminalmodus, Themewechsel sowie Start über Widget und
   Omarchy-Menü.
3. `run-omagram` nur dann auf das Rust-Binary umstellen. Python-Startweg eine
   Release lang als dokumentierten Fallback belassen; danach entfernen.

## Vergleichsprojekte

- [tgt](https://github.com/FedericoBruzzone/tgt) ist der beste Referenzclient:
  aktiv (Push 2026-09-15), Apache-2.0/MIT, Ratatui/Crossterm/Tokio, aber mit
  TDLib statt direktem MTProto. Architektur und Test-/Releasepraxis übernehmen,
  nicht den Telegram-Unterbau.
- [Ithil](https://github.com/LvcasX1/ithil) nutzt Ratatui, Crossterm und
  `grammers` für echten MTProto. Geeignet als API- und UI-Referenz, aber klein
  und zuletzt 2026-06 aktualisiert – kein Kopierfundament.
- [kittyview](https://github.com/gominimal/kittyview) ist ein aktiver,
  Apache-2.0-lizenzierter Rust-Referenzcode für Capability-Erkennung und
  chunked Kitty-Graphics. Er ergänzt Foot/Sixel nicht.
- [glow](https://github.com/isene/glow) zeigt die Kombination Kitty, Sixel und
  Halfblock. Wegen kleiner Codebasis und externer ImageMagick-Pfade nur als
  Protokollreferenz, nicht als harte Abhängigkeit.
