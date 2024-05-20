"""
File name: md5gen.py
Created on May 17 2024:
@author: <Benjamin Nolan>
Description: Generating an MD5 hash on entered text.
"""
from hashlib import md5
key = input('Enter password to hash: ').encode()
print(f'Your Key: {key}')

encKey = md5(key).hexdigest()
print(f'Your md5 hash: {encKey}')