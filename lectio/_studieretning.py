from .imports import *

def studieretningspræsentation(self):
    url = f"https://www.lectio.dk/lectio/{self.skoleId}/studieretningValgfag.aspx?elevid={self.elevId}"
    resp = self.session.get(url)
    if resp.url != url:
        raise Exception("lectio-cookie udløbet")
    soup = BeautifulSoup(resp.text, "html.parser")
    print(markdownify.markdownify(str(soup.find("div", {"id": "krop"}))))