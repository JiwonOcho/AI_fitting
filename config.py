from key.DBinfo import SEEOT_DB

db = SEEOT_DB
DB_URL = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"
