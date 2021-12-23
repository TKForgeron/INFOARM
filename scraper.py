import requests
import pandas as pd

class Repository:

    def __init__(self, repo_link: str, username: str, token: str) -> None:
        self.repo_link = repo_link
        self.username = username
        self.token = token
    
    def get_num_collaborators(self):

        """

        Using API instead of scraper as the github console only shows the recent / top committers
    

        """

        collaborators = []
        

        endpoint = f"https://api.github.com/repos/{self.repo_link.split('/')[-2]}/{self.repo_link.split('/')[-1]}/contributors?per_page=100&anon=1"
        response = requests.get(endpoint, auth=(self.username, self.token))
        collaborators += response.json()
        while 'next' in response.links:
            endpoint = response.links['next']['url']
            print(f"Getting next url {endpoint}")
            response = requests.get(endpoint, auth=(self.username, self.token))
            collaborators += response.json()

        return collaborators

    def get_loc(self) -> int:

        """

        Get list of commits from API
        Use scraper to get data


        """

        endpoint = f"https://api.github.com/repos/{self.repo_link.split('/')[-2]}/{self.repo_link.split('/')[-1]}/commits?per_page=100&anon=1"
        response = requests.get(endpoint, auth=(self.username, self.token))
        return response.json()



kubernetes_repo = Repository(repo_link = "https://github.com/kubernetes/kubernetes", username="", token = "")

# contributors = kubernetes_repo.get_num_collaborators()
# df = pd.DataFrame(contributors)
# df.to_csv('contributors.csv', index=False)


loc = kubernetes_repo.get_loc()
print(loc[0]['commit']['tree'].keys())
