import pandas as pd
from dotenv import load_dotenv
import os
from time import time

from pandas.core.frame import DataFrame
from repository import Repository

# GLOBALS
load_dotenv()
USERNAME = os.getenv("GITHUB_USERNAME")
TOKEN = os.getenv("GITHUB_TOKEN")


def get_repo_stats(url: str, loc: int, qscore: float) -> dict[str, float]:
    repo = Repository(url, loc, USERNAME, TOKEN)
    if repo.drop_this_repo:
        return {}
    else:
        num_col = repo.get_num_collaborators()
        num_bran = repo.get_num_branches()
        (
            mean_additions_pcommit,
            mean_deletions_pcommit,
            stdev_additions_pcommit,
            stdev_deletions_pcommit,
        ) = repo.get_loc_per_commit()
    return {
        "qscore": qscore,
        "loc": loc,
        "num_col": num_col,
        "num_bran": num_bran,
        "mean_additions_pcommit": mean_additions_pcommit,
        "mean_deletions_pcommit": mean_deletions_pcommit,
        "stdev_additions_pcommit": stdev_additions_pcommit,
        "stdev_deletions_pcommit": stdev_deletions_pcommit,
    }


def collect_all_repo_stats(repos) -> pd.DataFrame:
    all_stats = []
    for repo in repos:
        url = repo[0]
        loc = repo[1]
        qscore = repo[2]
        repo_stats = get_repo_stats(url, loc, qscore)
        all_stats.append(repo_stats)

    return pd.DataFrame(all_stats)


start_time = time()

repo_stats = collect_all_repo_stats(
    [
        # ("https://github.com/dib0/NHapiTools", 670090, 0.71),
        # ("https://github.com/itsaky/AnimatedTextView", 136217, 1.38),
        ("https://github.com/TKForgeron/INFOARM", 136217, 234),
    ]
)
print(repo_stats)

print(f"\n{time() - start_time} seconds")
