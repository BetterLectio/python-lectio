"""
TODO:
  * Gør elev og lærer id til id men hvor at elev id har et S foran (Eks: S123456789) og lærer har et T foran (Eks: T12345678)
"""

from .imports import *
from . import _auth, _lektier, _skema, _modul, _opgaver, _beskeder, _informationer, _filer, _fravær, _dokumenter, _forside, _ledigeLokaler, _karakterer, _eksamener, _studieretning, _spørgeskema, _termin

class sdk:
    def __init__(self, brugernavn, adgangskode, skoleId, base64Cookie=None):
        self.session = requests.session()

        if base64Cookie == None:
            self.brugernavn = brugernavn
            self.adgangskode = adgangskode
            self.skoleId = skoleId

            self.login()
        else:
            cookie = json.loads(base64.b64decode(base64Cookie))
            for _cookie in cookie:
                self.session.cookies.set(_cookie["name"], _cookie["value"], domain=_cookie["for"])

            self.skoleId = self.session.cookies["LastLoginExamno"]
            self.elevId = self.session.cookies["LastLoginElevId"]

        self.session.headers.update({"content-type": "application/x-www-form-urlencoded"})
    def login(self):
        return _auth.login(self)

    def base64Cookie(self):
        return _auth.base64Cookie(self)

    def lektier(self):
        return _lektier.lektier(self)

    def skema(self, uge=None, år=None, id=None):
        return _skema.skema(self, uge=uge, år=år, id=id)

    def modul(self, absid):
        return _modul.modul(self, absid)

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