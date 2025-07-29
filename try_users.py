# try_users.py
from crud import get_users, create_user

create_user("ziad", "ziad@example.com")
users = get_users()
for user in users:
    print(user)
