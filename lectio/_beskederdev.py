from .imports import *

def beskeder(self, id=None):
    if id != None:
        if "-" in str(id):
            url = f"https://www.lectio.dk/lectio/{self.skoleId}/beskeder2.aspx?type=&elevid={self.elevId}&selectedfolderid={id}"
        else:
            url = f"https://www.lectio.dk/lectio/{self.skoleId}/beskeder2.aspx?type=selecthold&elevid={self.elevId}&holdid={id}"
    else:
        url = f"https://www.lectio.dk/lectio/680/beskeder2.aspx?type=liste&elevid={self.elevId}"

    resp = self.session.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

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

    beskederHtml = soup.find_all("tr")

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
                        besked["message_id"] = re.findall("\$_\d+", td.find("a").get("onclick"))[0].replace("$_", "")

                i += 1

        beskeder.append(besked)

    return {"besked_muligheder": options, "beskeder": beskeder}

def besked(self, message_id):
    resp = self.session.get(f"https://www.lectio.dk/lectio/681/beskeder2.aspx?type=showthread&elevid={self.elevId}&id={message_id}")
    soup = BeautifulSoup(resp.text, "html.parser")

    beskeder = []
    beskederHtml = soup.find("ul", {"id": "s_m_Content_Content_ThreadList"}).find_all("li")

    paddingLeftResponseNum = {}
    i = 0

    _beskederOgRespons = {}

    lastI = i
    beskederNy = []
    for besked in beskederHtml:
        bruger = besked.find("span")
        beskedDiv = None
        for div in besked.find_all("div"):
            if div.get("class") == None:
                beskedDiv = div
                break

        if beskedDiv == None:
            raise Exception("Kan ikke finde besked, rapporter venligst dette på Github")

        paddingLeft = re.search("padding-left:\d*\.?\d*", str(besked.get("style"))).group().replace("padding-left:", "")

        beskedDict = {
            "bruger": {"navn:": bruger.text, "id": bruger.get("data-lectiocontextcard")},
            "titel": besked.find("h4").text,
            "dato": re.search("[0-9]+/[0-9]+-[0-9]+ [0-9]+:[0-9]+", besked.find("td").text).group(),
            "padding_left": re.search("padding-left:\d*\.?\d*", str(besked.get("style"))).group().replace("padding-left:", ""),
            "besked": markdownify.markdownify(str(beskedDiv), heading_style="ATX").lstrip().rstrip().replace("\n\n", "\n"),
            "vedhæftninger": [{"navn": vedhæft.text, "href": "https://www.lectio.dk"+vedhæft.get("href")} for vedhæft in besked.find("td").find_all("a", {"id": None})],
            "svar": []
        }
        if i == 0:
            beskederNy.append(beskedDict)


        hoppeMængde = ""
        for j in range(i):
            hoppeMængde += "[0][\"svar\"]"

        if paddingLeft not in paddingLeftResponseNum:
            paddingLeftResponseNum[paddingLeft] = i
            if i != 0:
                print(f"beskederNy{hoppeMængde} = [{beskedDict}]")
                exec(f"beskederNy{hoppeMængde} = [{beskedDict}]")
        else:
            i = paddingLeftResponseNum[paddingLeft]
            exec(f"beskederNy{hoppeMængde}.append({beskedDict})")

        #print(f"Svar til besked #{i}: {beskedDict}")

        beskeder.append(beskedDict)

        _beskederOgRespons[str(i)] = beskedDict

        #print(beskederNy)
        i += 1

    print(json.dumps(beskederNy, indent=2))
    exit()

    return beskeder

def sendBesked(self, message_id, content):
    pass