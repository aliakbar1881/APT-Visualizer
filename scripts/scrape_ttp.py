import requests
from bs4 import BeautifulSoup
import csv
from loguru import logger


class RequestError(BaseException):
    pass

class TTPs:
    def __init__(self, base_url, ttp_url):
        self.base_url = base_url
        self.ttp_url = ttp_url
        self.tactics = []
        self.techniques = []

    def __call__(self):
        self.fetch_tactics()
        self.fetch_techniques()
    
    def fetch_tactics(self):
        resp = requests.get(self.ttp_url)
        soup = BeautifulSoup(resp.content, "html.parser")
        techniques = soup.tbody.find_all("tr")
        for technique in techniques:
            td = technique.find_all("td")
            self.tactics.append([td[0].a.string, td[1].a.string])

    def fetch_techniques(self):
        for tactic in self.tactics:
            parent_technique = ""
            tactic_id = tactic[0]
            tactic_name = tactic[1]
            url = f"https://attack.mitre.org/tactics/{tactic_id}/"
            resp = requests.get(url)
            soup = BeautifulSoup(resp.content, "html.parser")
            techniques = soup.tbody.find_all("tr")
            for technique in techniques:
                tds = technique.find_all("td")
                if len(tds) == 3:
                    parent_technique = tds[0].a.string.strip()
                    self.techniques.append(
                        [
                            tactic_id,
                            tactic_name,
                            tds[0].a.string,
                            tds[1].a.string,
                        ]
                    )
                elif len(tds) == 4:
                    self.techniques.append(
                        [
                            tactic_id,
                            tactic_name,
                            parent_technique + tds[1].a.string.strip(),
                            tds[2].a.string
                        ]
                    )
        with open("techniques.csv", "w") as f:
            for row in self.techniques:
                writer = csv.writer(f)
                writer.writerow(row)


if __name__ == "__main__":
    ttps = TTPs("https://attack.mitre.org/", "https://attack.mitre.org/tactics/enterprise/")
    ttps()
