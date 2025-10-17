# Sprint 0: Projekt Software Engineering

**Anforderungen :**
+ Programmiersprache: Python
+ Blackbox Testing: Tests manuell durchführen
+ Source Code Management: Mit GitHub
+ Vorgehensmodell: Scrum
+ Funktionale Anforderungen: Unser System soll Nummernschilder erkennen als Sicherheitssystem. Einerseits wenn eine bekannte Nummer erkannt wird, muss eine Kombination von Handsignalen gegeben werden um das Tor zu öffnen. Andererseits wenn eine unbekannte Nummer vor dem Tor steht, wird erstmals eine Nachricht an das Telefon des Eigentümers geschickt. Dieser hat dann die Auswahl, 
+ Nicht-Funktionale Anforderungen: test
+ Technische Anforderungen:

+ Gesetzliche und Compliance Anforderungen:
Da unser System Bild- und eventuell Tonaufnahmen verarbeitet, fällt es unter das Datenschutzgesetz (DSG) beziehungsweise die Datenschutz-Grundverordnung (DSGVO). Das bedeutet, dass die Videoüberwachung nur zu einem klar definierten Zweck erfolgen darf, beispielsweise zur Überwachung von Räumen oder zum Schutz von Geräten. Öffentliche Bereiche oder private Grundstücke dürfen dabei nicht erfasst werden. Zudem muss der überwachte Bereich deutlich mit einem Hinweisschild gekennzeichnet werden, das auf die Videoüberwachung und den verantwortlichen Betreiber hinweist.
Auch die Speicherung der Videodaten ist gesetzlich geregelt. Die Aufnahmen dürfen nur so lange gespeichert werden, wie sie für den vorgesehenen Zweck notwendig sind, in der Regel maximal 72 Stunden. Danach müssen sie automatisch gelöscht oder überschrieben werden.
Ein weiterer wichtiger Punkt betrifft die IT-Sicherheit. Da unser System über WLAN funktioniert, muss die Datenübertragung verschlüsselt erfolgen, beispielsweise mit dem Sicherheitsstandard WPA3. Standardpasswörter der Kameras dürfen nicht verwendet werden, und nur autorisierte Personen sollen Zugriff auf die Daten und das System erhalten. Zusätzlich sollten regelmässige Software-Updates durchgeführt werden, um bekannte Sicherheitslücken zu schließen.
Schliesslich ist auch auf die technische und rechtliche Konformität der Hardware zu achten. Alle verwendeten Komponenten müssen eine gültige CE-Kennzeichnung besitzen, um zu bestätigen, dass sie den europäischen Sicherheitsanforderungen entsprechen.
