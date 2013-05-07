from parser import lexer
from parser import yaccer
import re
import sqlite3
from model import *
import pprint

def default_round_names(num_rounds):
  all_names = [
    'Round of 64',
    'Round of 32',
    'Round of 16',
    'Quarterfinals',
    'Semifinals',
    'Finals',
  ]
  return all_names[6-num_rounds:]

def strip_comments(text):
  return re.sub('<!--[^(-->)]*-->', '', text)

def decode_template_name(name):
  match = re.match(r'^(?P<player_count>16|32|64)(?P<style>SE|DE)Bracket', name)
  return match.groupdict()

def handle_one_round(cursor, tree, round_number, total_rounds):
  round_name_key = "R%s" % round_number
  if round_name_key in tree:
    round_name = tree[round_name_key]
  else:
    round_name = default_round_names(total_rounds)[round_number]

  num_matches = 2**(total_rounds - round_number)

  for match_number in range(1, num_matches+1):
    box_type = 'D' if round_number == 1 else 'W'
    player1_base_key = "R{0}{1}{2}".format(round_number, box_type, 2*match_number-1)
    player2_base_key = "R{0}{1}{2}".format(round_number, box_type, 2*match_number)
    
    player1_name = tree[player1_base_key]
    player1_race = tree[player1_base_key+"race"]
    player1_score = tree[player1_base_key+"score"]
    player1_win = tree[player1_base_key+"win"]
    player2_name = tree[player2_base_key]
    player2_race = tree[player2_base_key+"race"]
    player2_score = tree[player2_base_key+"score"]
    player2_win = tree[player2_base_key+"win"]

    if (player1_win == '1'): outcome = 1
    elif (player2_win == '1'): outcome = 2
    else: outcome = 0
    
    insert_match(cursor, (player1_name, player2_name, outcome, None, player1_race, player2_race))
    handle_one_bracket_match_summary(cursor, tree, round_number, match_number, cursor.lastrowid)

def handle_one_bracket_match_summary(cursor, tree, round_number, match_number, match_id):
  summary_key = "R{0}G{1}details".format(round_number, match_number)
  summary = tree[summary_key]['BracketMatchSummary']
  if 'date' in summary:
    update_match_date(cursor, match_rowid=match_id, date=summary['date'])

  game_numbers = [re.search("\d+", i).group() for i in summary.keys() if re.match("^map\d+$", i)]    

  for game_number in game_numbers:
    map_name_key = "map%s" % game_number
    map_outcome_key = map_name_key + "win"
    map_name = summary[map_name_key]
    map_outcome = summary[map_outcome_key]
    
    insert_game(cursor, (map_name, map_outcome, match_id))

def handle_bracket(cursor, tree):
  bracket_type_string = tree.keys()[0]
  bracket_type = decode_template_name(bracket_type_string)
  if bracket_type['style'] != 'SE':
    print "Only SE type brackets are supported"
    exit(1)

  if (bracket_type['player_count'] == '16'): num_rounds = 4
  elif (bracket_type['player_count'] == '32'): num_rounds = 5
  elif (bracket_type['player_count'] == '64'): num_rounds = 6
  else:
    print "Unsupported number of players in bracket"
    exit(1)

  for i in range(1, num_rounds+1):
    handle_one_round(cursor, tree[bracket_type_string], i, num_rounds)

text = '''{{16SEBracket
|R1=Round of 16 (Bo5)
|R2=Quarterfinals (Bo5)
|R3=Semifinals (Bo5)
|R4=Finals (Bo5)
 <!-- ROUND OF 16 -->
|R1D1=MarineKing |R1D1race=t |R1D1flag=kr |R1D1score=3 |R1D1win=1
|R1D2=Seed |R1D2race=p |R1D2flag=kr |R1D2score=2 |R1D2win=
|R1G1details={{BracketMatchSummary
|date=March 26th, 2013
|lrthread=http://www.teamliquid.net/forum/viewmessage.php?topic_id=404922
|map1=Akilon Wastes |map1win=1 |vodgame1=http://www.youtube.com/watch?v=L-cpOD_z1XU&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map2=Cloud Kingdom |map2win=1 |vodgame2=http://www.youtube.com/watch?v=0YGrBwVLRxI&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map3=Daybreak |map3win=2 |vodgame3=http://www.youtube.com/watch?v=v5B_108RmJo&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map4=Star Station |map4win=2 |vodgame4=http://www.youtube.com/watch?v=PdM_aoYXH0Q&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map5=Whirlwind |map5win=1 |vodgame5=http://www.youtube.com/watch?v=TP_osQEzUTs&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
}}
|R1D3=HuK |R1D3race=p |R1D3flag=ca |R1D3score=3 |R1D3win=1
|R1D4=BabyKnight |R1D4race=p |R1D4flag=dk |R1D4score=0 |R1D4win=
|R1G2details={{BracketMatchSummary
|date=March 29th, 2013
|lrthread=http://www.teamliquid.net/forum/viewmessage.php?topic_id=405369
|map1=Star Station |map1win=1 |vodgame1=http://www.youtube.com/watch?v=42ollC-0BXI&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map2=Daybreak |map2win=1 |vodgame2=http://www.youtube.com/watch?v=FqKiiIfBGz0&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map3=Neo Planet S |map3win=1 |vodgame3=http://www.youtube.com/watch?v=PNA-Z52XZck&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
}}
|R1D5=ViBE |R1D5race=z |R1D5flag=us |R1D5score=3 |R1D5win=1
|R1D6=State |R1D6race=p |R1D6flag=us |R1D6score=0 |R1D6win=
|R1G3details={{BracketMatchSummary
|date=March 28th, 2013
|lrthread=http://www.teamliquid.net/forum/viewmessage.php?topic_id=405216
|map1=Daybreak |map1win=1 |vodgame1=http://www.youtube.com/watch?v=Kp6-ceQogxA&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map2=Cloud Kingdom |map2win=1 |vodgame2=http://www.youtube.com/watch?v=nOQrPtJPYic&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map3=Akilon Wastes |map3win=1 |vodgame3=http://www.youtube.com/watch?v=LaKKezZVp2Q&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
}}
|R1D7=Bly |R1D7race=z |R1D7flag=ua |R1D7score=3 |R1D7win=1
|R1D8=Suppy |R1D8race=z |R1D8flag=us |R1D8score=1 |R1D8win=
|R1G4details={{BracketMatchSummary
|date=March 27th, 2013
|lrthread=http://www.teamliquid.net/forum/viewmessage.php?topic_id=404971
|map1=Daybreak |map1win=1 |vodgame1=http://www.youtube.com/watch?v=M4AZ-thrpNQ&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map2=Neo Planet S |map2win=2 |vodgame2=http://www.youtube.com/watch?v=ipQBIVKqwWc&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map3=Cloud Kingdom |map3win=1 |vodgame3=http://www.youtube.com/watch?v=BG3KujDQm6g&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map4=Whirlwind |map4win=1 |vodgame4=http://www.youtube.com/watch?v=-jDCBwii7sI&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
}}
|R1D9=Minigun |R1D9race=p |R1D9flag=us |R1D9score=0 |R1D9win=
|R1D10=Creator |R1D10race=p |R1D10flag=kr |R1D10score=3 |R1D10win=1
|R1G5details={{BracketMatchSummary
|date=April 1st, 2013
|lrthread=http://www.teamliquid.net/forum/viewmessage.php?topic_id=405833
|map1=Cloud Kingdom |map1win=2 |vodgame1=http://www.youtube.com/watch?v=ggB0Qsa6TPU&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map2=Daybreak |map2win=2 |vodgame2=http://www.youtube.com/watch?v=anxCqgoTHRM&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map3=Akilon Wastes |map3win=2 |vodgame3=http://www.youtube.com/watch?v=T8ve-46FruM&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
}}
|R1D11=Stephano |R1D11race=z |R1D11flag=fr |R1D11score=- |R1D11win=
|R1D12=ThorZaIN |R1D12race=t |R1D12flag=se |R1D12score=W |R1D12win=1
|R1G6details={{BracketMatchSummary
|lrthread=
|comment=Stephano forfeited the series.
}}
|R1D13=SaSe |R1D13race=p |R1D13flag=se |R1D13score=3 |R1D13win=1
|R1D14=Goswser |R1D14race=z |R1D14flag=us |R1D14score=0 |R1D14win=
|R1G7details={{BracketMatchSummary
|date=April 2nd, 2013
|lrthread=http://www.teamliquid.net/forum/viewmessage.php?topic_id=405993
|map1=Cloud Kingdom |map1win=1 |vodgame1=http://www.youtube.com/watch?v=wwls8i12wQE&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map2=Daybreak |map2win=1 |vodgame2=http://www.youtube.com/watch?v=Sr73sjblmpc&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map3=Newkirk City |map3win=1 |vodgame3=http://www.youtube.com/watch?v=TEkkaOYqUWw&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
}}
|R1D15=herO |R1D15race=p |R1D15flag=kr |R1D15score=W |R1D15win=1
|R1D16=Feast |R1D16race=p |R1D16flag=be |R1D16score=- |R1D16win=
|R1G8details={{BracketMatchSummary
|lrthread=
|comment= Feast forfeited the series.
}}

 <!-- QUARTERFINALS -->
|R2W1=MarineKing |R2W1race=t |R2W1flag=kr |R2W1score=3 |R2W1win=1
|R2W2=HuK |R2W2race=p |R2W2flag=ca |R2W2score=0 |R2W2win=
|R2G1details={{BracketMatchSummary
|date=April 5th, 2013
|lrthread=http://www.teamliquid.net/forum/viewmessage.php?topic_id=406448
|map1=Cloud Kingdom |map1win=1 |vodgame1=http://www.youtube.com/watch?v=0q5rpHsjR_g&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map2=Whirlwind |map2win=1 |vodgame2=http://www.youtube.com/watch?v=Q7yQUrLGq-E&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map3=Neo Planet S |map3win=1 |vodgame3=http://www.youtube.com/watch?v=d8JD7Nf_y2Q&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
}}
|R2W3=ViBE |R2W3race=z |R2W3flag=us |R2W3score=0 |R2W3win=
|R2W4=Bly |R2W4race=z |R2W4flag=ua |R2W4score=3 |R2W4win=1
|R2G2details={{BracketMatchSummary
|date=April 4th, 2013
|lrthread=http://www.teamliquid.net/forum/viewmessage.php?topic_id=406314
|map1=Daybreak |map1win=2 |vodgame1=http://www.youtube.com/watch?v=koNnbuepFf0&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map2=Cloud Kingdom |map2win=2 |vodgame2=http://www.youtube.com/watch?v=YC4M2Pho-PI&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map3=Neo Planet S |map3win=2 |vodgame3=http://www.youtube.com/watch?v=9Bu-u90KQeQ&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
}}
|R2W5=Creator |R2W5race=p |R2W5flag=kr |R2W5score=2 |R2W5win=
|R2W6=ThorZaIN |R2W6race=t |R2W6flag=se |R2W6score=3 |R2W6win=1
|R2G3details={{BracketMatchSummary
|date=April 9th, 2013
|lrthread=http://www.teamliquid.net/forum/viewmessage.php?topic_id=407044
|map1=Cloud Kingdom |map1win=1 |vodgame1=http://www.youtube.com/watch?v=b6b9Hr1jcnw&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map2=Akilon Wastes |map2win=2 |vodgame2=http://www.youtube.com/watch?v=wtbj4cBmMLY&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map3=Daybreak |map3win=2 |vodgame3=http://www.youtube.com/watch?v=k2bPX-jMXPg&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map4=Neo Planet S |map4win=1 |vodgame4=http://www.youtube.com/watch?v=Tx92ykMO9xw&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map5=Star Station |map5win=2 |vodgame5=http://www.youtube.com/watch?v=IXZXfQzIzEk&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
}}
|R2W7=SaSe |R2W7race=p |R2W7flag=se |R2W7score=1 |R2W7win=
|R2W8=herO |R2W8race=p |R2W8flag=kr |R2W8score=3 |R2W8win=1
|R2G4details={{BracketMatchSummary
|date=April 8th, 2013
|lrthread=http://www.teamliquid.net/forum/viewmessage.php?topic_id=406885
|map1=Akilon Wastes |map1win=1 |vodgame1=http://www.youtube.com/watch?v=H_JD5heTVL8&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map2=Whirlwind |map2win=2 |vodgame2=http://www.youtube.com/watch?v=BVEgpVtSqjw&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map3=Daybreak |map3win=2 |vodgame3=http://www.youtube.com/watch?v=Z6DfKbkJqL0&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map4=Newkirk City |map4win=2 |vodgame4=http://www.youtube.com/watch?v=mSNb3hsoAqk&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
}}

 <!-- SEMIFINALS -->
|R3W1=MarineKing |R3W1race=t |R3W1flag=kr |R3W1score=3 |R3W1win=1
|R3W2=Bly |R3W2race=z |R3W2flag=ua |R3W2score=0 |R3W2win=
|R3G1details={{BracketMatchSummary
|date=April 10th, 2013
|lrthread=http://www.teamliquid.net/forum/viewmessage.php?topic_id=407231
|map1=Daybreak |map1win=1 |vodgame1=http://www.youtube.com/watch?v=YCxErGE7qDQ&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map2=Neo Planet S |map2win=1 |vodgame2=http://www.youtube.com/watch?v=5qRHQ8kY4fc&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map3=Cloud Kingdom |map3win=1 |vodgame3=http://www.youtube.com/watch?v=6lUx8-yqsCY&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
}}
|R3W3=ThorZaIN |R3W3race=t |R3W3flag=se |R3W3score=0 |R3W3win=
|R3W4=herO |R3W4race=p |R3W4flag=kr |R3W4score=3 |R3W4win=1
|R3G2details={{BracketMatchSummary
|date=April 11th, 2013
|lrthread=http://www.teamliquid.net/forum/viewmessage.php?topic_id=407387
|map1=Cloud Kingdom |map1win=2 |vodgame1=http://www.youtube.com/watch?v=iZBYMdIvqd8
|map2=Akilon Wastes |map2win=2 |vodgame2=http://www.youtube.com/watch?v=j9uXaAz1Pg0
|map3=Star Station |map3win=2 |vodgame3=http://www.youtube.com/watch?v=QlA50a8uPAE
}}

<!-- FINAL MATCH-->
|R4W1=MarineKing |R4W1race=t |R4W1flag=kr |R4W1score=3 |R4W1win=1
|R4W2=herO |R4W2race=p |R4W2flag=kr |R4W2score=0 |R4W2win=
|R4G1details={{BracketMatchSummary
|date=April 12th, 2013
|lrthread=http://www.teamliquid.net/forum/viewmessage.php?topic_id=407546
|map1=Cloud Kingdom |map1win=1 |vodgame1=http://www.youtube.com/watch?v=aQGNo5Dyv4E&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map2=Neo Planet S |map2win=1 |vodgame2=http://www.youtube.com/watch?v=lrCTSNsJJ6g&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
|map3=Daybreak |map3win=1 |vodgame3=http://www.youtube.com/watch?v=fpmf6675w5w&list=PLn9kCgJGjpyLgB-r9PNJaRsaK3jDOqBi8
}}

}}'''
text_stripped = strip_comments(text)
# lexer.input(text_stripped)

# while True:
#   token = lexer.token()
#   if token is None: break

#   print token

tree = yaccer.parse(text_stripped)

conn = sqlite3.connect('matches.db')
cursor = conn.cursor()
delete_db(cursor)
create_db(cursor)
conn.commit()

handle_bracket(cursor, tree)

conn.commit()
conn.close()