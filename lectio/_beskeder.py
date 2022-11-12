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

    selected = None
    options = []
    for div in soup.find("div", {"id": "s_m_Content_Content_ListGridSelectionTree"}).find_all("div", {
        "lec-role": "treeviewnodecontainer"}):
        name = div.text.rstrip()
        if div.find("a", {"class": "selectedFolder"}) != None:
            selected = name
        if "-" in div.get("lec-node-id"):
            if len(name.split("\n")) == 1:
                options.append({
                    "name": name,
                    "id": div.get("lec-node-id"),
                    "content": []
                })
            else:
                name = div.text.rstrip().split("\n")[0]
                option = {
                    "name": name,
                    "id": div.get("lec-node-id"),
                    "content": []
                }
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

    return {"beskedSide": selected, "beskedMuligheder": options, "beskeder": beskeder}

def besked(self, message_id):
    pass

def sendBesked(self, message_id, content):
    pass