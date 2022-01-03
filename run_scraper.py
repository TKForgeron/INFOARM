import signal
import sys
from get_repo_urls import get_repo_urls
from get_website import get_repos_list, checkIfCorrectProjectUrl
from repository import Repository
import threading
import time
import pandas as pd
from print_launch import print_launch


SCRAPED_REPOS = []
MAX_INDEX = 0
FINISHED_INDEXES = 0
STARTED_INDEX = None
def on_interupt(sig, frame):
  global SCRAPED_REPOS
  print('You pressed Ctrl+C!')
  df = pd.DataFrame(SCRAPED_REPOS)
  print(df)
  df.to_csv('out {}-{}.csv'.format(
    str(STARTED_INDEX),
    str(FINISHED_INDEXES)
  ))
  sys.exit(0)

def thread_function(offset) -> list[dict]:
  start = time.time()
  global SCRAPED_REPOS
  global FINISHED_INDEXES
  repos = get_repos_list(offset)
  # print(repos)
  result = []
  for repo in repos:
    # print('starting mining')
    urls = get_repo_urls(repo['project_name'])
    if urls == False:
      print('[ERROR] - quitted thread')
      return 
    correct_url = None
    for index, url in enumerate(urls):
      if checkIfCorrectProjectUrl(url, repo['uuid']):
        correct_url = url
      if (index > 19):
        print('[warning] - too many tries to find repo with name {} '.format(repo['project_name']))
        break
    if correct_url == None:
      print('[warning][not_found] - repo with project_name {} not found, skipping'.format(repo['project_name']))
      continue
    repository = Repository(correct_url, repo)
    repo_result = repository.get_all_data_as_dict()
    if repo_result == False:
      print('[warning][not_comply] - repo with project_name {} skipped bc repository.py said to drop this'.format(repo['project_name']))
      continue
    print('[succes] - succesfully added repo with project_name {} to temp list'.format(repo['project_name']))
    result.append(repo)

  df = pd.DataFrame(result)
  df.to_csv('out/out {}-{}.csv'.format(
    str(offset),
    str(offset + 10)
  ))
  print('[!SUCCES!] - just added {} repos, thread took {} seconds'.format(str(len(result)), str(time.time() - start)))
  SCRAPED_REPOS = SCRAPED_REPOS + result
  FINISHED_INDEXES = max(FINISHED_INDEXES, offset + 10)
  return result
    
def start_thread() -> threading.Thread:
  global MAX_INDEX
  t = threading.Thread(target=thread_function, args=(MAX_INDEX,))
  t.start()
  MAX_INDEX += 10
  return t


def start_threads(numTreads: int = 1, start_offset: int = 0):
  global STARTED_INDEX
  global MAX_INDEX
  STARTED_INDEX = start_offset
  MAX_INDEX = start_offset
  threads = []
  for i in range(0, numTreads):
    # print('started thread')
    t = start_thread()
    threads.append(
      t
    )
  # print('started all')
  print_launch()
  add_threads = []
  finished_indexes = []
  while True:
    for i, t in enumerate(threads):
      if t == False: continue
      # print(t.is_alive())
      if t.is_alive() == False:
        new_t = start_thread()
        add_threads.append(
          new_t
        )
        finished_indexes.append(i)
        print('Thread finished')
      
    threads = threads + add_threads

    for index in finished_indexes:
      threads[index] = False

    add_threads = []
    finished_indexes = []
    
    time.sleep(10)
    



signal.signal(signal.SIGINT, on_interupt)
print('Press Ctrl+C')
# signal.pause()

if __name__ == '__main__': 
  start_threads(2)