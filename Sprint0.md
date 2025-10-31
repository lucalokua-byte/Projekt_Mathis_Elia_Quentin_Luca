# Sprint 0: Projekt Software Engineering

**Einleitung**
Im Rahmen des Moduls Software Engineering entwickeln wir ein intelligentes Sicherheitssystem zur automatischen Erkennung von Fahrzeugkennzeichen und Steuerung eines Tores. Wird ein bekanntes Kennzeichen erkannt, öffnet sich das Tor nur nach dem richtigen Handsignal. Bei unbekannten Kennzeichen wird der Eigentümer über eine App benachrichtigt und kann den Zutritt erlauben oder verweigern.

Das Projekt wird in Python entwickelt, folgt dem Scrum-Modell und nutzt GitHub zur Versionsverwaltung. Ziel ist ein sicheres, zuverlässiges und benutzerfreundliches System, das durch moderne Bildverarbeitung und Sensorik den Zugang effizient und geschützt steuert.

**Anforderungen :**
+ Programmiersprache: Python
+ Blackbox Testing: Tests manuell durchführen
+ Source Code Management: Mit GitHub
+ Vorgehensmodell: Scrum
+ Funktionale Anforderungen: Unser System soll Nummernschilder erkennen als Sicherheitssystem. Einerseits wenn eine bekannte Nummer erkannt wird, muss eine Kombination von Handsignalen gegeben werden um das Tor zu öffnen. Andererseits wenn eine unbekannte Nummer vor dem Tor steht, wird erstmals eine Nachricht an das Telefon des Eigentümers geschickt. Dieser hat dann die Auswahl, 
+ Nicht-Funktionale Anforderungen: 

Performanz:
Das System muss Nummernschilder innerhalb von 10 Sekunden erkennen, bei einer maximalen Entfernung von 5 Metern zwischen Kamera und Fahrzeug. Die maximale Fehlerrate darf 20 % nicht überschreiten. Die Kamera muss auch bei Nacht oder schlechten Lichtverhältnissen zuverlässig arbeiten. Sie wird automatisch aktiviert, sobald eine Bewegung erkannt wird, um Energie zu sparen.
Usability:
Die Bedienung des Systems soll sehr einfach sein. Der Benutzer muss nur die Kamera mit seinem Smartphone verbinden, um Benachrichtigungen zu erhalten. Über eine intuitive App kann das Tor in wenigen Schritten gesteuert werden. Alle wichtigen Funktionen wie das Hinzufügen von Kennzeichen oder das Öffnen des Tors sind zu finden.
Sicherheit:
Das Tor öffnet sich nur, wenn sowohl ein bekanntes Kennzeichen erkannt als auch das richtige Handsignal gegeben wird. Im Fall eines Systemfehlers oder Stromausfalls bleibt das Tor aus Sicherheitsgründen geschlossen.
Datenschutz:
Erfasste Daten werden für Sicherheitszwecke genutzt und nach spätestens 14 Tagen automatisch gelöscht. Der Eigentümer kann die Daten zusätzlich jederzeit manuell löschen. 
Zuverlässigkeit:
Das System soll rund um die Uhr (24/7) funktionsfähig sein. Fehler oder Ausfälle werden automatisch erkannt und als Benachrichtigung an die App des Eigentümers gesendet, damit schnell reagiert werden kann.

+ Technische Anforderungen: Hardware
1.	Kamera: Ausreichende Qualität für die Kennzeichenerkennung (Hardware)
2.	Gestensensor: Zuverlässiges Gerät zur Erkennung der "Handzeichen". (Hardware)
3.	Zentraleinheit: Rechenleistung für schnelle Verarbeitung.(Hardware)
4.	Tor-Schnittstelle: Verbindung zum elektrischen Tor für die Steuerung. (Hardware)
6.	Datenbank: Gesicherte Liste der zugelassenen Kennzeichen. (Software)
7.	Gestenprüfung: Algorithmus zur Validierung der Geste. (Software)
8.	Alarm/Benachrichtigung: System zum schnellen Senden von Push-Nachrichten. (Software)
9.	Mobile App: Schnittstelle zum Empfangen des Alarms und zur Fernsteuerung. (Software)
10.	Protokollierung: Speicherung von Zugängen und Versuchen. (Software)



+ Funktionale Anforderungen: Unser System soll Nummernschilder als Teil eines Sicherheitssystems erkennen. Wird ein bekanntes Kennzeichen erkannt, ist zum Öffnen des Tores zusätzlich eine festgelegte Kombination von Handsignalen erforderlich. Steht ein unbekanntes Fahrzeug vor dem Tor, erhält der Eigentümer zunächst eine Nachricht auf sein Telefon mit den verfügbaren Fahrzeugdaten (Nummernschild, Name usw.). Der Eigentümer kann dann entscheiden, ob das Fahrzeug zugelassen werden soll. Dabei besteht die Möglichkeit, das Kennzeichen dauerhaft zu speichern oder den Zugang zu verweigern. Zusätzlich sollten die Ankunfts- und Abfahrtszeiten protokolliert werden.
+ Nicht-Funktionale Anforderungen:
+ Technische Anforderungen:
+ Gesetzliche und Compliance Anforderungen:

Da unser System Bild- und eventuell Tonaufnahmen verarbeitet, fällt es unter das Datenschutzgesetz (DSG) beziehungsweise die Datenschutz-Grundverordnung (DSGVO). Das bedeutet, dass die Videoüberwachung nur zu einem klar definierten Zweck erfolgen darf, beispielsweise zur Überwachung von Räumen oder zum Schutz von Geräten. Öffentliche Bereiche oder private Grundstücke dürfen dabei nicht erfasst werden. Zudem muss der überwachte Bereich deutlich mit einem Hinweisschild gekennzeichnet werden, das auf die Videoüberwachung und den verantwortlichen Betreiber hinweist.
Auch die Speicherung der Videodaten ist gesetzlich geregelt. Die Aufnahmen dürfen nur so lange gespeichert werden, wie sie für den vorgesehenen Zweck notwendig sind, in der Regel maximal 72 Stunden. Danach müssen sie automatisch gelöscht oder überschrieben werden.
Ein weiterer wichtiger Punkt betrifft die IT-Sicherheit. Da unser System über WLAN funktioniert, muss die Datenübertragung verschlüsselt erfolgen, beispielsweise mit dem Sicherheitsstandard WPA3. Standardpasswörter der Kameras dürfen nicht verwendet werden, und nur autorisierte Personen sollen Zugriff auf die Daten und das System erhalten. Zusätzlich sollten regelmässige Software-Updates durchgeführt werden, um bekannte Sicherheitslücken zu schließen.
Schliesslich ist auch auf die technische und rechtliche Konformität der Hardware zu achten. Alle verwendeten Komponenten müssen eine gültige CE-Kennzeichnung besitzen, um zu bestätigen, dass sie den europäischen Sicherheitsanforderungen entsprechen.


# Schätzen und Priorisieren der Anforderungen.

**Kritische Anforderungen (Must):**

Nummernschilderkennung (13) – Zentrale Hauptfunktion
Toröffnung mit Handsignal (8) – Sicherheitsschlüssel-Funktion
Mobile App-Steuerung (8) – Bedienoberfläche für Nutzer
Kamera (5 m Erkennung) (5) – Notwendige Hardware
Sicheres Torverhalten bei Fehler (5) – Sicherheitsanforderung
Fehlerrate < 20 % (5) – Qualitätsstandard
Reaktionszeit ≤ 10 s (3) – Leistungsanforderung
Kennzeichen-Datenbank (3) – Basis für Identifikation

**Wichtige, aber nachgelagerte Anforderungen (Should):**

24/7 Betrieb + Fehlerbenachrichtigung (8) – Zuverlässigkeit und Überwachung
Benachrichtigung bei unbekanntem Kennzeichen (5) – Sicherheits- und Komfortfunktion
Gestensensor (5) – Zusätzliche Sicherheitsstufe

**Optionale Verbesserungen (Could):**

Energieeffiziente Kameraaktivierung (2) – Optional zur Energieeinsparung

