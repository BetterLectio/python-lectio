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
        for td in beskedHtml.find_all("td"):
            if len(value := td.text.lstrip().rstrip()) != 0:
                if beskedHeader[i] == "modtagere":
                    besked[beskedHeader[i]] = td.find("span").get("title").split("\r\n")
                else:
                    try:
                        besked[beskedHeader[i]] = td.find("span").get("title")
                    except Exception:
                        besked[beskedHeader[i]] = value

                    if beskedHeader[i] == "emne":
                        print(td.find("a"))
                        besked["message_id"] = re.findall("\$_\d+", td.find("a").get("onclick"))[0].replace("$_", "")

                i += 1

        beskeder.append(besked)

    return {"besked_muligheder": options, "beskeder": beskeder}

def besked(self, message_id):
    resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/beskeder2.aspx?type=showthread&elevid={self.elevId}&id={message_id}")
    soup = BeautifulSoup(resp.text, "html.parser")

    beskeder = []
    beskederHtml = soup.find("ul", {"id": "s_m_Content_Content_ThreadList"}).find_all("li")

    for besked in beskederHtml:
        bruger = besked.find("span")
        beskedDiv = None
        for div in besked.find_all("div"):
            if div.get("class") == None:
                beskedDiv = div
                break

        if beskedDiv == None:
            raise Exception("Kan ikke finde besked, rapporter venligst dette på Github")

        beskedDict = {
            "bruger": {"navn": bruger.text, "id": bruger.get("data-lectiocontextcard")},
            "titel": besked.find("h4").text,
            "dato": re.search("[0-9]+/[0-9]+-[0-9]+ [0-9]+:[0-9]+", besked.find("td").text).group(),
            "padding_left": re.search("padding-left:\d*\.?\d*", str(besked.get("style"))).group().replace("padding-left:", ""),
            "besked": markdownify.markdownify(str(beskedDiv), heading_style="ATX").lstrip().rstrip().replace("\n\n", "\n"),
            "vedhæftninger": [{"navn": vedhæft.text, "href": "https://www.lectio.dk"+vedhæft.get("href")} for vedhæft in besked.find("td").find_all("a", {"id": None})],
            "id": re.search("'\w+MESSAGE_\d+", str(besked.find("button").get("onclick"))).group().replace("'", ""),
        }
        beskeder.append(beskedDict)

    return beskeder

def besvarBesked(self, message_id, id, titel, content, _from):
    content = content  + "\n\n" + ["Sendt fra [url=github.com/BetterLectio/python-lectio] python-lectio [/url]", "Sendt fra [url=betterlectio.dk] Better Lectio [/url]"][_from]

    resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/beskeder2.aspx?type=showthread&elevid={self.elevId}&id={message_id}")
    soup = BeautifulSoup(resp.text, "html.parser")

    payload = _utils.generatePayload(soup, "__Page")
    payload["__EVENTARGUMENT"] = id
    payload["__LASTFOCUS"] = ""
    payload["s$m$searchinputfield"] = ""
    payload["s$m$Content$Content$SPSearchText$tb"] = ""
    payload["LectioPostbackId"] = ""


    resp = self.session.post(f"https://www.lectio.dk/lectio/{self.skoleId}/beskeder2.aspx?type=showthread&id={message_id}&elevid={self.elevId}", data=payload)
    soup = BeautifulSoup(resp.text, "html.parser")

    payload = _utils.generatePayload(soup, "s$m$Content$Content$CreateAnswerOKBtn")
    print(payload)
    print(urllib.parse.quote(content))
    print(urllib.parse.quote(titel))

    resp = self.session.post(f"https://www.lectio.dk/lectio/{self.skoleId}/beskeder2.aspx?type=showthread&id={message_id}&elevid={message_id}", data=f"__LASTFOCUS=&time=0&__EVENTTARGET=s%24m%24Content%24Content%24CreateAnswerOKBtn&__EVENTARGUMENT=&__SCROLLPOSITION=&__VIEWSTATEX={urllib.parse.quote(payload['__VIEWSTATEX'])}&__VIEWSTATEY_KEY=&__VIEWSTATE=&__VIEWSTATEENCRYPTED=&s%24m%24searchinputfield=&s%24m%24Content%24Content%24addRecipientToAnswerDD%24inp=&s%24m%24Content%24Content%24addRecipientToAnswerDD%24inpid=&s%24m%24Content%24Content%24Notification=NotifyBtnAuthor&s%24m%24Content%24Content%24RepliesToResponseAllowed=on&s%24m%24Content%24Content%24CreateAnswerHeading%24tb={urllib.parse.quote(titel)}&s%24m%24Content%24Content%24CreateAnswerDocChooser%24selectedDocumentId=&s%24m%24Content%24Content%24CreateAnswerContent%24TbxNAME%24tb={urllib.parse.quote(content)}&masterfootervalue=X1%21%C3%86%C3%98%C3%85&LectioPostbackId=", allow_redirects=False)

    if resp.status_code == 303:
        return {"success": True}
    else:
        raise Exception("Levering af besvarelsen var ikke succesfuld")