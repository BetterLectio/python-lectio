from .imports import *

def dokumenter(self, folderid=None):
    resp = self.session.get(f"https://www.lectio.dk/lectio/681/DokumentOversigt.aspx?elevid={self.elevId}")
    soup = BeautifulSoup(resp.text, "html.parser")

    dokumenterDict = {
        "folders": []
    }