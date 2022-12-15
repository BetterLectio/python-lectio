def generatePayload(soup, eventTarget):
    payload = {}
    for _input in soup.find("form", {"id": "aspnetForm"}).find_all("input", {"type": "hidden"}):
        id = _input.get("id")
        if id == None:
            id = _input.get("name")
        payload[id] = _input.get("value")
    payload["__EVENTTARGET"] = eventTarget

    return payload