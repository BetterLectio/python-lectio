from .imports import *

def generatePayload(soup, eventTarget):
    payload = {}
    for _input in soup.find("form", {"id": "aspnetForm"}).find_all("input", {"type": "hidden"}):
        id = _input.get("name")
        if id == None:
            id = _input.get("id")
        payload[id] = _input.get("value")
        if payload[id] == None:
            payload[id] = ""
    payload["__EVENTTARGET"] = eventTarget

    return payload



statusDictionary = {
    "s2brik": "normal",
    "s2cancelled": "aflyst",
    "s2changed": "ændret",

    "s2bgboxeksamen": "eksamen"
}

renameDictionary = {
    "Lærere": "Lærer",
    "Lokaler": "Lokale"
}

def skemaBrikExtract(dato, skemabrik):
    try:
        absid = re.search('absid=[0-9]+', skemabrik["href"]).group().replace("absid=", "")
    except Exception:
        absid = skemabrik.get("href")

    modulDict = {
        "navn": None,
        "tidspunkt": None,
        "hold": None,
        "hold_id": None,
        "lærer": None,
        "lokale": None,
        "status": "normal",
        "absid": absid,
        "andet": None
    }

    modulDetaljer = skemabrik
    statusClass = modulDetaljer.get("class")[2]
    if statusClass in statusDictionary:
        modulDict["status"] = statusDictionary[modulDetaljer.get("class")[2]]
    else:
        modulDict["status"] = modulDetaljer.get("class")[2]

    modulDetaljer = modulDetaljer["data-additionalinfo"].split("\n\n")[0].split("\n")

    for modulDetalje in modulDetaljer:
        if (value := ": ".join(modulDetalje.split(": ")[1:])) != "":
            if (navn := modulDetalje.split(": ")[0]) in renameDictionary:
                navn = renameDictionary[navn]

            modulDict[navn.lower()] = value
        else:
            try:
                int(datetime.strptime(modulDetalje.split(" - ")[0], "%H:%M").timestamp())
                modulDict["tidspunkt"] = f"{dato} {modulDetalje.replace(' - ', ' til ')}"
            except Exception:
                modulDict["navn"] = modulDetalje

    try:
        modulDict["hold_id"] = re.search('data-lectiocontextcard="HE[0-9]+', str(skemabrik)).group().replace("data-lectiocontextcard=\"", "")
    except Exception:
        pass

    try:
        modulDict["andet"] = skemabrik["data-additionalinfo"].split("\n\n")[1]
    except Exception:
        pass

    return modulDict