import hashlib

m2 = hashlib.md5()
m2.update('hello'.encode('utf-8'))
print(m2.hexdigest())