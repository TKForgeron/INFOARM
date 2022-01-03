import requests

MIN_LOC = "232"
MAX_LOC = "234567"

USER_NAME = "m.defroe@students.uu.nl"
API_KEY = "ce6c600c66706dcb2df7b8066a1b1a92867fccb1"

def get_repos_list(offset: int):
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'username': USER_NAME,
    'Authorization': 'Token ' + API_KEY,
  }

  data = {
    'min_loc': str(MIN_LOC),
    'max_loc': str(MAX_LOC),
    'start_index': str(offset),
  }

  url = "https://qscored.com/api/search_project_by_quality/"

  res = requests.post(url=url, data=data, headers=headers, )
  data = res.json()
  return data

def checkIfCorrectProjectUrl(repo_link: str, uuid: str):
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'username': USER_NAME,
    'Authorization': 'Token ' + API_KEY,
  }

  data = {
    'repo_link': repo_link,
    'start_index': 0
  }

  url = "https://qscored.com/api/search_project/"

  res = requests.post(url=url, data=data, headers=headers, )
  data = res.json()
  if len(data) == 0:
    return False
  if isinstance(data, dict) and data['reason']:
    # this case there is an error
    return False
  if data[0]['uuid'] == uuid:
    return True
  return False




