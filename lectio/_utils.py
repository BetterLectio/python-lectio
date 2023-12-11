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

#statusDictionary = {
#    "s2normal": "normal",
#    "s2cancelled": "aflyst",
#    "s2changed": "ændret",
#
#    "s2bgboxeksamen": "eksamen"
#}

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
    modulClass = modulDetaljer.get("class")
    if "s2normal" in modulClass:
        modulDetaljer["status"] = "normal"
    elif "s2cancelled" in modulClass:
        modulDetaljer["status"] = "aflyst"
    elif "s2changed" in modulClass:
        modulDetaljer["status"] = "ændret"
    elif "s2bgboxeksamen" in modulClass:
        modulDetaljer["status"] = "eksamen"

    modulDetaljer = modulDetaljer["data-tooltip"].split("\n\n")[0].split("\n")

    for modulDetalje in modulDetaljer:
        if (value := ": ".join(modulDetalje.split(": ")[1:])) != "":
            if (navn := modulDetalje.split(": ")[0]) in renameDictionary:
                navn = renameDictionary[navn]

            modulDict[navn.lower()] = value
        else:
            try:
                int(datetime.strptime(modulDetalje.split(" til ")[1], "%H:%M").timestamp())
                modulDict["tidspunkt"] = f"{modulDetalje.replace(' - ', ' til ')}"
            except Exception:
                modulDict["navn"] = modulDetalje

    try:
        modulDict["hold_id"] = re.search('data-lectiocontextcard="HE[0-9]+', str(skemabrik)).group().replace("data-lectiocontextcard=\"", "")
    except Exception:
        pass

    try:
        modulDict["andet"] = skemabrik["data-tooltip"].split("\n\n")[1]
    except Exception:
        pass

    return modulDict