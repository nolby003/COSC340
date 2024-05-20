from hashlib import md5

key = b'5678'
print(key)

encKey = md5(key).hexdigest()
print(encKey)
