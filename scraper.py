import requests
import pandas as pd
from typing import List, Tuple
from bs4 import BeautifulSoup
from functools import partial


class Repository:
    def __init__(self, repo_link: str, username: str, token: str) -> None:
        self.repo_link = repo_link
        self.username = username
        self.token = token
        splitted_repo_link = repo_link.split('/')
        self.owner = splitted_repo_link[-2]
        self.repo = splitted_repo_link[-1]



    def get_num_collaborators(self):

        """

        Using API instead of scraper as the github console only shows the recent / top committers


        """

        collaborators = []

        endpoint = f"https://api.github.com/repos/{self.owner}/{self.repo}/contributors?per_page=100&anon=1"
        response = requests.get(endpoint, auth=(self.username, self.token))
        collaborators += response.json()
        while "next" in response.links:
            endpoint = response.links["next"]["url"]
            print(f"Getting next url {endpoint}")
            response = requests.get(endpoint, auth=(self.username, self.token))
            collaborators += response.json()

        return collaborators

    def get_num_branches(self) -> int:
        """
        Request all branches in repo from GitHub API and returning number of branches
        """
        endpoint = f"https://api.github.com/repos/{self.owner}/{self.repo}/branches"

        res = requests.get(endpoint, auth=(self.username, self.token))
        res = res.json()  # OP HET MOMENT PAKT IE 100 COMMITS

        return len(res)


    def get_locpc(self) -> int:

        """

        Get list of commits from API
        Use scraper to get data


        """
        bs_parse = partial(BeautifulSoup, features="lxml")

        endpoint = f"https://api.github.com/repos/{self.owner}/{self.repo}/commits?per_page=100&anon=1"

        res = requests.get(endpoint, auth=(self.username, self.token))
        res = res.json()  # OP HET MOMENT PAKT IE 100 COMMITS

        commits = []
        added_lines = []
        deleted_lines = []

        for r in res:
            commit_url = r["commit"]["url"]
            suffix = commit_url.split("/")[-1]
            commits.append(suffix)

        for commit in commits:
            scraping_url = f"{self.repo_link}/commit/{commit}"
            bs_res = requests.get(scraping_url)
            bs_parse = partial(
                BeautifulSoup, features="lxml"
            )  # pure flex met partial functie
            doc = bs_parse(bs_res.text)
            div = doc.find_all(class_="toc-diff-stats").pop()
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
