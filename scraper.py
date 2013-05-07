from parser import lexer
from parser import yaccer
import urllib2
import json
import string

def scrape(api_endpoint_format, query_page):
  # get the wiki page source
  api_endpoint = api_endpoint_format.format(query_page)
  source = urllib2.urlopen(api_endpoint).read()
  json_obj = json.loads(source)
  pages = json_obj["query"]["pages"].keys()
  texts = [json_obj["query"]["pages"][page]["revisions"][0]["*"] for page in pages]
  return [handle_text(text.encode("utf-8")) for text in texts]

def handle_text(text):
  # figure out where the match list starts
  startIndex = string.find(text, "{{MatchList")

  # find the end of the match list using the token stream
  lexer.input(text[startIndex:])
  depth = 0
  end = -1
  while True:
    token = lexer.token()
    if token is None: break

    if token.type == "L2BRACE":
      depth += 1
    elif token.type == "R2BRACE":
      depth -= 1

    if depth == 0:
      endToken = token
      break
    # print token

  # pick out the match list section
  endIndex = startIndex + endToken.lexpos + len(endToken.value)
  clippedText = text[startIndex:endIndex]

  # generate parse tree
  return yaccer.parse(clippedText)