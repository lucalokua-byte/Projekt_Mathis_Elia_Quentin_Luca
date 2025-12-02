# Readme: Projekt Software Engineering

**Einleitung**
Im Rahmen des Moduls Software Engineering entwickeln wir ein intelligentes Sicherheitssystem zur automatischen Erkennung von Fahrzeugen, Fahrzeugkennzeichen und Steuerung eines Tores. Wird ein bekanntes Kennzeichen erkannt, öffnet sich das Tor. Bei unbekannten Kennzeichen wird der Eigentümer über eine e-mail benachrichtigt und kann den Zutritt erlauben oder verweigern ; indem er das Fahrzeug zur Whitelist oder Blacklist hinzufügt.

Das Projekt wird in Python entwickelt, folgt dem Scrum-Modell und nutzt GitHub zur Versionsverwaltung. Ziel ist ein sicheres, zuverlässiges und benutzerfreundliches System, das durch moderne Bildverarbeitung und Sensorik den Zugang effizient und geschützt steuert.

**Build-Anleitung**
Es muss python Version 3.11 benutzt werden, für die beste Kompatibilität mit Mediapipe. Die benötigten libraries sind die folgenden die mann mit pip install im vs code installieren kann:
- opencv-python
- pytesseract
- numpy
- imutils
- pillow
- requests
- mediapipe
- secure-smtplib email-validator
Für pytesseract muss auf https://github.com/UB-Mannheim/tesseract/wiki Tesseract installiert werden, bevor man den pip install pytesseract macht. Die Installation sollte im folgenden Dateipfad sein: C:\Program Files\Tesseract-OCR\tesseract.exe

Zur Funktion des Codes den main.py File ausführen. Dann wird die Kamera vom Device eingeschalten, um in einem Bild ein Auto zu erkennen. Wenn ein Auto mindestens eine Sekunde vor der Kamera steht, dann schließt sich diese. Dann öffnet sich die nächste Seite, um das Nummernschild zu erkennen. Sobald das Nummernschild bestätigt ist, kommt dieses in einer Email an projetseqlem@gmail.com geschickt, in der Email kann dann der Benutzer auf einen von 4 Optionen einen "Button"(es sind links) drücken um lokal die Antwort zu speichern und den code weiterlaufen lassen. Die 4 Optionen sind: Tor öffnen und Nummernschild zur Whitelist adden; Nur das Tor öffnen; Tor zulassen und Nummernschild zur Blacklist adden; Nur das Tor zulassen. Diese Auswahl wird dann in der Datenbank gespeichert.

**Anmeldung zur E-Mail-Adresse**
Konto : projetseqlem@gmail.com
Kennword : kelvintrinat25
NummerTelefonnummer : 06 98 74 28 87  -> Mathis Schmitt muss dann validieren

**Use Case  Diagramm**
![Use Case Diagram](https://www.plantuml.com/plantuml/png/RP7DQiCm48JlUeh19-VWDoWXRGszb2Oqf3qBUUCiaQKYRHj2wRlNYkoG7uCEoywdtHbf4KK7-UwiihGLY4VWTYTeE90HzaufRSG75AlWsw0xbEjZ5Efc1NJ4q1oPvS5HGBc95B9-Qepg1qTEHRbnU-SF3dNWdv7CjL9fhNQj9HIlRCX5mifg8JmQGp4YRo_mgu3-ZAwgQewo9kblurc7sQtqJhh1rS0xP4skmPiNthBHANeYSgA7gfhKpy1fmFAB75w6qHVzcjnni7-ZVEvOo7AKUsiNr9FLPZz5zLX-DYH_L-lF_Vbaz3-rwDEaR_y7)


**Funktions-Diagramm**

```mermaid
flowchart TD
  %% ==== Styles ====
  classDef actor fill:#ffffff,stroke:#333,stroke-dasharray:5 5;
  classDef usecase fill:#eef5ff,stroke:#333;

  %% ==== Actors (outside boundary) ====
  Owner["Owner"]:::actor
  Known["Visitor (Known Plate)"]:::actor
  Unknown["Visitor (Unknown Plate)"]:::actor
  PushSvc["Push Notification Service"]:::actor
  Programm["Programm/Code"]:::actor

  %% ==== System boundary ====
  subgraph System["License Plate Access Control System"]
    M([Detect Motion]):::usecase
    C([Activate Camera]):::usecase
    L([Recognize License Plate]):::usecase
    W([Check Whitelist]):::usecase
    O([Open Gate]):::usecase
    D([Deny Access]):::usecase
    N([Send Notification]):::usecase
    APP([Decision via App]):::usecase
    WL([Manage Whitelist]):::usecase
    BL([Manage BlackList]):::usecase
    LOG([Log Access Attempts]):::usecase
    FD([Detect System Fault]):::usecase
    FN([Send Fault Notification]):::usecase
  end

  %% ==== Actor triggers ====
  Programm --> Unknown
  Programm --> Known
  Known --> M
  Unknown --> M

  %% ==== Core flow ====
  M --> C --> L --> W
  

  %% Logging (always executed with core use cases) ≈ <<include>>
  L --> LOG
  O --> LOG
  D --> LOG

  %% ==== Branching (labels explain conditions) ====
 

  L -- "unknown plate" --> N

  %% ==== Notifications & decisions ====
  N --> Owner
  N --> PushSvc
  Owner --> APP
  APP --> O
  APP --> D

  %% ==== Management ====
  Owner --> WL
  Owner --> BL

  %% ==== Fault handling (fail-safe: gate stays closed) ====
  FD --> FN --> Owner

 

  ```

**Ziele**
- Ein sicheres Zugangssystem mit Kennzeichenerkennung erstellen.

- Das Tor öffnet sich nur bei korrekter Kennzeichen.

- Besitzer verwalten das System über eine E-mail.

- Das System muss ein Kennzeichen erkennen.

- Die maximale Fehlerrate für die Erkennung darf 30 % nicht überschreiten.

- Drahtlose Kommunikation muss verschlüsselt werden (WPA3).

- Gespeicherte Daten werden spätestens nach 14 Tagen gelöscht.


**Anforderungen :**
+ Programmiersprache: Python
+ Blackbox Testing: Tests manuell durchführen
+ Source Code Management: Mit GitHub
+ Vorgehensmodell: Scrum
+ **Funktionale Anforderungen:** unser System soll Nummernschilder erkennen als Sicherheitssystem. Einerseits wenn eine bekannte Nummer erkannt wird, soll sich das Tor öffnen. Andererseits wenn eine unbekannte Nummer vor dem Tor steht, wird erstmals eine Nachricht an das Mail des Eigentümers geschickt. Dieser hat dann die Auswahl, 4 Optionen einen "Button"(es sind links) drücken um lokal die Antwort zu speichern und den code weiterlaufen lassen. Die 4 Optionen sind: Tor öffnen und Nummernschild zur Whitelist adden; Nur das Tor öffnen; Tor zulassen und Nummernschild zur Blacklist adden; Nur das Tor zulassen. Diese Auswahl wird dann in der Datenbank gespeichert.
+ **Nicht-Funktionale Anforderungen:** 

    **Performanz:**
    Das System muss Nummernschilder innerhalb von 10 Sekunden erkennen, bei einer maximalen Entfernung von 5 Metern zwischen Kamera und Fahrzeug. Die maximale Fehlerrate darf 20 % nicht überschreiten. Die Kamera muss auch bei Nacht oder schlechten Lichtverhältnissen zuverlässig arbeiten. Sie wird automatisch aktiviert, sobald eine Bewegung erkannt wird, um Energie zu sparen.
    **Usability:**
    Die Bedienung des Systems soll sehr einfach sein. Der Benutzer muss nur die Kamera mit seinem Smartphone verbinden, um Benachrichtigungen zu erhalten. Über eine intuitive App kann das Tor in wenigen Schritten gesteuert werden. Alle wichtigen Funktionen wie das Hinzufügen von Kennzeichen oder das Öffnen des Tors sind zu finden.
    **Sicherheit:**
    Das Tor öffnet sich nur, wenn sowohl ein bekanntes Kennzeichen erkannt als auch das richtige Handsignal gegeben wird. Im Fall eines Systemfehlers oder Stromausfalls bleibt das Tor aus Sicherheitsgründen geschlossen.
    **Datenschutz:**
    Erfasste Daten werden für Sicherheitszwecke genutzt und nach spätestens 14 Tagen automatisch gelöscht. Der Eigentümer kann die Daten zusätzlich jederzeit manuell löschen. 
    **Zuverlässigkeit:**
    Das System soll rund um die Uhr (24/7) funktionsfähig sein. Fehler oder Ausfälle werden automatisch erkannt und als Benachrichtigung an die App des Eigentümers gesendet, damit schnell reagiert werden kann.

+ **Technische Anforderungen:** 
    **Hardware:**
    Kamera: Ausreichende Qualität für die Kennzeichenerkennung (Hardware)
    Gestensensor: Zuverlässiges Gerät zur Erkennung der "Handzeichen". (Hardware)
    Zentraleinheit: Rechenleistung für schnelle Verarbeitung.(Hardware)
    Tor-Schnittstelle: Verbindung zum elektrischen Tor für die Steuerung. (Hardware)
    Datenbank: Gesicherte Liste der zugelassenen Kennzeichen. (Software)
    Gestenprüfung: Algorithmus zur Validierung der Geste. (Software)
    Alarm/Benachrichtigung: System zum schnellen Senden von Push-Nachrichten. (Software)
    Mobile App: Schnittstelle zum Empfangen des Alarms und zur Fernsteuerung. (Software)
    Protokollierung: Speicherung von Zugängen und Versuchen. (Software)



+ **Funktionale Anforderungen:** Unser System soll Nummernschilder als Teil eines Sicherheitssystems erkennen. Wird ein bekanntes Kennzeichen erkannt, ist zum Öffnen des Tores zusätzlich eine festgelegte Kombination von Handsignalen erforderlich. Steht ein unbekanntes Fahrzeug vor dem Tor, erhält der Eigentümer zunächst eine Nachricht auf sein Telefon mit den verfügbaren Fahrzeugdaten (Nummernschild, Name usw.). Der Eigentümer kann dann entscheiden, ob das Fahrzeug zugelassen werden soll. Dabei besteht die Möglichkeit, das Kennzeichen dauerhaft zu speichern oder den Zugang zu verweigern. Zusätzlich sollten die Ankunfts- und Abfahrtszeiten protokolliert werden.

+ **Gesetzliche und Compliance Anforderungen:**

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

