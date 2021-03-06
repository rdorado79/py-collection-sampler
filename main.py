import sys, os, getopt, io

from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer

from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

import numpy as np

import math
import random


class PModel:
  ncat = 0  

  def __init__(self,logpcats, logpconds, wordlist):
    self.ncat = len(logpcats)
    self.logpcats = logpcats
    self.logpconds = logpconds
    self.wordlist = wordlist

  def calculateProb(self, fd, category):
    probs = []
    for word_id, value in fd.iteritems():
      probs.append(self.logpconds[category][word_id])
    return sum(probs)
   
  def calculateBest(self, fd):    
    bestp=-sys.maxint
    bestcat=-1
    print "Cat "+str(self.ncat)
    for cat in range(self.ncat):
      prob = self.calculateProb(fd, cat)
      print "prob="+str(prob)
      if prob > bestp:
         bestp = prob
         bestcat = cat
    return bestcat

  def getId(self, word):
    try:
      return self.wordlist.index(word)
    except ValueError:
      return -1

class SampleWithouReplacementModel:
   
   def __init__(self, elements, sample):
     self.n = len(sample)
     self.sample = sample
     self.mask = [0 for x in range(self.n)]
     self.nselected = [0 for x in range(elements)]
     self.maxs = [sample.count(x) for x in range(elements)]

   def next(self, element):
#     if self.nselected >= self.maxs: raise Exception
     
     rand = int(random.random()*(self.maxs[element] - self.nselected[element]))  
     count = 0
     for i in range(self.n):
       if self.sample[i] == element and self.mask[i] != 1:
         if rand == count:            
           self.mask[i] = 1
           self.nselected[element] = self.nselected[element] + 1
           return i
         else: count = count + 1
    

def logsum(array):
  resp = 0
  print array
  for i in range(0,len(array)): 
    resp+=math.log(array[i])
  return resp
    

def test(twenty_test, pmodel):
  tokenizer = RegexpTokenizer(r'[a-z]+')
  pred = []
  i=0
  for document in twenty_test.data:   

    fd = {}
    splits = tokenizer.tokenize(document)
    filtered_words = [word for word in splits if word not in stopwords.words('english')]

    for word in filtered_words:
      indx = pmodel.getId(word)
      if indx != -1:
        try:
          fd[indx] = fd[indx]+1
        except KeyError:
          fd[indx] = 1
    best = pmodel.calculateBest(fd)
    pred.append( best ) 
    print str(best)+" "+str(twenty_test.target[i]) 
    i=i+1
  return np.mean(pred == twenty_test.target) 

def main(argv):

  try:
    opts, args = getopt.getopt(argv,"l:",["ifile=","ofile="])
  except getopt.GetoptError:
    # printUsage()
    sys.exit(2)


  for opt, arg in opts:
    if opt == '-l':
      traindatadir = arg
    elif opt == '-g':
      classfile = arg
    elif opt == '-e':
      uclassfile = arg
    elif opt == '-u':
      unlabeleddatadir = arg
    elif opt == '-d':
      debug = True


  sampler = SampleWithouReplacementModel(2, [0,1,1,1,0,1,1])

  for i in range(2):
    print sampler.next(0)
    print sampler.next(1)
"""
  categories = ['talk.politics.guns','soc.religion.christian','sci.electronics','rec.sport.baseball','comp.graphics']
  twenty_train = fetch_20newsgroups(categories=categories, subset='train', shuffle=True, random_state=42,remove=('headers', 'footers', 'quotes') ) #
  twenty_test = fetch_20newsgroups(categories=categories, subset='test', shuffle=True, random_state=42,remove=('headers', 'footers', 'quotes') )

  id_dict = {} 
  wordlist = []
  nterms = 0
  document_counts=[]
  ndocs = 0
  word_counts = {}

  tokenizer = RegexpTokenizer(r'[a-z]+')




  for document in twenty_train.data[:10]:    

    splits = tokenizer.tokenize(document)
    filtered_words = [word for word in splits if word not in stopwords.words('english')]

    fd = {}

    for word in filtered_words:
      
      try:
        id_word = id_dict[word]
      except KeyError:
        id_dict[word] = nterms
        id_word = nterms
        nterms = nterms+1
        wordlist.append(word)

      try:
        fd[id_word] = fd[id_word] + 1
        #fd[id_word] = 1 
      except KeyError:
        fd[id_word] = 1

      try:
        word_counts[id_word] = word_counts[id_word] + 1
      except KeyError:
        word_counts[id_word] = 1
 
    document_counts.append(fd)
    ndocs=ndocs+1
  
  nvocab = len(wordlist)
  ncat = len(set(twenty_train.target))
  countcat = [0 for x in range(ncat)]
  sumcounts = [{} for x in range(ncat)]
  pconds = [[0 for x in range(nvocab)] for x in range(ncat)]
  logpconds = [[0 for x in range(nvocab)] for x in range(ncat)]
  for i in range(ndocs):

    print twenty_train.target[i]
    #print document_counts[i]
    countcat[twenty_train.target[i]] += 1
    
    #for doc_count in document_counts:
    for word_id, value in document_counts[i].iteritems():
        pconds[twenty_train.target[i]][word_id]+=value
        try:
          sumcounts[twenty_train.target[i]][word_id]+=value
        except KeyError:
          sumcounts[twenty_train.target[i]][word_id]=value




  #******************************************************************************
  #******************************************************************************
  #******************************************************************************


  Acatprior = 1
  Bcatprior = ncat
  logcats = [ (x + Acatprior)/float(ndocs + Bcatprior)  for x in countcat]
  #logcats = [math.log( (x + Acatprior)/float(ndocs + Bcatprior) ) for x in countcat]

  print countcat
  print sumcounts
  print logcats

#  print "'"+twenty_train.data[1]+"'"
#  print str(document_counts[1])
  for i in range(10):
    print "cat: "+str(twenty_train.target[i])
    print "'"+str(twenty_train.data[i])+"'\n"    
    print document_counts[i]

  tmp_id_word = 2
  print wordlist[tmp_id_word]+": "+str(tmp_id_word)
  for i in range(ncat):
    try:
     print "p(c="+str(i)+", w="+wordlist[tmp_id_word]+") = "+str(sumcounts[i][tmp_id_word])
    except KeyError:
     print "p(c="+str(i)+", w="+wordlist[tmp_id_word]+") = 0"
  print word_counts[tmp_id_word]


  alphaWordprior = 1.0
  sumPrior = ncat*alphaWordprior
  for id_word in range(nvocab):
    for i in range(ncat):
      pconds[i][id_word] = (pconds[i][id_word] + alphaWordprior)/(word_counts[tmp_id_word] + sumPrior)
      logpconds[i][id_word] = math.log(pconds[i][id_word])

  print "\n/******************/\n   Probs\n/******************/"
  print logcats
  print sum(logcats)

  for i in range(ncat):
      print pconds[i][id_word]
       
  print wordlist
  pmodel = PModel(logcats, logpconds, wordlist)

  #******************************************************************************
  #******************************************************************************
  #******************************************************************************
  print "\n/******************/\n   Prediction step\n/******************/"

  accuracy = test(twenty_test, pmodel)
  print "Accuracy: "+str(accuracy)
    
#  print wordlist[1]+": "+str(document_counts[1])
#  print "p(c=0, w=dad)"+sumcounts[0][0]
        #termsdoc = termsdoc+1
    
  #counts.append(count)


  #count_vect = CountVectorizer()
  #data = count_vect.fit_transform(twenty_train.data[0:1])
  #print data.toarray()
  #print data.vocabulary

  #

  #for dirname, dirnames, filenames in os.walk(traindatadir):
  #  for filename in filenames:
  #    inpfile = os.path.join(dirname,filename)
  #    print inpfile
"""

if __name__ == "__main__":
  main(sys.argv[1:])
