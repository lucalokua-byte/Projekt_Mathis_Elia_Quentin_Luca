# Readme: Projekt Software Engineering

**Einleitung**
Im Rahmen des Moduls Software Engineering entwickeln wir ein intelligentes Sicherheitssystem zur automatischen Erkennung von Fahrzeugen, Fahrzeugkennzeichen und Steuerung eines Tores. Wird ein bekanntes Kennzeichen erkannt, öffnet sich das Tor. Bei unbekannten Kennzeichen wird der Eigentümer über eine e-mail benachrichtigt und kann den Zutritt erlauben oder verweigern ; indem er das Fahrzeug zur Whitelist oder Blacklist hinzufügt.

Das Projekt wird in Python entwickelt, folgt dem Scrum-Modell und nutzt GitHub zur Versionsverwaltung. Ziel ist ein sicheres, zuverlässiges und benutzerfreundliches System, das durch moderne Bildverarbeitung und Sensorik den Zugang effizient und geschützt steuert.

**Build-Anleitung**
Es muss python Version 3.12 benutzt werden, für die beste Kompatibilität mit Mediapipe. Die benötigten libraries sind die folgenden die mann mit pip install im vs code installieren kann:
- opencv-python
- pytesseract
- numpy
- imutils
- pillow
- requests
- mediapipe
- secure-smtplib email-validator
Für pytesseract muss auf https://github.com/UB-Mannheim/tesseract/wiki Tesseract installiert werden, bevor man den pip install pytesseract macht. Die Installation sollte im folgenden Dateipfad sein: C:\Program Files\Tesseract-OCR\tesseract.exe

Zur Funktion des Codes den main.py File ausführen. Dann wird die Kamera vom Device eingeschalten, um in einem Bild ein Auto zu erkennen. Wenn ein Auto mindestens eine Sekunde vor der Kamera steht, dann schließt sich diese. Dann öffnet sich die nächste Seite, um das Nummernschild zu erkennen. Sobald das Nummernschild bestätigt ist, kommt dieses in einer Email an projetseqlem@gmail.com geschickt, (https://github.com/lucalokua-byte/Projekt_Mathis_Elia_Quentin_Luca/blob/main/Coding/mail_system/email_system.py#L138 dieser Link bringt sie zur Linie im Code wo ihre email eingegeben werden kann).
In der Email kann dann der Benutzer auf einen von 4 Optionen einen "Button"(es sind links) innerhalb von 120s drücken um lokal die Antwort zu speichern und den code weiterlaufen lassen. Die 4 Optionen sind: Tor öffnen und Nummernschild zur Whitelist adden; Nur das Tor öffnen; Tor zulassen und Nummernschild zur Blacklist adden; Nur das Tor zulassen. Diese Auswahl wird dann in der Datenbank gespeichert.



**Use Case  Diagramm**
![Use Case Diagram](https://www.plantuml.com/plantuml/png/TPFVRjem5CRl_HH7z69mmIDiQWWPYnPYbAHbrLHDNd9AhHfdijqXDEtT5tDaisakL-ZyllF7tmUtrWdZNe-AANnou4Omyl3iO906UoT7pTWxUEy_q3wqNR655Vz21UOLGXyKmgoIFMgBi5F28MHzZzP2UxOEZpFunHW0m7oDRkg0N9W520jt-JUg46rH3r0iZqAgWElHoQSpuGR50F-i2IfFIBD_bWwLj2ujZ3YSeyz0fmQ5Bn5SAT6_l3qgObBp7wXXynVt1VRxwbsMTxnfOLzsdo3dbV_-duSxCnwCECASV5lC_AnGlAbyB2lrYapqRZGmuoUD1kPt5Wr9gK32ZK7KGNalhNIZr-eNFPuqh8ty6Re8Xhu7L6eyNU_UDNpJP5keolfp2tE_Vq68XSkMNs--J-N7vJNGDACqaumoZ5lvlYwQiFFobB2KtZYr7doLUcEi2KgH9a6CC4Kfm7ZGVTcM7OydSJD55eq83au3nWkuJaYpO5E29ineYteDnJOhAwXvLtuiywmhUKsKHL_z48F3u_83_H0OkqKz-3_s7m00)


**Class diagram**
[![Class diagram](https://img.plantuml.biz/plantuml/png/XLJBRjj03BppAmWOI4_91_GGHBQBD83T1bRHe4TwnKYRh7ODxYg1-_ZthYL7aYtPradW3CaXHzIT3oIXAWrymjaYILESFoJtgsJv6NzoePLXd7DW5RIpU8Kfgqfqs6AwzO5B0F-gxOQ4IbI6lCS_WF6PadhDnLKscpdZ19yA7RX64X7ttWId9h8QkfECfH_z1r5FuhtEBQfTtEE61RNDz9lEAZB8XaksmKFJjoHjSRBGUH6cfc80RGFBCod6PEs3a0hpwP8ivR7CvAbW2ZtAVjHsqcQwXnOV97ohoZNBew70ArOkj_ftLtSlQSvA-rZiAzdCxD0VXVR1y1wUaRJzaircB_vUc2ssb9A5niNr-GVq4U3x-YMcDWNYYeU4jlQZECNUZvA6CzSVnMGPfzgkdFyOx4lqmgHiiztC2tghtpuQTHxyOcFSEq3jtFNrxV52-i3fDNIiNjikEAuPu7Zv5zkSjQBBlimxzE8oVsWDm0adZhTmXjRw07st3X7epBgv-NixlAFpukkS2uTrIcATEtfZGxs7LmPm5x7T_mp-0m00)](https://editor.plantuml.com/uml/XLJBRjj03BppAmWOI4_91_GGHBQBD83T1bRHe4TwnKYRh7ODxYg1-_ZthYL7aYtPradW3CaXHzIT3oIXAWrymjaYILESFoJtgsJv6NzoePLXd7DW5RIpU8Kfgqfqs6AwzO5B0F-gxOQ4IbI6lCS_WF6PadhDnLKscpdZ19yA7RX64X7ttWId9h8QkfECfH_z1r5FuhtEBQfTtEE61RNDz9lEAZB8XaksmKFJjoHjSRBGUH6cfc80RGFBCod6PEs3a0hpwP8ivR7CvAbW2ZtAVjHsqcQwXnOV97ohoZNBew70ArOkj_ftLtSlQSvA-rZiAzdCxD0VXVR1y1wUaRJzaircB_vUc2ssb9A5niNr-GVq4U3x-YMcDWNYYeU4jlQZECNUZvA6CzSVnMGPfzgkdFyOx4lqmgHiiztC2tghtpuQTHxyOcFSEq3jtFNrxV52-i3fDNIiNjikEAuPu7Zv5zkSjQBBlimxzE8oVsWDm0adZhTmXjRw07st3X7epBgv-NixlAFpukkS2uTrIcATEtfZGxs7LmPm5x7T_mp-0m00)

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

    Da unser System Bild- und Tonaufnahmen verarbeitet, unterliegt es dem DSG/der DSGVO. Videoüberwachung ist nur zu einem klar definierten Zweck erlaubt und darf keine öffentlichen Bereiche oder fremde Privatgrundstücke erfassen. Der überwachte Bereich muss klar mit einem Hinweis auf Kameraüberwachung und den Verantwortlichen gekennzeichnet sein.


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



[def]: [https://editor.plantuml.com/uml/ZLJBReCm4BnRyZ_igJqb7v1351ggDbBJHa7gtJZRr94naMqEwUFVowE0mK1otPtP7S-mh8nbscQ9fEGUrYz1546u2PxsmNO1x_Wfk4G8qIAt8bLm1n7oJ0jxWUXYB2QKSCcCWOG91PG8PL5_C8uGnCPgnctui6MA7L6xpV_1pTngrgRkkz3NB8bHxoIpk4UU7fNuAcPLMqFamkJyPwOEiYslcMv61-SpV5EIQ_kbf0KagDcmYW8z08QYK9VUubDEgOYfzXZDn9rEEHfJGQ2hmNzOwR2dzJ6tLaQe3ZYmg3QtwPGvp6RBlWUTplZZ7PYprwaEgwQaR_drHPCPjFGRWDqqRY3u-L0o4eVdn0JE-TJTq7gjDhFv_6SvT2UJ-alIrViPKLcIHoxAazo_BKfMURVyK_m1]