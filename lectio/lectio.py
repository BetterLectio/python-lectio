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
        try:
            return _lektier.lektier(self)
        except Exception:
            self.refreshCookie()
            return _lektier.lektier(self)

    def skema(self, retry=False, uge=None, år=None, elevId=None):
        try:
            return _skema.skema(self, retry=retry, uge=uge, år=år, elevId=elevId)
        except Exception:
            self.refreshCookie()
            return _skema.skema(self, retry=retry, uge=uge, år=år, elevId=elevId)

    def modul(self, absid):
        try:
            return _modul.modul(self, absid)
        except Exception:
            self.refreshCookie()
            return _modul.modul(self, absid)

    def opgave(self, exerciseid):
        try:
            return _opgaver.opgave(self, exerciseid)
        except Exception:
            self.refreshCookie()
            return _opgaver.opgave(self, exerciseid)
    def opgaver(self):
        try:
            return _opgaver.opgaver(self)
        except Exception:
            self.refreshCookie()
            return _opgaver.opgaver(self)

    def besked(self, message_id):
        try:
            return _beskeder.besked(self, message_id=message_id)
        except Exception:
            self.refreshCookie()
            return _beskeder.besked(self, message_id=message_id)

    def beskeder(self, id=None):
        try:
            return _beskeder.beskeder(self, id=id)
        except Exception:
            self.refreshCookie()
            return _beskeder.beskeder(self, id=id)

    def informationer(self):
        try:
            return _informationer.informationer(self)
        except Exception:
            self.refreshCookie()
            return _informationer.informationer(self)

    def fåElev(self, elevId):
        try:
            return _informationer.fåElev(self, elevId)
        except Exception:
            self.refreshCookie()
            return _informationer.fåElev(self, elevId)

    def fåBruger(self, brugerId):
        try:
            return _informationer.fåBruger(self, brugerId)
        except Exception:
            self.refreshCookie()
            return _informationer.fåBruger(self, brugerId)

    def fåFil(self, filUrl):
        try:
            return _filer.fåFil(self, filUrl)
        except Exception:
            self.refreshCookie()
            return _filer.fåFil(self, filUrl)

    def fravær(self):
        try:
            return _fravær.fravær(self)
        except Exception:
            self.refreshCookie()
            return _fravær.fravær(self)

    def dokumenter(self, folderid=None):
        try:
            return _dokumenter.dokumenter(self, folderid)
        except Exception:
            self.refreshCookie()
            return _dokumenter.dokumenter(self, folderid)

    def forside(self):
        try:
            return _forside.forside(self)
        except Exception:
            self.refreshCookie()
            return _forside.forside(self)

    def besvarBesked(self, message_id, id, titel, content, _from=0):
        try:
            return _beskeder.besvarBesked(self, message_id, id, titel, content, _from)
        except Exception:
            self.refreshCookie()
            return _beskeder.besvarBesked(self, message_id, id, titel, content, _from)

    def ledigeLokaler(self):
        try:
            return _ledigeLokaler.ledigeLokaler(self)
        except Exception:
            self.refreshCookie()
            return _ledigeLokaler.ledigeLokaler(self)

    def refreshCookie(self):
        return _refreshCookie.refreshCookie(self)