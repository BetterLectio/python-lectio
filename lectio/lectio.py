from .imports import *
from . import _auth, _lektier, _skema, _modul, _opgaver, _beskeder, _informationer, _filer, _fravær, _dokumenter, _forside, _ledigeLokaler, _karakterer, _eksamener, _studieretning, _spørgeskema, _termin, _studieplan

class sdk:
    def __init__(self, brugernavn=None, adgangskode=None, skoleId=None, base64Cookie=None, userId=None, QrId=None):
        self.session = requests.session()

        if brugernavn != None and adgangskode != None and skoleId != None:
            self.brugernavn = brugernavn
            self.adgangskode = adgangskode
            self.skoleId = skoleId

            self.login()
        elif base64Cookie != None:
            cookie = json.loads(base64.b64decode(base64Cookie))
            for _cookie in cookie:
                self.session.cookies.set(_cookie["name"], _cookie["value"], domain=_cookie["for"])

            self.skoleId = self.session.cookies["LastLoginExamno"]
            self.elevId = self.session.cookies["LastLoginElevId"]
        elif userId != None and QrId != None and skoleId != None:
            self.skoleId = skoleId

            self.qrLogin(userId, QrId)
        else:
            raise Exception("Der blev ikke angivet nok parameter til at kunne logge ind.")


        self.session.cookies.set("isloggedin3", "Y", domain="www.lectio.dk")
        self.session.headers.update({
            "content-type": "application/x-www-form-urlencoded",
            "referer": f"https://www.lectio.dk/lectio/{self.skoleId}/forside.aspx",
        })
    def login(self):
        return _auth.login(self)

    def base64Cookie(self):
        return _auth.base64Cookie(self)

    def qrLogin(self, userId, QrId):
        return _auth.qrLogin(self, userId, QrId)

    def lektier(self):
        return _lektier.lektier(self)

    def skema(self, uge=None, år=None, id=None):
        return _skema.skema(self, uge=uge, år=år, id=id)

    def modul(self, absid):
        return _modul.modul(self, absid)

    def modulHtml(self, absid):
        return _modul.modulHtml(self, absid)

    def opgave(self, exerciseid):
        return _opgaver.opgave(self, exerciseid)
    def opgaver(self):
        return _opgaver.opgaver(self)

    def besked(self, message_id):
        return _beskeder.besked(self, message_id=message_id)

    def beskeder(self, id=None):
        return _beskeder.beskeder(self, id=id)

    def informationer(self):
        return _informationer.informationer(self)

    def fåElev(self, elevId):
        return _informationer.fåElev(self, elevId)

    def fåBruger(self, brugerId):
        return _informationer.fåBruger(self, brugerId)

    def fåFil(self, filUrl):
        return _filer.fåFil(self, filUrl)

    def fravær(self):
        return _fravær.fravær(self)

    def dokumenter(self, folderid=None):
        return _dokumenter.dokumenter(self, folderid)

    def forside(self):
        return _forside.forside(self)

    def besvarBesked(self, message_id, id, titel, content, _from=0):
        return _beskeder.besvarBesked(self, message_id, id, titel, content, _from)

    def ledigeLokaler(self):
        return _ledigeLokaler.ledigeLokaler(self)

    def eksamener(self):
        return _eksamener.eksamener(self)
    
    def karakterer(self):
        return _karakterer.karakterer(self)

    def studieretningspræsentation(self, elevId=None):
        return _studieretning.studieretningspræsentation(self, elevId=elevId)

    def spørgeskemaer(self):
        return _spørgeskema.spørgeskemaer(self)

    def opretMappe(self, folderName, folderComment, folderId):
        return _dokumenter.opretMappe(self, folderName, folderComment, folderId)

    def holdTilFag(self, holdId):
        return _skema.holdTilFag(self, holdId)

    def fåTerminer(self):
        return _termin.fåTerminer(self)

    def ændreTermin(self, terminId):
        return _termin.ændreTermin(self, terminId)

    def spørgeskema(self, id):
        return _spørgeskema.spørgeskema(self, id)

    def besvarSpørgeskema(self, id, besvarelser):
        return _spørgeskema.besvarSpørgeskema(self, id, besvarelser)

    def lokaleDagsorden(self, kunAktuelAfdeling=True):
        return _ledigeLokaler.lokaleDagsorden(self, kunAktuelAfdeling)

    def studieplan(self):
        return _studieplan.studieplan(self)

    def forløb(self, id):
        return _studieplan.forløb(self, id)

    def dokumentUpload(self, fileName, folderId, contentType, content, fileComment="", public=False, documentId=None):
        return _dokumenter.dokumentUpload(self, fileName, folderId, contentType, content, fileComment, public, documentId)

    def dokumentHent(self, dokumentId, doctype=None):
        return _dokumenter.dokumentHent(self, dokumentId, doctype)

    def fåHoldMedlemmer(self, id):
        return _informationer.fåHoldMedlemmer(self, id)

    def afleverOpgave(self, exerciseid, fileName, fileContentType, fileContent="", note=None):
        return _opgaver.afleverOpgave(self, exerciseid, fileName, fileContentType, fileContent, note)