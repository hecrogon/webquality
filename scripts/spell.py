from enchant.checker import SpellChecker
from enchant import Broker
#from enchant.tokenize import get_tokenizer, EmailFilter
from lxml import etree, html
from lxml.html.clean import clean_html, Cleaner
import requests
import enchant

from scrapy.selector import Selector


r = requests.get('http://www.shidix.com')

sel = Selector(r)

body = sel.xpath('//body')

print body

cleaner = Cleaner(scripts=True, embedded=True, meta=True, page_structure=True, links=True, style=True, processing_instructions=True, annoying_tags=True, remove_tags = ['a', 'ul', 'li', 'td', 'div', 'span', 'img', 'p', 'h1', 'h2', 'h3', 'strong', 'body', 'br'])
text = cleaner.clean_html(r.text) 

#print text

#text = "hola hello fasdf"
chkr = SpellChecker("es_ES")
chkr.set_text(text)

errors = {}
for err in chkr:
    errors[err.word] = True

chkr = SpellChecker("en_EN")
chkr.set_text(text)

errors2 = {}
for err in chkr:
    errors2[err.word] = True

errors3 = [val for val in errors if val in errors2]
#print errors3

