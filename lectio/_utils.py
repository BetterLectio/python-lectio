from .imports import *

def generatePayload(soup, eventTarget):
    payload = {}
    for _input in soup.find("form", {"id": "aspnetForm"}).find_all("input", {"type": "hidden"}):
        id = _input.get("id")
        if id == None:
            id = _input.get("name")
        payload[id] = _input.get("value")
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

def skemaBrikExtract(skemabrik):
    try:
        absid = re.search('absid=[0-9]+', skemabrik["href"]).group().replace("absid=", "")
    except Exception:
        absid = skemabrik.get("href")

    modulDict = {
        "navn": None,
        "tidspunkt": None,
        "hold": None,
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
                int(datetime.strptime(modulDetalje.split(": ")[0].split(" til")[0],
                                      "%d/%m-%Y %H:%M").timestamp())
                modulDict["tidspunkt"] = modulDetalje
            except Exception:
                modulDict["navn"] = modulDetalje.split(": ")[0]

    try:
        modulDict["andet"] = skemabrik["data-additionalinfo"].split("\n\n")[1]
    except Exception:
        pass

    return modulDict