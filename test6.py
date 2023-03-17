import secrets
import string

res = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(128))
