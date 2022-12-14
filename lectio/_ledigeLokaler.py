from .imports import *

def ledigeLokaler(self):
    url = f"https://www.lectio.dk/lectio/{self.skoleId}/SkemaAvanceret.aspx?type=aktuelleallelokaler&nosubnav=1&prevurl=FindSkemaAdv.aspx"
    resp = self.session.get(url)
    if resp.url != url:
        raise Exception("lectio-cookie udløbet")
    soup = BeautifulSoup(resp.text, "html.parser")

    ledigeLokalerDict = []
    for div in soup.find("div", {"id": "m_Content_LectioDetailIsland1_pa"}).find_all("div"):
        try:
            if div.get("id").startswith("printSingleControl"):
                ledigeLokalerDict.append({
                    "lokale": div.find("span").text,
                    "status": "ledigt" if "Der er ingen data..." in str(div) else "optaget"
                })
        except:
            pass

    return ledigeLokalerDict