# Apple Health + Leo Health Stack Plan

## Kurzstatus

- WHOOP ist end-to-end produktiv getestet: OAuth, API-Sync, E-Mail-Export-Backfill, ActivityWatch-Buckets, GitHub CI.
- Apple Screen Time funktioniert lokal und hat ActivityWatch-Buckets; der stündliche launchd Job muss noch final hart geprüft werden, weil er zuletzt `not running` war.
- ActivityWatch Stack ist stabil: Doctor findet ActivityWatch API, WHOOP Buckets, Screen-Time Buckets und State/Dropzone.
- Apple Health Importer wurde als neues Repo umgesetzt: `aw-importer-apple-health`.
- Apple Health Importer ist ohne echte Gesundheitsdaten getestet: Fake-`export.xml`, Parser, Ruff, pytest, GitHub CI.

## Top 3 Wege, Apple Health zu verbinden

### 1. Apple Health Export ZIP / export.xml — beste sichere Startvariante

- iPhone Health App öffnen.
- Profilbild oben rechts.
- `Export All Health Data` / `Alle Gesundheitsdaten exportieren`.
- ZIP lokal auf den Mac bringen.
- Ablegen unter: `~/ActivityWatchImports/apple-health/`.
- Importieren mit:

```bash
aw-importer-apple-health inspect ~/ActivityWatchImports/apple-health/export.zip
aw-importer-apple-health import-export ~/ActivityWatchImports/apple-health/export.zip --dry-run
aw-importer-apple-health import-export ~/ActivityWatchImports/apple-health/export.zip
```

Vorteile:

- keine Cloud nötig
- lokal-first
- einfach zu prüfen
- gut für Backfill und erste Datenbasis

Nachteile:

- manuell
- nicht live
- große XML-Datei

### 2. Auto Health Export App / Health Auto Export — beste Automatik später

- iPhone-App exportiert HealthKit-Daten regelmäßig als JSON/CSV.
- Mac/Leo liest aus lokaler Dropzone oder lokalem Endpoint.
- Perfekt für tägliches Morning Briefing.

Vorteile:

- automatisch
- selektive Datentypen
- besser als riesige manuelle XML-Exports

Nachteile:

- zusätzliche App
- muss konfiguriert werden
- Datenschutz/Netzwerkmodus bewusst einstellen

### 3. iOS Shortcuts Bridge — beste minimalistische Live-Variante

- iPhone Shortcut sammelt nur wenige Werte:
  - Schritte gestern/heute
  - Schlaf
  - Ruhepuls
  - HRV
  - Mindful Minutes
  - Zahnbürsten-/Oclean-Daten, falls in HealthKit
- Shortcut sendet JSON lokal oder legt Datei in iCloud/Dropzone ab.

Vorteile:

- sehr kontrolliert
- kein riesiger Export
- ideal für tägliche Briefings

Nachteile:

- Shortcuts können hakelig sein
- nicht jeder HealthKit-Typ ist gleich angenehm exportierbar

## Was jetzt umgesetzt ist

- Neues Repo: `https://github.com/Martin-Hausleitner/aw-importer-apple-health`
- Lokaler Pfad: `/Users/mh/.openclaw/workspace/aw-importer-apple-health`
- CLI:
  - `aw-importer-apple-health inspect <export.xml|export.zip|export.xml.gz>`
  - `aw-importer-apple-health import-export <export.xml|export.zip|export.xml.gz> --dry-run`
  - `aw-importer-apple-health import-export <export.xml|export.zip|export.xml.gz>`
- Buckets:
  - `aw-importer-apple-health-daily`
  - `aw-importer-apple-health-vitals`
  - `aw-importer-apple-health-workout`
  - `aw-importer-apple-health-sleep`
  - `aw-importer-apple-health-mindfulness`
  - `aw-importer-apple-health-habits`
- Unterstützte Starttypen:
  - Steps
  - Active Energy
  - Heart Rate
  - Resting Heart Rate
  - HRV SDNN
  - Body Mass
  - Exercise Time
  - Mindful Sessions
  - Sleep Analysis
  - Toothbrushing Event
  - Workouts

## Teststatus

- `aw-importer-whoop`
  - pytest: 8 passed
  - ruff: OK
  - GitHub CI: success
- `aw-importer-apple-screentime`
  - pytest: 2 passed
  - ruff: OK
  - GitHub CI: success
- `aw-activitywatch-stack`
  - Doctor: ActivityWatch API OK
  - WHOOP buckets: 5 found
  - Screen-Time buckets: 4 found
  - GitHub CI: success
- `aw-importer-apple-health`
  - pytest: 1 passed
  - ruff: OK
  - sample parse: OK
  - secret scan: OK
  - GitHub CI: success

## Wichtig: keine echten Apple-Health-Daten exportiert

- Es wurde kein echter Apple-Health-Export von dir gelesen.
- Es wurde kein echtes `export.xml` verarbeitet.
- Es wurde nur ein künstliches Mini-Test-XML verwendet.
- Das Repo ignoriert echte Health-Exports via `.gitignore`.

## Nächster sauberer Schritt

1. Auf dem iPhone einmal Apple Health Export erzeugen.
2. ZIP nach `~/ActivityWatchImports/apple-health/` legen.
3. Erst `inspect` laufen lassen.
4. Dann `--dry-run`.
5. Erst danach echter Import in ActivityWatch.
6. Danach Doctor um Apple-Health-Buckets erweitern.
7. Danach Morning-Briefing-Skill bauen.

## Morning-Briefing Richtung

Leo soll nicht nur melden, was kaputt ist, sondern täglich sinnvoll informieren:

- Wetter und Kleidung
- Recovery / Trainingsempfehlung
- Schlaf und Energie
- Fokuszeit aus ActivityWatch
- Screen-Time Reflexion
- Apple Health Trends
- kurze Story oder Tagesimpuls
- klare Handlung für heute

## Sicherheitsregel

Keine medizinische Diagnose. Keine falsche Sicherheit. Health-Daten sind für Awareness, Coaching und Trends. Kritische Werte sollen vorsichtig eskalieren: Pause, beobachten, Arzt/medizinische Hilfe bei echten Warnzeichen.
