import secrets
import string

res = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(128))
print(res.encode())
s = "vale"
t = ""
for i in range(len(s)):
    t = t + chr(ord(s[i]) + 1)
val = res[0:63]
end = len(s)
print(val + t.upper() + str(end))