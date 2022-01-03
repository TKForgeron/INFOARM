from typing import Dict
import numpy as np
from requests.auth import HTTPBasicAuth
import statistics as st
import random
import requests
import pandas as pd
from config import config

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


class Repository:
    def __init__(
        self,
        repo_link: str,
        q_scored_data: dict = {}
    ) -> None:
        self.repo_link = repo_link
        splitted_repo_link = repo_link.split("/")
        self.owner = splitted_repo_link[-2]
        self.repo = splitted_repo_link[-1]
        self.api_base_url = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        self.auth = HTTPBasicAuth(config['username'], config['token'])
        self.weekly_commits = None
        self.project_name = q_scored_data["project_name"]
        self.score = q_scored_data["score"]
        self.lang = q_scored_data["lang"]
        self.lines_of_code = q_scored_data["loc"]
        # checking whether repo has released anything
        self.drop_this_repo = False
        if self.__get_num_releases():
            commit_condition = len(
                list(filter(lambda x: x != 0, self.__get_commits_per_week()))
            )

            if commit_condition < 2:  # repos should have at least 2 weeks of commits
                self.drop_this_repo = True
            elif (
                sum(self.__get_commits_per_week()) < 7
            ):  # implementing total commit count threshold of 7
                self.drop_this_repo = True
        else:
            self.drop_this_repo = True

    # IF THERE IS TIME, ADD FUCNTION THAT FETCHES AMOUNT OF COMMITS
    # THAT COLLABORATORS OF THIS REPO HAVE MADE TO OTHER REPOS WHILE ACTIVE ON THIS REPO

    def get_all_data_as_dict(self) -> dict or bool:
        if self.drop_this_repo:
            return False
        return {
            "project_name": self.project_name,
            "repo_link": self.repo_link,
            "score": self.score,
            "lang": self.lang,
            "lines_of_code": self.lines_of_code,
            "num_collaborators": self.get_num_collaborators(),
            "num_branches": self.get_num_branches(),
            "loc_per_commit": self.get_loc_per_commit(),
        }

    def get_num_collaborators(self) -> int:

        """

        Using API instead of scraper as the github console only shows the recent / top committers


        """

        collaborators = []

        endpoint = f"{self.api_base_url}/contributors?per_page=100"
        response = requests.get(endpoint, auth=self.auth)
        collaborators += response.json()
        while "next" in response.links:
            endpoint = response.links["next"]["url"]
            # print(f"Getting next url {endpoint}")
            response = requests.get(endpoint, auth=self.auth)
            collaborators += response.json()

        return len(collaborators)

    def get_num_branches(self) -> int:
        """

        Request all branches in repo from GitHub API and returning one of 3 categories
        1 = one branch 
        2 = two or three branches
        3 = more than four branches

        """
        endpoint = f"https://api.github.com/repos/{self.owner}/{self.repo}/branches"

        res = requests.get(endpoint, auth=self.auth)
        res = res.json()
        res = len(res)
        if res == 1:
            return 1
        elif res == 2 or res == 3:
            return 2
        else:
            return 3

    def get_loc_per_commit(self):
        add_lines, del_lines = self.__get_loc_per_week()
        commits_pweek = self.__get_commits_per_week()

        if len(del_lines) == len(commits_pweek) and len(add_lines) == len(del_lines):
            # weet ff niet hoe ik dit doe in NumPy
            # deleting all weeks where commit_count==0 (to prevent division by 0 later on...)
            add_del_comm_pweek = pd.DataFrame(
                np.array([add_lines, del_lines, commits_pweek]).T
            )
            index_to_be_dropped = add_del_comm_pweek[add_del_comm_pweek[2] == 0].index
            add_del_comm_pweek = add_del_comm_pweek.drop(index_to_be_dropped)

            # back to numpy for speed
            add_del_comm_pweek = add_del_comm_pweek.to_numpy().T
            add_lines = add_del_comm_pweek[0]
            del_lines = add_del_comm_pweek[1]
            commits_pweek = add_del_comm_pweek[2]

            # get avg additions/deletions per commit per week
            avg_additions_pcommit_pweek = np.divide(add_lines, commits_pweek)
            avg_deletions_pcommit_pweek = np.divide(del_lines, commits_pweek)

            # calculate statistics for additions/deletions per commit per week
            mean_additions_pcommit = st.mean(avg_additions_pcommit_pweek)
            mean_deletions_pcommit = st.mean(avg_deletions_pcommit_pweek)
            stdev_additions_pcommit = st.stdev(avg_additions_pcommit_pweek)
            stdev_deletions_pcommit = st.stdev(avg_deletions_pcommit_pweek)

        # elif len(del_lines) > len(commits_pweek):
        #     print("len(del_lines) > len(commits_pweek)")
        # elif len(add_lines) > len(commits_pweek):
        #     print("len(add_lines) > len(commits_pweek)")
        # elif len(add_lines) < len(commits_pweek):
        #     print("len(add_lines) < len(commits_pweek)")
        # elif len(del_lines) < len(commits_pweek):
        #     print("len(del_lines) < len(commits_pweek)")
        # else:
        #     print("is this even possible?")

        return (
            mean_additions_pcommit,
            mean_deletions_pcommit,
            stdev_additions_pcommit,
            stdev_deletions_pcommit,
        )

    def __get_commits_per_week(self) -> list[int]:
        # python 3.8 and earlier: List[int] (and import List from typing module)
        """

        Get list of commits from API
        Use scraper to get data

        only scrape repos with 50+ commits, --bc less than that doesn't represent code projects that work together (via Git)
        random sample 100 commits (when repo has 100+ commits) for locpc --bc we are limited in computational power



        """

        if self.weekly_commits:
            return self.weekly_commits

        endpoint_contributors = f"{self.api_base_url}/stats/contributors"

        weekly_commits = ["Nothing Found..."]

        try:
            res_contributors = requests.get(
                endpoint_contributors,
                headers={
                    "User-Agent": GET_UA(),
                    "accept": "application/vnd.github.v3+json",
                },
                auth=self.auth,
            ).json()

            weekly_commits = []
            for rc in res_contributors:
                contr_weekly_commits = []

                for week in rc["weeks"]:
                    contr_weekly_commits.append(week["c"])

                weekly_commits.append(contr_weekly_commits)

            weekly_commits = np.sum(np.array(weekly_commits), 0)
            # print(f"Fetched weekly commits ({sum(weekly_commits)}) for {self.repo}")

        except Exception as e:
            print("Error:", str(e))

        self.weekly_commits = list(weekly_commits)

        return self.weekly_commits

    def __get_loc_per_week(self) -> int:

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

        try:
            res = requests.get(endpoint, headers=headers, auth=self.auth)

            # IF ENDPOINT ABOVE LIMITS REQUESTS LIMITINGLY, USE THE FOLLOWING INSTEAD:
            # endpoint_code_frequency = f"{self.api_base_url}/stats/code_frequency"
            # res = requests.get(
            #     endpoint_code_frequency,
            #     headers={
            #         "User-Agent": GET_UA(),
            #         "accept": "application/vnd.github.v3+json",
            #     },
            #     auth=self.auth,
            # )

            weekly_changes = res.json()
        except Exception as e:
            print("Error:", str(e))

        added_lines = []
        deleted_lines = []
        for changes in weekly_changes:
            added_lines.append(changes[1])
            deleted_lines.append(changes[2])

        added_deleted_len = len(added_lines) - len(deleted_lines)

        if added_deleted_len == 0:
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

    def __get_num_releases(self):
        """

        We only analyze projects that release their code (via Git)


        """

        endpoint = f"https://api.github.com/repos/{self.repo_link.split('/')[-2]}/{self.repo_link.split('/')[-1]}/releases?per_page=100"
        response = requests.get(endpoint, auth=self.auth).json()
        num_releases = len(response)
        # ONLY FIRST 100 RELEASES ARE FETCHED!!!!
        return num_releases
