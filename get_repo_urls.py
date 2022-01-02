import requests

def get_repo_url(reponame):
  url = "https://api.github.com/search/repositories?q=" + reponame 
  response = requests.get(url).json()
  for item in response['items']:
      repo_url = item.get('html_url')
      print(repo_url)
  
get_repo_url('INFOARM')