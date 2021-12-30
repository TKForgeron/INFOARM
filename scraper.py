from dotenv import load_dotenv
import os
from time import time
from repository import Repository

# GLOBALS
load_dotenv()
USERNAME = os.getenv("GITHUB_USERNAME")
TOKEN = os.getenv("GITHUB_TOKEN")

start_time = time()

NHapiTools_repo = Repository(
    repo_link="https://github.com/dib0/NHapiTools",
    lines_of_code=670090,
    username=USERNAME,
    token=TOKEN,
)
INFOARM_repo = Repository("https://github.com/TKForgeron/INFOARM", USERNAME, TOKEN)
kubernetes_repo = Repository(
    "https://github.com/kubernetes/kubernetes", USERNAME, TOKEN
)

print(f"\n{time() - start_time} seconds")


def get_repo_stats(url: str, loc: int):
    repo = Repository(url, loc, USERNAME, TOKEN)
    if repo.drop_this_repo:
        return None
    else:
        locpc = repo.get_loc_per_commit()
        num_col = repo.get_num_collaborators()
        num_bran = repo.get_num_branches()
