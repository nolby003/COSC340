#!/usr/bin/env python

import socket

host='127.0.0.1'
port=65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
      s.connect((host, port))
      inp = input('Client: ')
      x = inp.split()
      cmd = x[0].upper()
      val = x[1].lower()
      if cmd == 'LOGIN':
          s.sendall(cmd.encode())
          data = s.recv(1024).decode()
      elif cmd == 'COMPOSE':
          cmd2 = input('Client: ')
          s.sendall(cmd+cmd2.encode())
          data = s.recv(1024).decode()
      # note: an int it coming through as a string from server
      print(f'Server: {data!r}')
