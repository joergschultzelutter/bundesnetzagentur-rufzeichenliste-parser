# bundesnetzagentur-rufzeichenliste-parser

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![CodeQL](https://github.com/joergschultzelutter/bundesnetzagentur-rufzeichenliste-parser/actions/workflows/codeql.yml/badge.svg)](https://github.com/joergschultzelutter/bundesnetzagentur-rufzeichenliste-parser/actions/workflows/codeql.yml)

(As this program mainly targets a German audience, this Readme is in German, too. However, the program uses English comments 🙂 You can use it for extracting ham radio call signs from the latest German Bundesnetzagentur publication and converting the data to a CSV machine readable format)

Quick-Hack zum Herunterladen der jeweils aktuellen Rufzeichenliste der Bundesnetzagentur. Anschließend werden alle vorhandenen Rufzeichen extrahiert und auf stdout in einem csv-Format zur weiteren maschinellen Verarbeitung ausgegeben. 

Das Programm besitzt keinerlei Ein- und Ausgabeparameter. Nach dem Start kann es 20-30 Sekunden dauern, bis die relativ große pdf-Datei der Bundesnetzagentur initial analysiert worden ist. Da die komplette Ausgabe gegen stdout erfolgt, werden während dieser Zeit keine Informationen auf dem Bildschirm ausgegeben. Es erfolgt keine Filterung nach Kategorien; d.h. alle Rufzeichen (z.B. auch Klubstationen, Ausbildungsrufzeichen usw.) sind im Export enthalten.

## Installation

Benötigte pip-pakete:

- [pdfminer.six](https://github.com/pdfminer/pdfminer.six)
- [requests](https://github.com/psf/requests)

Installation aller Pakete via

    pip install -r requirements.txt

## Aufruf

Programm einfach ohne Parameter aufrufen. Die Rufzeichenliste wird heruntergeladen, analysiert und anschließend zeilenweise auf dem Bildschirm ausgegeben. Die Datenstruktur ist identisch mit der in der pdf-Datei verwendeten Datenstruktur - d.h. Callsign, Klasse (A/E/N) und -sofern vorhanden- Name und Anschrift(en)

## Bekannte Einschränkungen

- Die PDF-Quelldatei besteht aus insgesamt drei Spalten. Ist eine Seite der pdf-Datei nicht vollständig gefüllt (z.B. weil auf der Folgeseite eine neue Dokument-Kategorie beginnt), so wird im Extrakt die Reihenfolge der Einträge möglicherweise nicht korrekt in das CSV-Dateiformat überführt. Da die erzeugte CSV-Datei aber eh maschinell weiterverarbeitet werden wird, sollte dieser Punkt irrelevant sein.
