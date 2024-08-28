# Mannschaften-correct

Ein kleines CLI-Tool, um die Einträge der Mannschaften für das Kegelprogramm zu importieren/korrigieren.
Zurzeit wird nur das Programm "Kegel-Control-Center" des Technikum Kamenz unterstützt.

## Installation

Es wird Python 3.10 oder höher benötigt.

```bash
python --version
```

Sollte die Version unter 3.10 sein, dann bitte Python 3.10 oder höher installieren.
Beispiel:

```
Python 3.12.0
```

Am Anfang kann die CSV-Datei `Spieler.csv` und `Mannschaft.csv` im working directory
(momentanes Verzeichnis) erstellt werden.

```bash
python create_default_csv.py
```

Dabei wird geprüft, ob die Dateien bereits existieren. Sollte dies der Fall sein, wird eine Warnung ausgegeben und gefragt, ob die Dateien überschrieben werden sollen.

## Verwendung

starten des Programms:

```bash
python main.py
```

In der Konsole wird eine Auswahl angezeigt, welche Aktionen durchgeführt werden können.

```
1 - Neue Mannschaft erstellen (als Input)
2 - Mannschaft neu einlesen und korrigieren
3 - Mannschaften aus CSV einlesen (mit Platzhaltern)
4 - Alle Mannschaften korrigieren (mit Platzhaltern)
- Export -
5 - Exportiere eine Mannschaft als CSV
6 - Exportiere alle Mannschaften als CSV


end - Programm beenden
```

Die Aktionen 1-4 können durch die Eingabe der entsprechenden Zahl ausgewählt werden.
Die Aktion "end" beendet das Programm.

### Neue Mannschaft erstellen

Erstellt eine neue Mannschaft mit den eingegebenen Daten.
Zuerst wird der Name der Mannschaft abgefragt.
Sollte die Mannschaft bereits existieren, wird eine Warnung ausgegeben und es wird gefragt, ob die Mannschaft überschrieben werden soll.
Der Default-Wert ist "ja".
Die Mannschaft wird im `out/`-Ordner als CSV-Datei gespeichert. Der Name der Datei ist der Name der Mannschaft.
Danach werden die allgemeinen Daten der Mannschaft abgefragt.

1. Spielklasse (Kreis, Bezirk, Land, ...)
2. Liga (Kreisklasse, Kreisliga, ...)
3. Bezirk
4. Spielführer
5. Betreuer
6. Vereinsnummer
7. LV-Nummer
8. Anzahl der Spieler (Default: 10)
   All diese Werte können auch leer gelassen werden.

Danach werden die Daten der Spieler geladen. Die Daten der Spieler stehen in der Datei
`Spieler.csv` im working directory (Momentanes Verzeichnis).
Die Datei muss folgendes Spalten haben (Reihenfolge ist egal):

* Name
* Vorname
* Geburtsdatum
* Geschlecht
* Altersklasse
* Passnummer
* Verein
* Verein_angezeigt

Die gefundenen Spieler werden danach nach Namen sortiert.
Sollten mehr Spieler gefunden werden, als in der Mannschaft benötigt werden, werden die überschüssigen Spieler ignoriert.
Sind es weniger Spieler, als benötigt werden, werden Platzhalter hinzugefügt.

### Mannschaft neu einlesen und korrigieren

Die Mannschaft wird neu eingelesen und korrigiert.
Korrigiert wird haupsächlich die Anzahl der Spieler und die Reihenfolge der Spieler sowie das Geburtstdatum.
Dazu wird der Name der Mannschaft abgefragt. Es handelt sich dabei um den Namen der
`.ini`-Datei im momentanen Verzeichnis.
Die Endung `.ini` wird automatisch hinzugefügt, wenn er vergessen wird.
Danach wird der neue Name der Mannschaft abgefragt. Dieser kann auch leer gelassen werden.
Die Mannschaft wird im `out/`-Ordner als CSV-Datei gespeichert. Der Name der Datei ist der Name der Mannschaft.
Intern wird die Mannschaft wie folgt korrigiert:

* Korrektur des Geburtsdatums
* Korrektur der Anzahl der Spieler
* Korrektur der Reihenfolge der Spieler (Nachname sortiert)
* Setzt Platzhalter ans Ende der Liste

### Mannschaften aus CSV einlesen

Importiert die Mannschaften aus einer CSV-Datei.
Dies ist ziemlich ähnlich zu "Neue Mannschaft erstellen", nur dass mehrere Mannschaften aus konkreten
CSV-Dateien (Spieler.csv und Mannschaft.csv) gelesen werden.
Hier wird explizit nach der minimalen Anzahl der Platzhalter gefragt, die hinzugefügt werden sollen.
Der Rest wird aus den CSV-Dateien gelesen.
Dabei werden mindestens 10 Spieler in der Mannschaft erstellt.
Sollte die Anzahl der Spieler in der CSV-Datei kleiner sein, werden weitere Platzhalter hinzugefügt.
Sollten genügend Spieler vorhanden sein, werden dennoch die Mindestanzahl an Platzhaltern hinzugefügt.
Auch hier werden die Spieler nach Namen sortiert.
Alle Mannschaften werden im `out/`-Ordner als CSV-Datei gespeichert. Der Name der Datei ist der Name der Mannschaft.

### Alle Mannschaften korrigieren

Hier werden alle im Basisverzeichnis vorhandenen Mannschaften korrigiert. Das Basisverzeichnis kann in
`main.py` geändert werden.
Standardmäßig ist es `C:\Control Center Kegeln\Einstellungen\Mannschaften`.
Die Mannschaften werden wie bei "Mannschaft neu einlesen und korrigieren" korrigiert.
Hier wi

### Exportiere eine Mannschaft als CSV

Exportiert eine Mannschaft als CSV-Datei. Der Name der Mannschaft wird abgefragt. Es handelt sich dabei um den Namen
der `.ini`-Datei im Basisverzeichnis.

### Exportiere alle Mannschaften als CSV

Exportiert alle Mannschaften im Basisverzeichnis als CSV-Dateien.
Alle Mannschaften werden im `out/`-Ordner als CSV-Datei gespeichert. Spieler werden in Spieler-\[Datum\].csv und
Mannschaften in Mannschaften-\[Datum\].csv gespeichert.
Ein Import an einem anderen PC ist somit (mit kleinen Anpassungen) möglich.

## Lizenz

[Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/)

