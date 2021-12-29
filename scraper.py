from requests.auth import HTTPBasicAuth
import statistics as st
import json
import random
from urllib.parse import urlparse
import requests
import time
from datetime import datetime
import pandas as pd
from typing import List, Tuple
from bs4 import BeautifulSoup
from functools import partial


def GET_UA():
    uastrings = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62",
    ]

    return random.choice(uastrings)


def bs_parse_url(url: str, auth: Tuple[str] = None, accept: str = None):

    if accept:
        headers = {"User-Agent": GET_UA(), "Accept": accept}
    else:
        headers = {"User-Agent": GET_UA()}
    content = None

    try:
        response = requests.get(url, headers=headers, auth=HTTPBasicAuth(auth))
        ct = response.headers["Content-Type"].lower().strip()

        if "text/html" in ct:
            content = response.content
            soup = BeautifulSoup(content, "lxml")
        else:
            content = response.content
            soup = None

    except Exception as e:
        print("Error:", str(e))

    return content, soup, ct


class Repository:
    def __init__(
        self, repo_link: str, username: str, token: str, lines_of_code: int = None
    ) -> None:
        self.repo_link = repo_link
        self.lines_of_code = lines_of_code
        splitted_repo_link = repo_link.split("/")
        self.owner = splitted_repo_link[-2]
        self.repo = splitted_repo_link[-1]
        self.api_base_url = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        self.auth = HTTPBasicAuth(username, token)

        # phasing out the following:
        self.username = username
        self.token = token

    def get_releases(self):
        """

        We only analyze projects that release their code (via Git)


        """
        # /repos/{owner}/{repo}/releases
        endpoint = f"https://api.github.com/repos/{self.repo_link.split('/')[-2]}/{self.repo_link.split('/')[-1]}/releases?per_page=100&anon=1"
        response = requests.get(endpoint, auth=(self.username, self.token)).json()

        return response

    def get_num_collaborators(self):

        """

        Using API instead of scraper as the github console only shows the recent / top committers


        """

        collaborators = []

        endpoint = f"{self.api_base_url}/contributors?per_page=100&anon=1"
        response = requests.get(endpoint, auth=(self.username, self.token))
        collaborators += response.json()
        while "next" in response.links:
            endpoint = response.links["next"]["url"]
            print(f"Getting next url {endpoint}")
            response = requests.get(endpoint, auth=(self.username, self.token))
            collaborators += response.json()

        return len(collaborators)

    def get_num_branches(self) -> int:
        """
        Request all branches in repo from GitHub API and returning number of branches
        """
        endpoint = f"https://api.github.com/repos/{self.owner}/{self.repo}/branches"

        res = requests.get(endpoint, auth=(self.username, self.token))
        res = res.json()  # OP HET MOMENT PAKT IE 100 COMMITS

        return len(res)

    def get_loc_per_commit(self):

        """

        Get list of commits from API
        Use scraper to get data

        only scrape repos with 50+ commits, --bc less than that doesn't represent code projects that work together (via Git)
        random sample 100 commits (when repo has 100+ commits) for locpc --bc we are limited in computational power



        """
        endpoint_code_frequency = f"{self.api_base_url}/stats/code_frequency"
        endpoint_participation = f"{self.api_base_url}/stats/participation"
        endpoint_contributors = f"{self.api_base_url}/stats/contributors"
        endpoint_commit_activity = f"{self.api_base_url}/stats/commit_activity"

        try:
            res_participation = requests.get(
                endpoint_participation,
                headers={
                    "User-Agent": GET_UA(),
                    "accept": "application/vnd.github.v3+json",
                },
                auth=self.auth,
            ).json()
            res_contributors = requests.get(
                endpoint_contributors,
                headers={
                    "User-Agent": GET_UA(),
                    "accept": "application/vnd.github.v3+json",
                },
                auth=self.auth,
            ).json()
            res_code_freq = requests.get(
                endpoint_code_frequency,
                headers={
                    "User-Agent": GET_UA(),
                    "accept": "application/vnd.github.v3+json",
                },
                auth=self.auth,
            ).json()
            res_commit_activity = requests.get(
                endpoint_commit_activity,
                headers={
                    "User-Agent": GET_UA(),
                    "accept": "application/vnd.github.v3+json",
                },
                auth=self.auth,
            ).json()

            # print(sum(res_participation["all"]))
            print(len(res_commit_activity))

            # for c in res_contributors:
            #     print(c["author"]["login"])
        except Exception as e:
            print("Error:", str(e))

        # return

    def get_loc_per_commit_slow(self) -> int:

        """

        Get list of commits from API
        Use scraper to get data

        only scrape repos with 50+ commits, --bc less than that doesn't represent code projects that work together (via Git)
        random sample 100 commits (when repo has 100+ commits) for locpc --bc we are limited in computational power



        """

        endpoint = f"https://api.github.com/repos/{self.owner}/{self.repo}/commits?per_page=100&anon=1"
        content, soup, ct1 = bs_parse_url(
            endpoint, auth=(self.username, self.token), accept="application/json"
        )  # OP HET MOMENT PAKT IE 100 COMMITS

        try:
            json_content = json.loads(content)
        except Exception as e:
            print("Error:", str(e))
            print("MY ERROR NOTICE: content is not JSON")

        commits = []
        added_lines = []
        deleted_lines = []

        for jc in json_content:
            commit_url = jc["commit"]["url"]
            suffix = commit_url.split("/")[-1]
            commits.append(suffix)

        for commit in commits:
            scraping_url = f"{self.repo_link}/commit/{commit}"
            c, soepie, ct2 = bs_parse_url(scraping_url)
            div = soepie.find_all(class_="toc-diff-stats").pop()
            strong1 = div.strong.string
            strong2 = div.strong.next_sibling.next_sibling.string
            added_lines.append(strong1.split(" ")[0])
            deleted_lines.append(strong2.split(" ")[0])

        added_lines = list(map(int, added_lines))
        deleted_lines = list(map(int, deleted_lines))

        print(f"added: {added_lines}")
        print(f"deleted: {deleted_lines}")

        mean_added_locpc = sum(added_lines) / len(commit)
        mean_deleted_locpc = sum(deleted_lines) / len(commit)

        return mean_added_locpc - mean_deleted_locpc

    def get_loc_per_week(self) -> int:

        """

        Get list of commits from API
        Use scraper to get data

        only scrape repos with 50+ commits, --bc less than that doesn't represent code projects that work together (via Git)
        random sample 100 commits (when repo has 100+ commits) for locpc --bc we are limited in computational power



        """

        endpoint = (
            f"https://github.com/{self.owner}/{self.repo}/graphs/code-frequency-data"
        )
        accept = "application/json"
        headers = {"User-Agent": GET_UA(), "Accept": accept}
        auth = (self.username, self.token)

        endpoint_code_frequency = f"{self.api_base_url}/stats/code_frequency"

        try:
            res = requests.get(endpoint, headers=headers, auth=self.auth)

            # res = requests.get(
            #     endpoint_code_frequency,
            #     headers={
            #         "User-Agent": GET_UA(),
            #         "accept": "application/vnd.github.v3+json",
            #     },
            #     auth=(self.username, self.token),
            # )

            weekly_changes = res.json()
        except Exception as e:
            print("Error:", str(e))

        added_lines = []
        deleted_lines = []
        for changes in weekly_changes:
            if changes[1] != 0:
                added_lines.append(changes[1])
                deleted_lines.append(changes[2])
            else:
                if changes[2] != 0:
                    added_lines.append(changes[1])
                    deleted_lines.append(changes[2])
                else:
                    pass  # of kan dit gwn weg?

        # print(f"added: {added_lines}")
        # print(f"deleted: {deleted_lines}")

        added_deleted_len = len(added_lines) - len(deleted_lines)

        if added_deleted_len == 0:
            # mean_added_loc = st.mean(added_lines)
            # mean_deleted_loc = st.mean(deleted_lines)
            # stdev_deleted_loc = st.stdev(added_lines)
            # stdev_added_loc = st.stdev(deleted_lines)
            print(f"Fetched weekly additions/deletions for {self.repo}")
        elif added_deleted_len > 0:
            print(
                f"Error: 'added_lines' is a longer list than 'deleted_lines', {added_deleted_len} to be specific"
            )
        else:
            print(
                f"Error: 'added_lines' is a shorter list than 'deleted_lines', {added_deleted_len} to be specific"
            )

        return added_lines, deleted_lines


NHapiTools_repo = Repository(
    repo_link="https://github.com/dib0/NHapiTools",
    lines_of_code=670090,
    username="",
    token="",
)

# loc = NHapiTools_repo.get_loc_per_week()
# print(loc)
locpc = NHapiTools_repo.get_loc_per_commit()
print(locpc)
# col = NHapiTools_repo.get_num_collaborators()
# print(col)
