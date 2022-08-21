# Python-Lectio
En SDK til gymnasie siden Lectio

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
## Skema
Se dit skema for en hvilken som helst uge. Hvis du ikke skriver uge/år på tager den for ugen næste skoledag
```python
skemaUgeNæsteSkoledag = client.skema()
skemaUgePåSpecifikUge = client.skema(uge=35, år=2022)
```

# To Do
   * Tilføj flere funktioner
   * Måske gøre så hvad der bliver returneret er i json format i stedet for html