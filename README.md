## Generiert Aufgabenblätter aus Vorlagen

![Beispiel für Lösungsblatt](https://raw.githubusercontent.com/Ryz3D/generate_exam/master/docs/example1.png)
![Beispiel für Aufgabenblatt](https://raw.githubusercontent.com/Ryz3D/generate_exam/master/docs/example2.png)
![Beispiel für Vorlage](https://raw.githubusercontent.com/Ryz3D/generate_exam/master/docs/example.png)

Features:
  - Volle LaTeX-Unterstützung
  - Automatisches Einsetzen von gegebenen Werten an allen Stellen des Texts
  - Ausrechnen von Lösungen durch vorgegebene Formeln
  - Einsetzen von Werten in Formeln
  - Gesamtpunktzahl berechnet
  - Abhängigkeiten von anderen Aufgabenteilen als Notiz

Dependencies:
  - Python 3 (Getestet auf 3.9.0 und 3.7.3)
  - MikTex oder LiveTex, um pdflatex zu nutzen
    - Für LiveTex müssen standardmäßig folgende LaTeX-Pakete intalliert werden (Mit MikTex automatisch): wrapfig, graphicx, textgreek, amsmath, caption, geometry, fancyhdr, lastpage

Nutzung:
```
python main.py (OPTIONEN) [DATEI]

OPTIONEN:
    -h      --help      Benutzungshilfe anzeigen
    -a      --all       Läuft für alle .xml Vorlagen -> Kein Dateiname notwendig
    -s      --sol       Generiert zusätzlich Lösungsblatt
    -c      --calc      Interaktive Konsole um mathematische Ausdrücke zu lösen (unabhängig vom Hauptprogramm)
    -o DIR  --out DIR   Bewegt den .pdf Output in den angegebenen Ordner
    -l LVL  --log LVL   Legt Anzahl der Meldungen fest (1: Nur Fehler ... 3: Kompletter Debug-Output)

DATEI:
    Notwendig ohne -h -a oder -c
    Dateinamen mit .xml Endung angeben. Die Vorlage muss sich im "{files}" Ordner befinden. Skript vom Hauptordner aus starten.

ACHTUNG:
    Dateien im Output-Ordner werden automatisch überschrieben!

BEISPIELKOMMANDOS:
    python main.py -l 3 "example.xml"   Generiert Aufgabenblatt für "example.xml" mit Debug-Output
    python main.py -a -l 0 -s -o "out"  Generiert Lösungs- und Aufgabenblätter im "out" Ordner für alle Dateien mit Fehler-Output.
    python main.py -c                   Startet Ausdruckslöser
```
