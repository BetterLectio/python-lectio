"""
TODO:
  * Gør elev og lærer id til id men hvor at elev id har et S foran (Eks: S123456789) og lærer har et T foran (Eks: T12345678)
  * Fjern retry fra enkelte funktioner og gør det til en general ting
"""

from .imports import *
from . import _auth, _lektier, _skema, _modul, _opgaver, _beskeder, _informationer, _filer, _fravær, _dokumenter, _forside, _ledigeLokaler, _refreshCookie

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
            self.skoleId = cookie["LastLoginExamno"]
            self.elevId = cookie["LastLoginElevId"]

            for identifier, value in cookie.items():
                self.session.cookies.set(identifier, value, domain="lectio.dk")

            self.session.headers.update({"content-type": "application/x-www-form-urlencoded"})
    def login(self):
        return _auth.login(self)

    def base64Cookie(self):
        return _auth.base64Cookie(self)

    def lektier(self):
        return _lektier.lektier(self)

    def skema(self, retry=False, uge=None, år=None, elevId=None):
        return _skema.skema(self, retry=retry, uge=uge, år=år, elevId=elevId)

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

    def refreshCookie(self):
        return _refreshCookie.refreshCookie(self)