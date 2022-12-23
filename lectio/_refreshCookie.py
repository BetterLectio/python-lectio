from .imports import *

def refreshCookie(self):
    try:
        oldSessionId = self.session.cookies["ASP.NET_SessionId"]
        #resp = self.session.get(f"https://lectio.dk/lectio/{self.skoleId}/forside.aspx", allow_redirects=False)
        headers = {
            "cookie": f"lectiogsc={self.session.cookies['lectiogsc']}; autologinkey={self.session.cookies['autologinkey']}",
        }
        resp = requests.get(f"https://www.lectio.dk/lectio/{self.skoleId}/forside.aspx", headers=headers, allow_redirects=False)
        newSessionId = resp.cookies["ASP.NET_SessionId"]
        if newSessionId != oldSessionId:
            self.session.cookies.set('ASP.NET_SessionId', newSessionId, domain='lectio.dk', path='/')

            return {"success": True}
    except Exception:
        pass

    return {"success": False}