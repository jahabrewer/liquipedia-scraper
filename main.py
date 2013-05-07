from scraper import scrape
import string
import re
import sqlite3
from model import *

def handle_match_list(cursor, match_list):
  match_numbers = [re.search("\d+", i).group() for i in match_list.keys() if re.match("^match\d+$", i)]
  for match_number in match_numbers:
    match = match_list["match" + match_number]['MatchMaps']
    player1 = match['player1']
    player2 = match['player2']
    if match['winner'] == 'draw':
      outcome = 0
    else:
      outcome = int(match['winner'])
    if 'date' in match:
      date = match['date']
    else:
      date = None
    player1race = match['player1race']
    player2race = match['player2race']
    insert_match(cursor, (player1, player2, outcome, date, player1race, player2race))
    handle_games(cursor, match, cursor.lastrowid)

def handle_games(cursor, match, match_id):
  game_numbers = [re.search("\d+", i).group() for i in match.keys() if re.match("^map\d+$", i)]    
  for game_number in game_numbers:
    map_name_key = "map%s" % game_number
    map_outcome_key = map_name_key + "win"
    map_name = match[map_name_key]
    map_outcome = match[map_outcome_key]
    # print (map_name, map_outcome, match_id)
    insert_game(cursor, (map_name, map_outcome, match_id))

pages = [
  "2013_MLG_Winter_Championship/Showdowns",
  "2013_DreamHack_Open/Stockholm/Group_Stage_1",
  "2013_DreamHack_Open/Stockholm/Group_Stage_2",
  "2013_DreamHack_Open/Stockholm/Group_Stage_3",
  "2013_Ritmix_Russian_StarCraft_II_League_Season_4",
]
pages_normalized = [re.sub('[_]', '%20', text) for text in pages]
pages_joined = string.join(pages_normalized, '|')
api = "http://wiki.teamliquid.net/starcraft2/api.php?format=json&action=query&titles={0}&prop=revisions&rvprop=content"
trees = scrape(api, pages_joined)

conn = sqlite3.connect('matches.db')
cursor = conn.cursor()
delete_db(cursor)
create_db(cursor)
conn.commit()

for tree in trees:
  handle_match_list(cursor, tree["MatchList"])

conn.commit()
conn.close()