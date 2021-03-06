import sqlite3, hashlib, os, zlib, json

basedir = os.path.abspath(os.path.dirname(__file__))
global f
f = basedir+"/../data/lens.db"

# Encrypt password - Returns SHA256
def encrypt_password(password):
    encrypted = hashlib.sha256(password).hexdigest()
    return encrypted

# Login - Returns true if successful, false otherwise
def login(username, password):
    db = sqlite3.connect(f)
    c = db.cursor()
    st = False
    c.execute("SELECT username, password FROM users WHERE username = '%s'" % (username))
    for account in c:
        u = account[0]
        p = account[1]
        # Check if usernames and encrypted passwords match
        if username == u and encrypt_password(password) == p:
            st = True
    db.commit()
    db.close()
    return st

# Create account - Returns true if successful, false otherwise
def create_account(username, password):
    db = sqlite3.connect(f)
    c = db.cursor()
    st = False
    if not does_username_exist(username):
        # Add user to accounts table
        c.execute("SELECT * FROM users ORDER BY id DESC LIMIT 1")
        user_id = int(c.fetchone()[0]) + 1
        c.execute("INSERT INTO users VALUES(%d, '%s', '%s')" % (user_id, username, encrypt_password(password)))
        st = True
    db.commit()
    db.close()    
    return st

def does_username_exist(username):
    db = sqlite3.connect(f)
    c = db.cursor()
    c.execute("SELECT username FROM users WHERE username = '%s'" % (username))
    st = False
    for account in c:
        st = True
    db.commit()
    db.close()
    return st

def change_password(username, old_password, new_password):
    db = sqlite3.connect(f)
    c = db.cursor()
    st = False
    if login(username, old_password):
        c.execute("UPDATE users SET password='%s' WHERE username = '%s' AND password = '%s'" % (encrypt(new_password), username, old_password))
        st = True
    db.commit()
    db.close()
    return st

def does_hash_exist(hashcode):
    db = sqlite3.connect(f)
    c = db.cursor()
    #checks if hash already in use
    st = c.execute("SELECT 1 FROM sessions WHERE hash_id='%s'" % (hashcode)).fetchall() != []
    db.commit()
    db.close()
    return st

def create_new_hash():
    new_hash = zlib.adler32(os.urandom(10))
    while(does_hash_exist(new_hash)):
        new_hash = zlib.adler32(os.urandom(10))
    return new_hash

def create_session(username, o_dist, o_height, focus, sign):
    db = sqlite3.connect(f)
    c = db.cursor()
    #assumes user exists
    exe = "INSERT INTO sessions VALUES('%s', (SELECT id FROM users WHERE username = '%s'), %s, %s, %s, %s)" % (create_new_hash(), username, o_dist, o_height, focus, sign)
    print exe
    c.execute(exe)
    db.commit()
    db.close()

def get_session(hashcode):
    db = sqlite3.connect(f)
    c = db.cursor()
    info = {}
    raw = c.execute("SELECT * FROM sessions WHERE hash_id = '%s'" % hashcode).fetchall()[0]
    info["hash"] = raw[0]
    info["id"] = raw[1]
    info["o_dis"] = raw[2]
    info["o_height"] = raw[3]
    info["focus"] = raw[4]
    info["sign"] = raw[5]
    print info
    db.commit()
    db.close()
    return info

def get_owned_sessions(username):
    db = sqlite3.connect(f)
    c = db.cursor()
    info = [hash_id[0] for hash_id in c.execute("SELECT hash_id FROM sessions WHERE id = (SELECT id FROM users WHERE username = '%s')" % (username)).fetchall()]
    db.commit()
    db.close()
    return info

def update_session(hashcode, o_dist, o_height, focus, sign):
    db = sqlite3.connect(f)
    c = db.cursor()
    exe = "UPDATE sessions SET o_dist=%s, o_height=%s, focus=%s, sign=%s WHERE hash_id=%s" % (o_dist, o_height, focus, sign, hashcode)
    print exe
    c.execute(exe)
    db.commit()
    db.close()

def check_hash(username, hashcode):
    db = sqlite3.connect(f)
    c = db.cursor()
    st = c.execute("SELECT 1 FROM sessions WHERE id = (SELECT id FROM users WHERE username = '%s') and hash_id = '%s'" % (username, hashcode)).fetchall() != []
    db.commit()
    db.close()
    return st

def get_user_sessions_details(username):
    db = sqlite3.connect(f)
    c = db.cursor()
    details = c.execute("SELECT hash_id, focus, o_height, o_dist, sign FROM sessions WHERE id = (SELECT id FROM users WHERE username = '%s')" % (username)).fetchall()
    print details
    db.commit()
    db.close()
    return details
    
def get_sessions_details(sessions):
    db = sqlite3.connect(f)
    c = db.cursor()
    print("SELECT * FROM sessions WHERE hash_id in ('%s')" % (",".join(str(e) for e in sessions)))
    details = c.execute("SELECT hash_id, focus, o_height, o_dist, sign FROM sessions WHERE hash_id in (%s)" % (",".join(str(e) for e in sessions))).fetchall()
    print details
    db.commit()
    db.close()
    return details

#get_user_sessions_details("admin")
#get_sessions_details([414581764, 322438084])

#create_session("admin", 12, 12, "Null", 0)
#print(get_session(393151666))
