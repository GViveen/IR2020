import os
from subprocess import call
from subprocess import Popen

# subprocess.call(['python', 'exampleScripts.py', somescript_arg1, somescript_val1,...]).

Popen(['nohup', 'python', 'reranker.py', "d-core-k", "67", "d-core-l", "20", "output", "output_6720.txt"],
      stdout=open('null1', 'w'),
      stderr=open('logfile.log', 'a'),
      start_new_session=True)

Popen(['nohup', 'python', 'reranker.py', "d-core-k", "67", "d-core-l", "33", "output_6750.txt"],
      stdout=open('null2', 'w'),
      stderr=open('logfile.log', 'a'),
      start_new_session=True)

Popen(['nohup', 'python', 'reranker.py', "d-core-k", "67", "d-core-l", "50", "output_6767.txt"],
      stdout=open('null3', 'w'),
      stderr=open('logfile.log', 'a'),
      start_new_session=True)

Popen(['nohup', 'python', 'reranker.py', "d-core-k", "50", "d-core-l", "20", "output", "output_6720.txt"],
      stdout=open('null1', 'w'),
      stderr=open('logfile.log', 'a'),
      start_new_session=True)

Popen(['nohup', 'python', 'reranker.py', "d-core-k", "50", "d-core-l", "33", "output_6750.txt"],
      stdout=open('null2', 'w'),
      stderr=open('logfile.log', 'a'),
      start_new_session=True)

Popen(['nohup', 'python', 'reranker.py', "d-core-k", "50", "d-core-l", "50", "output_6767.txt"],
      stdout=open('null3', 'w'),
      stderr=open('logfile.log', 'a'),
      start_new_session=True)

Popen(['nohup', 'python', 'reranker.py', "d-core-k", "33", "d-core-l", "20", "output", "output_6720.txt"],
      stdout=open('null1', 'w'),
      stderr=open('logfile.log', 'a'),
      start_new_session=True)

Popen(['nohup', 'python', 'reranker.py', "d-core-k", "33", "d-core-l", "33", "output_6750.txt"],
      stdout=open('null2', 'w'),
      stderr=open('logfile.log', 'a'),
      start_new_session=True)

Popen(['nohup', 'python', 'reranker.py', "d-core-k", "33", "d-core-l", "50", "output_6767.txt"],
      stdout=open('null3', 'w'),
      stderr=open('logfile.log', 'a'),
      start_new_session=True)