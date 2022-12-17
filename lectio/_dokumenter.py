from .imports import *

def dokumenter(self, folderid=None):
    resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/DokumentOversigt.aspx?elevid={self.elevId}" if folderid == None else f"https://www.lectio.dk/lectio/{self.skoleId}/DokumentOversigt.aspx?elevid={self.elevId}&folderid={folderid}")
    soup = BeautifulSoup(resp.text, "html.parser")

    dokumenterDict = {"titel": soup.find("span", {"id": "s_m_Content_Content_FolderLabel"}).text, "indhold": []}

    if folderid == None:
        for element in soup.find("div", {"id": "s_m_Content_Content_FolderTreeView"}):
            if element != None:
                if str(element) != "\n":
                    itemDict = {
                        "navn": element.find("div", {"class": "TreeNode-title"}).text,
                        "type": "folder",
                        "id": element.get("lec-node-id")
                    }
                    dokumenterDict["indhold"].append(itemDict)
    else:
        _element = soup.find("div", {"lec-node-id": folderid})
        backId = _element.parent.parent.get("lec-node-id")
        dokumenterDict["indhold"].append({
            "navn": "..",
            "type": "folder",
            "id": backId if backId != None else ".."
        })

        element = _element.find("div", {"lec-role": "ltv-sublist"})
        if element != None:
            for _element in element:
                if str(_element) != "\n":
                    itemDict = {
                        "navn": _element.find("div", {"class": "TreeNode-title"}).text,
                        "type": "folder",
                        "id": _element.get("lec-node-id")
                    }
                    dokumenterDict["indhold"].append(itemDict)

        files = soup.find("div", {"id": "printfoldercontent"}).find_all("tr")
        # TODO: Tjek om mappens title er Aktiviteter eller Holdmaterialer for så er opbygningen af mappen anderledes
        if not 'class="noRecord nowrap"' in str(files):
            for tr in files[1:]:
                if dokumenterDict["titel"] == "Aktiviteter":
                    _tds = tr.find_all("td")
                    tds = [_tds[1], _tds[2], "ukendt", _tds[0]]
                    ændret_af = "ukendt"
                    id = tds[0].find("a").get('href').split("lc/")[1]
                else:
                    tds = tr.find_all("td")[:-1] if dokumenterDict["titel"] == "Nyeste dokumenter" else tr.find_all("td")[1:-1]
                    ændret_af = tds[2].find("span", {"class": "tooltip"}).get("title")
                    id = tds[0].find("a").get('href').split("documentid=")[1]

                filDict = {
                    "navn": unicodedata.normalize('NFD', tds[0].find("a").text).lstrip().rstrip(),
                    "type": "dokument",
                    "id": id,
                    "kommentar": tds[1].find("span", {"class": "tooltip"}).get("title"),
                    "ændret_af": ændret_af,
                    "dato": tds[3].text
                }

                dokumenterDict["indhold"].append(filDict)

    return dokumenterDict