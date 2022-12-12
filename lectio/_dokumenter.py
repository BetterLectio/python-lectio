from .imports import *

def dokumenter(self, folderid=None):
    resp = self.session.get(f"https://www.lectio.dk/lectio/681/DokumentOversigt.aspx?elevid={self.elevId}" if folderid == None else f"https://www.lectio.dk/lectio/681/DokumentOversigt.aspx?elevid={self.elevId}&folderid={folderid}")
    soup = BeautifulSoup(resp.text, "html.parser")

    dokumenterDict = []

    if folderid == None:
        for element in soup.find("div", {"id": "s_m_Content_Content_FolderTreeView"}):
            if element != None:
                if str(element) != "\n":
                    itemDict = {
                        "name": element.find("div", {"class": "TreeNode-title"}).text,
                        "type": "folder",
                        "id": element.get("lec-node-id")
                    }
                    dokumenterDict.append(itemDict)
    else:
        element = soup.find("div", {"lec-node-id": folderid}).find("div", {"lec-role": "ltv-sublist"})
        if element != None:
            for _element in element:
                if str(_element) != "\n":
                    itemDict = {
                        "navn": _element.find("div", {"class": "TreeNode-title"}).text,
                        "type": "folder",
                        "id": _element.get("lec-node-id")
                    }
                    dokumenterDict.append(itemDict)

    files = soup.find("div", {"id": "printfoldercontent"}).find_all("tr")

    # TODO: Tjek om mappens title er Aktiviteter eller Holdmaterialer for så er opbygningen af mappen anderledes
    if not 'class="noRecord nowrap"' in str(files):
        for tr in files[1:]:
            tds = tr.find_all("td")[1:-1]
            filDict = {
                "navn": unicodedata.normalize('NFD', tds[0].find("a").text).lstrip().rstrip(),
                "type": "dokument",
                "id": tds[0].find("a").get('href').split("documentid=")[1],
                "kommentar": tds[1].find("span", {"class": "tooltip"}).get("title"),
                "ændret_af": tds[2].find("span", {"class": "tooltip"}).get("title"),
                "dato": tds[3].text
            }

            dokumenterDict.append(filDict)

    return dokumenterDict