import bcrypt


def hashing(string):
    return bcrypt.hashpw(string.encode('utf-8'), bcrypt.gensalt())


def compare_hashes(password, user_password):
    return bcrypt.checkpw(password, user_password)
