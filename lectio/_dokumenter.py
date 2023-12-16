from .imports import *
from . import _utils

def dokumenter(self, folderid=None):
    url = f"https://www.lectio.dk/lectio/{self.skoleId}/DokumentOversigt.aspx?elevid={self.elevId}" if folderid == None else f"https://www.lectio.dk/lectio/{self.skoleId}/DokumentOversigt.aspx?elevid={self.elevId}&folderid={folderid}"
    resp = self.session.get(url)
    if resp.url != url:
        raise Exception("lectio-cookie udløbet")
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

def opretMappe(self, folderName, folderComment, folderId):
    url = f"https://www.lectio.dk/lectio/{self.skoleId}/DokumentFolderRediger.aspx?parentfolderid={folderId}"
    resp = self.session.get(url)
    if resp.url != url:
        raise Exception("lectio-cookie udløbet")
    soup = BeautifulSoup(resp.text, "html.parser")

    payload = _utils.generatePayload(soup, "m$Content$SaveButtonsRow$svbtn")
    payload["__EVENTARGUMENT"] = ""
    payload["__LASTFOCUS"] = ""
    payload["m$searchinputfield"] = ""
    payload["LectioPostbackId"] = ""
    payload["m$Content$EditFolderName$tb"] = folderName
    payload["m$Content$EditFolderComments"] = folderComment
    payload["m$Content$FolderBox$ctl03"] = folderId

    resp = self.session.post(f"https://www.lectio.dk/lectio/681/DokumentFolderRediger.aspx?parentfolderid={folderId}", data="&".join([f"{urllib.parse.quote(key)}={urllib.parse.quote(value)}" for key, value in payload.items()]), allow_redirects=False)
    if resp.status_code == 303:
        return {"success": True}
    else:
        raise Exception("Oprettelsen af mappen var ikke succesfuld")

def dokumentHent(self, dokumentId, doctype):
    url = f"https://www.lectio.dk/lectio/{self.skoleId}/dokumenthent.aspx?documentid={dokumentId}"
    if doctype: url += f"&doctype={doctype}"
    resp = self.session.get(url)
    if resp.url != url:
        raise Exception("lectio-cookie udløbet")

    return {
        "content": resp.content,
        "content-type": resp.headers["content-type"],
        "content-disposition": resp.headers["content-disposition"],
    }

def dokumentUpload(self, fileName, folderId, contentType, content, fileComment, public, documentId):
    urlDokumentRediger = f"https://www.lectio.dk/lectio/{self.skoleId}/dokumentrediger.aspx?" + (f"dokumentid={documentId}" if documentId else f"folderid={folderId}")
    resp = self.session.get(urlDokumentRediger)
    if resp.url != urlDokumentRediger:
        raise Exception("lectio-cookie udløbet")
    soupSubmit = BeautifulSoup(resp.text, "html.parser")

    url = f"https://www.lectio.dk/lectio/{self.skoleId}/documentchoosercontent.aspx?year=2023&ispublic=0&showcheckbox=1&mode=pickfile"
    resp = self.session.get(url)
    if resp.url != url:
        raise Exception("lectio-cookie udløbet")
    soupFile = BeautifulSoup(resp.text, "html.parser")

    payload = _utils.generatePayload(soupFile, "ctl00$Content$newfileOK")
    payload["__LASTFOCUS"] = ""
    payload["__EVENTARGUMENT"] = ""
    payload["LectioPostbackId"] = ""

    webKitFormBoundary = ""
    for key, value in payload.items():
        webKitFormBoundary += f'------WebKitFormBoundaryi4oxASAKjAOULyBa\nContent-Disposition: form-data; name="{key}"\n\n{value}\n'
    webKitFormBoundary += f'------WebKitFormBoundaryi4oxASAKjAOULyBa\nContent-Disposition: form-data; name="ctl00$Content$fileUpload_up"; filename="{fileName}"\nContent-Type: {contentType}\n\n{content}\n------WebKitFormBoundaryi4oxASAKjAOULyBa--'

    resp = self.session.post(f"https://www.lectio.dk/lectio/{self.skoleId}/documentchoosercontent.aspx?year=2023&ispublic=0&showcheckbox=1&mode=pickfile", data=webKitFormBoundary, headers={
        "content-type": "multipart/form-data; boundary=----WebKitFormBoundaryi4oxASAKjAOULyBa"
    })
    if resp.url != url:
        raise Exception("lectio-cookie udløbet")

    serializedId = re.search('"serializedId":"\w+"', resp.text).group()[16:-1]
    payload = _utils.generatePayload(soupSubmit, "m$Content$docChooser")
    payload["__EVENTARGUMENT"] = "documentId"
    payload["__LASTFOCUS"] = ""
    payload["m$searchinputfield"] = ""
    payload["m$Content$docChooser$selectedDocumentId"] = '{"type":"serializedAnyFileId","serializedId":"'+serializedId+'","isPublic":true,"filename":"' + fileName +'"}'
    payload["m$Content$EditDocRelatedAddDD$inp"] = ""
    payload["LectioPostbackId"] = ""

    resp = self.session.post(urlDokumentRediger, data="&".join(f"{urllib.parse.quote(key)}={urllib.parse.quote(value).replace('%20', '+')}" for key, value in payload.items()), headers={
        "content-type": "application/x-www-form-urlencoded"
    })
    soup = BeautifulSoup(resp.text, "html.parser")
    payload = _utils.generatePayload(soup, "m$Content$SaveButtonsRow$svbtn")
    payload["__EVENTARGUMENT"] = ""
    payload["m$searchinputfield"] = ""
    payload["m$Content$EditDocComments$tb"] = fileComment
    payload["m$Content$AffiliationsGV$ctl02$FolderBox$ctl03"] = folderId
    payload["m$Content$EditDocRelatedAddDD$inp"] = ""
    payload["LectioPostbackId"] = ""
    if documentId:
        payload["m$Content$AffiliationsGV$ctl02$AllowEditCheckBox"] = "on"
    if public: payload["m$Content$EditDocIsPublic"] = "on"

    resp = self.session.post(urlDokumentRediger, data="&".join(f"{urllib.parse.quote(key)}={urllib.parse.quote(value).replace('%20', '+')}" for key, value in payload.items()))
    if resp.url == f"https://www.lectio.dk/lectio/{self.skoleId}/default.aspx":
        return {"success": True}
    else:
        raise Exception("Upload var ikke succesfuld")
