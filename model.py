def insert_game(cursor, game):
  cursor.execute('INSERT INTO games VALUES (?,?,?)', game)

def insert_match(cursor, match):
  cursor.execute('INSERT INTO matches VALUES (?,?,?,?,?,?)', match)

def update_match_date(cursor, match_rowid, date):
  cursor.execute('UPDATE matches SET date=? WHERE rowid=?', [date, match_rowid])

def create_db(cursor):
  cursor.execute('''CREATE TABLE matches
    (player1 text, player2 text, outcome integer, date text, player1race text, player2race text)''')
  cursor.execute('''CREATE TABLE games
    (map text, outcome int, match_id int, FOREIGN KEY(match_id) REFERENCES matches(rowid));''')

def delete_db(cursor):
  cursor.execute('DROP TABLE games')
  cursor.execute('DROP TABLE matches')