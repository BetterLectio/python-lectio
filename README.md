# Python-Lectio
En SDK til gymnasie siden Lectio  
Dataen bliver returneret som JSON

# Installation
```
pip install python-lectio
```

# Dokumentation
Denne dokumentation er til den [gamle python-lectio](https://github.com/jona799t/python-lectio/tree/old) branch og vil måske ikke returnere/fungere som den gjorde før.  
Hvis du vil bruge den [gamle python-lectio](https://github.com/jona799t/python-lectio/tree/old) kan du finde den [her](https://github.com/jona799t/python-lectio/tree/old).  
  
En dokumentation til den [nye python-lectio](https://github.com/jona799t/python-lectio/tree/main) er på vej.
## Login
Login på Lectio igennem python
```python
import lectio

client = lectio.sdk(brugernavn="mit brugernavn", adgangskode="min adgangskode", skoleId="mit skole id")
```
## Elev ID
```python
import lectio

elevId = client.elevId
```

## Skema
Se dit skema for en hvilken som helst uge. Hvis du ikke skriver uge/år på tager den for ugen næste skoledag
```python
skema = client.skema()
skemaSpecifikUge = client.skema(uge=35, år=2022)
lektierForSpecifikElev = client.lektier(elevId="...")
```
Returneret format:
```json
{
    "modulTider": {"1. modul": "8:15 - 9:15", "2. modul": "9:20 - 10:20"...},
    "ugeDage": ["Mandag (31/10)", "Tirsdag (1/11)", "Onsdag (2/11)"...],
    "moduler": [
        {
            "navn": "...",
            "tidspunkt": "...",
            "hold": "...",
            "lærer": "...",
            "lokale": "...",
            "absid": "...",
            "andet": "..."
        },
        ...
    ],
}

```

## Lektier
Få dine lektier for de kommende 14 dage
```python
lektier = client.lektier()
lektierForSpecifikElev = client.lektier(elevId="...")
```
Returneret format:
```json
[
    {
        "dato": "...",
        "aktivitet": {
            "navn": "...",
            "tidspunkt": "...",
            "hold": "...",
            "lærer": "...",
            "lokale": "...",
            "absid": "..."
        },
        "note": "...",
        "lektier": {
            "beskrivelse": "...",
            "link": "..."
        }
    },
    ...
]
```

## ~~Elever~~ Brug informationer() i stedet
Få alle elever på skolen med et bestemt forbogstav.
```python
elever = client.elever(forbogstav="A")
```
Returneret format:
```json
[
    {
        "navn": "...",
        "elevid": "..."
    },
    ...
]
```


# To Do
   * Tilføj flere funktioner
   * Login med auto login key