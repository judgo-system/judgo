# This module is written by Charles Clarke
import pickle
import random
import math
from topic.models import Topic
from document.models import Document

class lisp(object):
    def __init__(self, ar = None, dr = None):
        if dr == None:
            self.__ar = ar
            self.__dr = None
        else:
            if not isinstance(ar, lisp):
                ar = lisp(ar)
            self.__ar = ar
            if not isinstance(dr, lisp):
                dr = lisp(dr)
            self.__dr = dr

    def __repr__(self):
        if self.null():
            return "empty"
        elif self.atom():
            return " '" + repr(self.__ar)
        else:
            return "(" + repr(self.__ar) + " " + repr(self.__dr) + ")"

    def __post(self):
        if self.null():
            return ")"
        elif self.atom():
            return " '" + str(self.__ar) + ")"
        else:
            return " "  + str(self.__ar) + self.__dr.__post()

    def __str__(self):
        if self.null():
            return "empty"
        elif self.atom():
            return "'" + str(self.__ar)
        else:
            return "(" + str(self.__ar) + self.__dr.__post()

    def null(self):
        return self.__ar == None

    def atom(self):
        return self.__dr == None

    def consp(self):
        return not self.atom()

    def listp(self):
        return self.null() or self.consp()

    def car(self):
        "It takes a list as argument, and returns its first element."
        return self.__ar

    def cdr(self):
        "It takes a list as argument, and returns a list without the first element"
        return self.__dr

    def cadr(self):
        "Return second object"
        return self.cdr().car()

    def caar(self):
        "If the first element of a list is a list, then caar is the first element of the sublist"
        return self.car().car()

    def caadr(self):
        "(car (car (cdr x))) "
        return self.cadr().car()

    def caaar(self):
        "(car (car (car x)))"
        return self.caar().car()

    def cdar(self):
        "If the first element of a list is a list, then caar is the first element of the sublist, cdar is the rest of that sublist"
        return self.car().cdr()

    def cddr(self):
        "(cdr (cdr x)) "
        return self.cdr().cdr()

    def caaadr(self):
        "(car (car (car (cdr x))))"
        return self.caadr().car()

    def __reverse(self, reversed):
        if self.null():
            return reversed
        else:
            return self.cdr().__reverse(cons(self.car(), reversed))

    def reverse(self):
        "It takes a list and returns a list with the top elements in reverse order."
        return self.__reverse(empty())

    def append(self, thing):
        "append new item to the end of list"
        if self.null():
            return cons(thing, empty())
        else:
            return cons(self.car(), self.cdr().append(thing))

    def concat(self, llist):
        "merge to list together"
        if self.null():
            return llist
        else:
            return cons(self.car(), self.cdr().concat(llist))

    def length(self):
        if self.null():
            return 0
        else:
            return 1 + self.cdr().length()


class empty(lisp):
    def __init__(self):
        super().__init__()


class cons(lisp):
    def __init__(self, ar, dr):
        super().__init__(ar, dr)


class pref(object):
    def __init__(self, items):
        seen = set()
        self.__t = empty()
        for item in items:
            if item not in seen:
                self.__t = cons(cons(item, empty()),self.__t)
                seen.add(item)
        self.__equiv = []

        total_len = self.__t.length()
        self.total_judgment = (total_len - 1) + math.pow((total_len) // 2, 2)
        self.cur_judgment = 0
        

    def __repr__(self):
        return repr([self.__t, self.__equiv])

    def __str__(self):
        return str(self.__t) + " " + str(self.__equiv)

    def empty(self):
        return self.__t.null()

    def done(self):
        return self.empty() or self.__t.cdr().null()

    def best(self):
      if self.__t.null():
          return None
      else:
          b = {self.__t.caaar()}
          changed = True
          while changed:
              changed = False
              for (x, y) in self.__equiv:
                  if x in b and y not in b:
                      b.add(y)
                      changed = True
                  if y in b and x not in b:
                      b.add(x)
                      changed = True
          return b


    def request(self):
        if self.done():
            return None
        else:
            return [self.__t.caaar(), self.__t.caaadr()]

    def better(self, item):
        if not self.done():
            one = self.__t.car()
            rest = self.__t.cdr()
            two = rest.car()
            rest = rest.cdr()
            if item == one.caar():
                outcome = cons(one.car(), cons(two, one.cdr()))
                self.__t = rest.append(outcome)
            elif item == two.caar():
                outcome = cons(two.car(), cons(one, two.cdr()))
                self.__t = rest.append(outcome)

    def equivalent(self):
        if not self.done():
            one = self.__t.car()
            primary = one.car()
            rest = self.__t.cdr()
            two = rest.car()
            secondary = two.car()
            rest = rest.cdr()
            self.__t = rest.append(one.concat(two.cdr()))
            x = primary.car()
            y = secondary.car()
            if x != y:
                self.__equiv.append((x, y))

    def pop(self):
        if not self.done() or self.empty():
            return
        self.__t = self.__t.cdar()

    def length(self):
        return self.__t.length()

    def get_max_judgment(self):
        return 


def create_new_pref_obj(topic):
    """ Create a new pref object from list of ducuments for topic id

    Args:
        topic (obj): an object of topic.view.Topic model
    
    Returns:
        bytes of a pref obj created from a list of documents related to topic id
    """

    tutorial_topic = ['127', '133']
    #check if topic_id is tutorial topic or not, if yes then stop shuffle, if no then continue shuffle 
    if topic.uuid  in tutorial_topic:
        document_list = Document.objects.filter(topics = topic)
        docs_list = []
        for d in document_list:
            docs_list.append(d.uuid)
        pref_obj = pref(docs_list)  
    else:
        document_list = Document.objects.filter(topics = topic)
        docs_list = []
        for d in document_list:
            docs_list.append(d.uuid)
        random.shuffle(docs_list) #shuffles documents
        pref_obj = pref(docs_list)

    return pickle.dumps(pref_obj) 


def get_documents(pref_obj):
    """
    Args:

    Returns:
        
    """
    
    pref_obj = pickle.loads(pref_obj)
    if not pref_obj.done():
        return pref_obj.request() 
    return None

def is_judgment_finished(pref_obj):
    """
    Args:

    Returns:
        
    """
    
    pref_obj = pickle.loads(pref_obj)
    return pref_obj.done()
        

def is_judgment_completed(pref_obj):
    """
    Args:

    Returns:
        
    """
    
    pref_obj = pickle.loads(pref_obj)
    return pref_obj.empty()

def evaluate(pref_obj, element=None, equal=False):
    """
    Args:

    Returns:
        
    """
    
    pref_obj = pickle.loads(pref_obj)
    
    if not equal: 
        pref_obj.better(element)
    else:
        pref_obj.equivalent()
    # increase number of judgment
    pref_obj.cur_judgment += 1

    return pickle.dumps(pref_obj) 



def get_str(pref_obj):
    """
    Args:

    Returns:
        
    """
    
    pref_obj = pickle.loads(pref_obj)
    return pref_obj.__str__()

def get_best(pref_obj):

    pref_obj = pickle.loads(pref_obj)
    return pref_obj.best()


def pop_best(pref_obj):

    pref_obj = pickle.loads(pref_obj)
    pref_obj.pop()
    return pickle.dumps(pref_obj) 

def get_size(pref_obj):

    pref_obj = pickle.loads(pref_obj)
    return pref_obj.length()


def get_progress_count(pref_obj):

    pref_obj = pickle.loads(pref_obj)
    progress = 100 * (pref_obj.cur_judgment / pref_obj.total_judgment)     
    return round(progress, 2)