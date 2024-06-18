from .imports import *
from . import _utils

def opgave(self, exerciseid):
    url = f"https://www.lectio.dk/lectio/{self.skoleId}/ElevAflevering.aspx?elevid={self.elevId}&exerciseid={exerciseid}"
    resp = self.session.get(url)
    if resp.url != url:
        raise Exception("lectio-cookie udløbet")
    soup = BeautifulSoup(resp.text, "html.parser")

    opgaveDict = {
        "oplysninger": {
            "opgavetitel": None,
            "opgavebeskrivelse": None,
            "opgavenote": None,
            "hold": None,
            "karakterskala": None,
            "ansvarlig": None,
            "elevtid": None,
            "afleveringsfrist": None,
            "i_undervisningsbeskrivelse": None
        },
        "gruppemedlemmer": [],
        "afleveres_af": {},
        "opgave_indlæg": []
    }
    for tr in soup.find("table", {"class": "ls-std-table-inputlist"}).find_all("tr"):
        if (identifier := unicodedata.normalize("NFKD", tr.find("th").text).lower().replace(" ", "_").replace(":", "")) == "ansvarlig":
            opgaveDict["oplysninger"][identifier] = {"navn": unicodedata.normalize("NFKD", tr.find("td").text), "bruger_id": tr.find("span").get("data-lectiocontextcard")}
        elif identifier == "opgavebeskrivelse":
            opgaveBeskrivelse = ""
            for a in tr.find_all("a"):
                opgaveBeskrivelse += f'[{unicodedata.normalize("NFKD", a.text).lstrip().rstrip()}](https://www.lectio.dk{a.get("href")})\n  '
            opgaveDict["oplysninger"][identifier] = opgaveBeskrivelse[:-1]
        else:
            opgaveDict["oplysninger"][identifier] = unicodedata.normalize("NFKD", tr.find("td").text)

    if soup.find_all("span", {"class": "islandHeader"})[1].text == "Gruppeaflevering":
        for tr in soup.find("table", {"class": "ls-table-layout1 lf-grid"}).find_all("tr")[1:]:
            opgaveDict["gruppemedlemmer"].append({"navn": unicodedata.normalize("NFKD", tr.text.lstrip().rstrip()), "bruger_id": tr.find("span").get("data-lectiocontextcard")})

    header = soup.find("table", {"class": "ls-table-layout1 maxW textTop lf-grid"}).find_all("tr", {"class": ""})[0]
    headerIdentifiers = []
    for th in header.find_all("th")[1:]:
        headerIdentifiers.append(th.text.lower().replace(" ", "_"))

    for tr in soup.find("table", {"class": "ls-table-layout1 maxW textTop lf-grid"}).find_all("tr")[1:]:
        i = 0
        for td in tr.find_all("td")[1:]:
            if (identifier := headerIdentifiers[i]) == "afsluttet":
                opgaveDict["afleveres_af"][identifier] = td.find("input").get("checked") == "checked"
            elif identifier == "elev":
                opgaveDict["afleveres_af"][identifier] = {"navn": unicodedata.normalize("NFKD", td.text).lstrip().rstrip(), "bruger_id": td.find_all("span")[1].get("data-lectiocontextcard")}
            elif identifier == "status_-_frav\u00e6r":
                opgaveDict["afleveres_af"]["status_frav\u00e6r"] = unicodedata.normalize("NFKD", td.text).lstrip().rstrip()
            
            else:
                opgaveDict["afleveres_af"][identifier] = unicodedata.normalize("NFKD", td.text).lstrip().rstrip()
            i += 1

    indlægHtml = soup.find("table", {"id": "m_Content_RecipientGV"})
    indlægHeader = [header.text.lower().replace(" ", "_") for header in indlægHtml.find_all("th")]

    for tr in indlægHtml.find_all("tr")[1:]:
        indlæg = {}
        i = 0
        for td in tr.find_all("td"):
            if (identifier := indlægHeader[i]) == "dokument" and td.find("a") != None:
                indlæg[identifier] = f"[{td.text.lstrip().rstrip()}](https://www.lectio.dk{td.find('a').get('href')})"
            elif identifier == "bruger":
                indlæg[identifier] = {"navn": td.text.lstrip().rstrip(), "bruger_id": td.find("span").get("data-lectiocontextcard")}
            else:
                indlæg[identifier] = td.text.lstrip().rstrip()
            i += 1

        opgaveDict["opgave_indlæg"].append(indlæg)

    return opgaveDict
def opgaver(self):
    url = f"https://www.lectio.dk/lectio/{self.skoleId}/OpgaverElev.aspx?elevid={self.elevId}"
    resp = self.session.get(url)
    if resp.url != url:
        raise Exception("lectio-cookie udløbet")
    soup = BeautifulSoup(resp.text, "html.parser")

    if str(soup.find("input", {"id": "s_m_Content_Content_CurrentExerciseFilterCB"}).get("checked")) == "checked":
        resp = self.session.post(f"https://www.lectio.dk/lectio/{self.skoleId}/OpgaverElev.aspx?elevid={self.elevId}", data=_utils.generatePayload(soup, "s$m$Content$Content$CurrentExerciseFilterCB"))
        soup = BeautifulSoup(resp.text, "html.parser")

    opgaver = []
    header = []

    _header = soup.find("tr")
    for th in _header.find_all("th"):
        header.append(th.text.lower().replace("\xad", "-"))

    for opgave in soup.find_all("tr")[1:]:
        opgaveDict = {}

        i = 0
        for td in opgave.find_all("td"):
            if header[i] == "opgavetitel":
                opgaveDict["exerciseid"] = re.findall("exerciseid=\d+", td.find("a", href=True).get("href"))[0].replace(
                    "exerciseid=", "")

            opgaveDict[header[i]] = td.text.lstrip()
            i += 1

        if opgaveDict["afventer"] == "":
            opgaveDict["status"] = "Afsluttet"
        opgaveDict["status"] = opgaveDict["status"].split("\r\n\t\t\t\t\t\t\t")[0].strip()
        opgaver.append(opgaveDict)

    return opgaver

def afleverOpgave(self, exerciseid, fileName, fileContentType, fileContent, note):
    opgaveUrl = f"https://www.lectio.dk/lectio/{self.skoleId}/ElevAflevering.aspx?elevid={self.elevId}&exerciseid={exerciseid}&prevurl=OpgaverElev.aspx"
    resp = self.session.get(opgaveUrl)
    if resp.url != opgaveUrl:
        raise Exception("lectio-cookie udløbet")
    soup = BeautifulSoup(resp.text, "html.parser")
    opgavePayload = _utils.generatePayload(soup, "m$Content$choosedocument")

    url = f"https://www.lectio.dk/lectio/{self.skoleId}/documentchoosercontent.aspx?year=2023&ispublic=0&showcheckbox=0&mode=pickfile" # Lectio bruger stadig 2023
    resp = self.session.get(url)
    if resp.url != url:
        raise Exception("lectio-cookie udløbet")
    soup = BeautifulSoup(resp.text, "html.parser")

    payload = _utils.generatePayload(soup, "ctl00$Content$newfileOK")
    payload["__LASTFOCUS"] = ""
    payload["__EVENTARGUMENT"] = ""
    payload["LectioPostbackId"] = ""

    webKitFormBoundary = b""
    for key, value in payload.items():
        webKitFormBoundary += f'------WebKitFormBoundarybOZ0WE0mGm0SOd1b\nContent-Disposition: form-data; name="{key}"\n\n{value}\n'.encode()
    webKitFormBoundary += f'------WebKitFormBoundarybOZ0WE0mGm0SOd1b\nContent-Disposition: form-data; name="ctl00$Content$fileUpload_up"; filename="{fileName}"\nContent-Type: {fileContentType}\n\n'.encode()
    webKitFormBoundary += fileContent
    webKitFormBoundary += b"\n------WebKitFormBoundarybOZ0WE0mGm0SOd1b--"

    resp = self.session.post(url, data=webKitFormBoundary, headers={
        "content-type": "multipart/form-data; boundary=----WebKitFormBoundarybOZ0WE0mGm0SOd1b"
    })
    if resp.url != url:
        raise Exception("lectio-cookie udløbet")

    serializedId = re.search('"serializedId":"\w+"', resp.text).group()[16:-1]

    opgavePayload["__EVENTARGUMENT"] = "documentId"
    opgavePayload["__LASTFOCUS"] = ""
    opgavePayload["m$searchinputfield"] = ""
    opgavePayload["m$Content$CommentsTB$tb"] = note
    opgavePayload["m$Content$choosedocument$selectedDocumentId"] = '{"type":"serializedAnyFileId","serializedId":"' + serializedId + '","isPublic":true,"filename":"' + fileName + '"}'
    opgavePayload["masterfootervalue"] = "X1!ÆØÅ"
    opgavePayload["LectioPostbackId"] = ""

    resp = self.session.post(opgaveUrl, data=formEncode(opgavePayload), headers={
        "content-type": "application/x-www-form-urlencoded"
    })

    try:
        lectioAlert = re.search("LectioAlertBox\.RegisterAlerts.*?',", resp.text).group()[31:-2].replace("\\u003C", "<").replace("\\n", "\n")
        return {"success": False, "error": BeautifulSoup(lectioAlert, "html.parser").text.strip()}
    except AttributeError:
        return {"success": True}