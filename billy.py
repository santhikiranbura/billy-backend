import spacy
import json
from datetime import datetime, timedelta
from dateutil.parser import parse
from numerizer import numerize
import random
import nltk
from nltk.chat.util import Chat, reflections
from nltk.corpus import wordnet
nlp = spacy.load("en_core_web_md")

patterns = [
    (r"hi|hello|hey", ["Hello!", "Hi there!","Hello there!","Hey"]),
    (r"how are you", ["I'm good, thank you.", "I'm doing well.","I'm awesome"]),
    (r"what is your name|who are you", ["I'm a simple chatbot.", "You can call me Billy."]),
    (r"quit|bye", ["Goodbye!", "See you later!"]),
]

chatbot = Chat(patterns, reflections)

nltk.download("punkt")

class Bill:
    def init(self):
        self.name = None
        self.amount = None
        self.date = None

    def __init__(self, dict):
        if dict is not None:
            vars(self).update(dict)
        else:
            self.init()

def isItAnExpense(verb):
    if nlp("pay made bought recharge").similarity(nlp(verb)) > 0.4:
        return True
    else:
        return False


def getNearestBillName(text, billnames):
    if text is None:
        return None
    max_similarity = 0
    closestBillName = None
    for billname in billnames:
        similarity = nlp(text.lower()).similarity(nlp(billname.lower()))
        if similarity > 0.6:
            if max_similarity < similarity:
              max_similarity = similarity
              closestBillName = billname
    if closestBillName is None and text is not None:
        closestBillName = text.split("/t")[0].strip()
    return closestBillName


def getValidAmount(money):
    money = numerize(money)
    amount = money.split(" ")[0]
    return int(amount)


def getValidDate(date):
    if date == "today":
        dt = datetime.now().date()
    elif date == "yesterday":
        dt = (datetime.now() - timedelta(days=1)).date()
    elif date == "tomorrow":
        dt = (datetime.now() + timedelta(days=1)).date()
    else:
        dt = parse(date)
    if dt is not None:
        date = dt.strftime("%Y-%m-%d")
    return date


def billEvent(bill, doc, billnames):

    for ent in doc.ents:
        if ent.label_ == "MONEY":
            bill.amount = getValidAmount(ent.text)
        if ent.label_ == "DATE":
            bill.date = getValidDate(ent.text)
    text = None
    numbers = 0
    number = 0
    for token in doc:
        if (token.dep_ == "dobj" or token.dep_ == "compound") and "rupee" not in token.text:
            if text is None:
                text = ""
            text = text + " " + token.text

        if token.pos_ == "NUM":
            number = token.text
            numbers = numbers + 1
        print(token.pos_,token.dep_,token.lemma_)
    if text is None and bill.name is None:
      for token in doc:
        if token.dep_ == "ROOT" and token.pos_ != "VERB":
            text = token.text
    if bill.name is None:
      bill.name = getNearestBillName(text, billnames)
    if bill.date is not None and numbers ==1:
      bill.amount = getValidAmount(number)


def getEvent(doc):
    for token in doc:
        if token.pos_ == "VERB" and isItAnExpense(token.lemma_) > 0.4:
            print("Triggered a bill event")
            return "bill"
    return None

class Event:
    def __init__(self, name, query, data):
        self.name = name
        self.query = query
        self.doc = nlp(query)
        self.data = data
        return getattr(self, name)()

    def default(self):
        name = getEvent(self.doc)
        if name is not None:
            self.name = name
            getattr(self, name)()
        else:
            self.data.update(comments=chatbot.respond(self.query))
          
    def validate(self,bill):
      if bill.name is not None and bill.amount is not None and bill.date is not None:
        return "Successfully created a bill"
      if bill.name is None:
        return random.choice(["What did you buy?","What did you purchase?","What items did you acquire?","What did you get?","What did you invest in?","What things did you procure?"])
      elif bill.amount is None:
        return random.choice(["How much you spent","How much did you expend?","What was your expenditure?","What was the amount you used?","What was your spending?","How much money did you put into it?"])
      elif bill.date is None:
        return random.choice(["When did you make this expense?","When did you incur this cost?","At what time did you spend money on this?","When did you make this expenditure?","What was the date of this expense?","When did you incur this financial outlay?"])
      else:
        return random.choice(["I'm having difficulty comprehending.","I'm struggling to grasp this.","It's not clear to me.","I find it hard to understand.","I'm having trouble making sense of it"]);
    def bill(self):
        if self.data is None:
            self.data = {}
            bill = Bill(None)
        elif "bill" not in self.data:
            bill = Bill(None)
        else:
            bill = Bill(self.data["bill"])
        if "billnames" not in self.data:
            billnames = []
        else:
            billnames = self.data["billnames"]
        billEvent(bill, self.doc, billnames)
        self.data.update(bill=vars(bill))
        comments = self.validate(bill)
        self.data.update(comments=comments)
