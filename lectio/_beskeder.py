from .imports import *
from . import _utils

def beskeder(self, id=None):
    if id != None:
        if "-" in str(id):
            url = f"https://www.lectio.dk/lectio/{self.skoleId}/beskeder2.aspx?type=&elevid={self.elevId}&selectedfolderid={id}"
        else:
            url = f"https://www.lectio.dk/lectio/{self.skoleId}/beskeder2.aspx?type=selecthold&elevid={self.elevId}&holdid={id}"
    else:
        url = f"https://www.lectio.dk/lectio/{self.skoleId}/beskeder2.aspx?type=liste&elevid={self.elevId}"

    resp = self.session.get(url)
    if resp.url != url:
        raise Exception("lectio-cookie udløbet")
    soup = BeautifulSoup(resp.text, "html.parser")

    beskederHtml = soup.find_all("tr")

    if (sideInddeling := soup.find("tr", {"class": "paging heavy"})) != None:
        payload = {}
        for _input in soup.find("form", {"id": "aspnetForm"}).find_all("input", {"type": "hidden"}):
            id = _input.get("id")
            if id == None:
                id = _input.get("name")
            payload[id] = _input.get("value")
        payload["__EVENTTARGET"] = sideInddeling.find_all("td")[-1].find("a").get("href").split("\"")[1].split("\"")[0]

        resp = self.session.post(url, data=payload)
        soup = BeautifulSoup(resp.text, "html.parser")

        beskederHtml = soup.find_all("tr")[2:-2]

    options = []
    for div in soup.find("div", {"id": "s_m_Content_Content_ListGridSelectionTree"}).find_all("div", {
        "lec-role": "treeviewnodecontainer"}):
        if "-" in div.get("lec-node-id"):
            name = div.text.rstrip()
            option = {
                "name": None,
                "id": div.get("lec-node-id"),
                "selected": False,
                "content": []
            }
            if div.find("a", {"class": "selectedFolder"}) != None:
                option["selected"] = True

            if len(name.split("\n")) == 1:
                option["name"] = name
                options.append(option)
            else:
                name = div.text.rstrip().split("\n")[0]
                option["name"] = name
                for item in div.find_all("div", {"lec-role": "treeviewnodecontainer"}):
                    option["content"].append({
                        "name": item.text.rstrip(),
                        "id": item.get("lec-node-id")
                    })

                options.append(option)

    beskedHeader = []
    for th in beskederHtml[0].find_all("th"):
        if len(header := th.text.rstrip()) != 0:
            header = header.lower().title().replace(" ", "")
            header = header[0].lower() + header[1:]
            beskedHeader.append(header)

    beskeder = []
    for beskedHtml in beskederHtml[1:]:
        besked = {}

        i = 0
        for td in beskedHtml.find_all("td")[3:-2]:
            if beskedHeader[i] == "modtagere":
                besked[beskedHeader[i]] = td.find("span").get("title").split("\r\n")
            else:
                try:
                    besked[beskedHeader[i]] = td.find("span").get("title")
                except Exception:
                    besked[beskedHeader[i]] = td.text.lstrip().rstrip()

                if beskedHeader[i] == "emne":
                    besked["message_id"] = re.findall("\$_\d+", td.find("a").get("onclick"))[0].replace("$_", "")

            i += 1

        beskeder.append(besked)

    return {"besked_muligheder": options, "beskeder": beskeder}

def calculateSpacing(besked, beskedOversigt, spacing=0):
    if beskedOversigt[besked] != None:
        return calculateSpacing(beskedOversigt[besked], beskedOversigt, spacing+1)
    else:
        return spacing

def besked(self, message_id):
    url = f"https://www.lectio.dk/lectio/{self.skoleId}/beskeder2.aspx?type=showthread&elevid={self.elevId}&id={message_id}"
    resp = self.session.get(url)
    if resp.url != url:
        raise Exception("lectio-cookie udløbet")
    soup = BeautifulSoup(resp.text, "html.parser")

    beskeder = []
    beskederHtml = soup.find("table", {"id": "s_m_Content_Content_MessageThreadCtrlId_MessagesGV"}).find_all("tr")

    beskedOversigt = {}
    for besked in soup.find("table", {"id": "s_m_Content_Content_MessageThreadCtrlId_MessagesGV"}).find_all("tr")[:-1]:
        try:
            beskedOversigt[besked.find("div", {"class": "message-thread-message-sender"}).text.strip()] = besked.find("div", {"class": "message-reply-summary viewed-persons-message"}).text.replace("Er svar på besked af ", "").strip()
        except Exception:
            beskedOversigt[besked.find("div", {"class": "message-thread-message-sender"}).text.strip()] = None

    for besked in beskederHtml[:-1]:
        bruger = {"navn": besked.find("div", {"class": "message-thread-message-sender"}).find("span").text, "id": besked.find("div", {"class": "message-thread-message-sender"}).find("span").get("data-lectiocontextcard")}
        try:
            besvarelse = besked.find("div", {"class": "message-reply-summary viewed-persons-message"}).text.replace("Er svar på besked af ", "").strip()
        except Exception:
            besvarelse = None
        try:
            vedhæftninger = besked.find("div", {"class": "message-attachements"}).find_all("a")
        except Exception:
            vedhæftninger = []

        beskedDict = {
            "bruger": bruger,
            "titel": besked.find("div", {"class": "message-thread-message-header"}).text.strip(),
            "dato": besked.find("div", {"class": "message-thread-message-sender"}).text.replace(bruger["navn"], "").strip()[2:],
            "padding_left": 0,
            "besked": besked.find("div", {"class": "message-thread-message-content"}).text.strip(),
            "vedhæftninger": [{"navn": vedhæft.text, "href": "https://www.lectio.dk"+vedhæft.get("href")} for vedhæft in vedhæftninger],
            "besvarelse": besvarelse,
            "id": None,
        }

        try:
            beskedDict["id"] = re.search("ctl\d+", str(besked.find("div", {"class": "lec-context-menu"}))).group()
        except Exception:
            pass

        if besvarelse != None:
            beskedDict["padding_left"] = calculateSpacing(f"{bruger['navn']}, {beskedDict['dato']}", beskedOversigt)

        beskeder.append(beskedDict)

    sortedBeskeder = []
    for besked in beskeder:
        if besked["besvarelse"]:
            sortedBeskeder.insert([i for i, _besked in enumerate(sortedBeskeder) if besked["besvarelse"] == f"{_besked['bruger']['navn']}, {_besked['dato']}"][0]+1, besked)
        else:
            sortedBeskeder.append(besked)

    beskedDict = {
        "modtagere": ", ".join([str(modtager.text) for modtager in soup.find("div", {"id": "s_m_Content_Content_MessageThreadCtrlId_RecipientsReadMode"}) if len(modtager.text.strip().replace(",", "")) > 0]).strip(),
        "beskeder": sortedBeskeder
    }

    return beskedDict

def besvarBesked(self, message_id, id, titel, content, _from):
    content = content  + "\n\n" + ["Sendt fra [url=github.com/BetterLectio/python-lectio] python-lectio [/url]", "Sendt fra [url=betterlectio.dk] BetterLectio [/url]"][_from]

    url = f"https://www.lectio.dk/lectio/{self.skoleId}/beskeder2.aspx?type=showthread&elevid={self.elevId}&id={message_id}"
    resp = self.session.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    payload = _utils.generatePayload(soup, "__Page")
    payload["__EVENTARGUMENT"] = id
    payload["__LASTFOCUS"] = ""
    payload["s$m$searchinputfield"] = ""
    payload["s$m$Content$Content$SPSearchText$tb"] = ""
    payload["LectioPostbackId"] = ""

    payloadEncoded = "&".join(f"{urllib.parse.quote(key)}={urllib.parse.quote(value).replace('%20', '+')}" for key, value in payload.items())
    resp = self.session.post(f"https://www.lectio.dk/lectio/{self.skoleId}/beskeder2.aspx?type=showthread&id={message_id}&elevid={self.elevId}", data=payloadEncoded)
    soup = BeautifulSoup(resp.text, "html.parser")

    payload = _utils.generatePayload(soup, "s$m$Content$Content$CreateAnswerOKBtn")
    payload["__LASTFOCUS"] = ""
    payload["__EVENTARGUMENT"] = ""
    payload["s$m$searchinputfield"] = ""
    payload["s$m$Content$Content$addRecipientToAnswerDD$inp"] = "" # Skal tilføjes som option
    payload["s$m$Content$Content$Notification"] = "NotifyBtnAuthor" # Skal tilføjes som option
    payload["s$m$Content$Content$RepliesToResponseAllowed"] = "on" # Skal tilføjes som option
    payload["s$m$Content$Content$CreateAnswerHeading$tb"] = titel
    payload["s$m$Content$Content$CreateAnswerContent$TbxNAME$tb"] = content
    payload["LectioPostbackId"] = ""

    payloadEncoded = "&".join(f"{urllib.parse.quote(key)}={urllib.parse.quote(value).replace('%20', '+')}" for key, value in payload.items())

    resp = self.session.post(f"https://www.lectio.dk/lectio/{self.skoleId}/beskeder2.aspx?type=showthread&id={message_id}&elevid={message_id}", data=payloadEncoded, allow_redirects=False)

    if resp.status_code == 303:
        return {"success": True}
    else:
        raise Exception("Levering af besvarelsen var ikke succesfuld")