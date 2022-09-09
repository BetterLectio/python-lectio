# Python-Lectio
En SDK til gymnasie siden Lectio  
Dataen bliver returneret som JSON

# Installation
```
pip install python-lectio
```

# Documentation
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
```
Returneret format:
```json
[
  {
    "navn": "...",
    "tidspunkt": "...",
    "hold": "...",
    "lærer": "...",
    "lokale": "...",
    "andet": "..."
    },
  ...
]
```
## Elever
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