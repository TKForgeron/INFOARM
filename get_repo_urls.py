import requests
from config import config
from requests.auth import HTTPBasicAuth


def get_repo_urls(reponame):
  url = "https://api.github.com/search/repositories?q=" + reponame 
  auth = HTTPBasicAuth(config['username'], config['token'])
  response = requests.get(url, auth=auth).json()
  result = []
  # print(response)
  if 'items' not in response:
    print('ERROR! Item not in reponse')
    print(response)
    return False
  for item in response['items']:
      repo_url = item.get('html_url')
      result.append(repo_url)
  return result
  