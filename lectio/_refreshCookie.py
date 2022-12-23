def refreshCookie(self):
    del self.session.cookies["LastAuthenticatedPageLoad"]
    del self.session.cookies["ASP.NET_SessionId"]

    resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/forside.aspx", allow_redirects=False, cookies=self.session.cookies)
    resp = self.session.get(f"https://www.lectio.dk{resp.headers['Location']}", allow_redirects=False, cookies=self.session.cookies)
    resp = self.session.get(f"https://www.lectio.dk{resp.headers['Location']}", allow_redirects=False, cookies=self.session.cookies)
    if resp.status_code == 200:
        return {"success": False}

    return {"success": True}