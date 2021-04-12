import re
import ftfy
import json
import spacy
import torch

from tqdm import tqdm


def load_existing_data_loader(data_loader, path):
    old_data_loader = torch.load(path)
    for attr in data_loader.__dict__.keys():
        #print(old_data_loader)#DEBUG
        #print(attr)#DEBUG
        if attr not in old_data_loader.__dict__.keys():
            continue
        setattr(data_loader, attr, getattr(old_data_loader, attr))
    #print(data_loader.__dict__["vocab_encoder"])DEBUG


################################################################################
#
# Code Below taken from HuggingFace pytorch-openai-lm repository
#
################################################################################


def get_pairs(word):
    """
    Return set of symbol pairs in a word.
    word is represented as tuple of symbols (symbols being variable-length strings)
    """
    pairs = set()
    prev_char = word[0]
    for char in word[1:]:
        pairs.add((prev_char, char))
        prev_char = char
    return pairs


def text_standardize(text):
    """
    fixes some issues the spacy tokenizer had on books corpus
    also does some whitespace standardization
    """
    text = text.replace('—', '-')
    text = text.replace('–', '-')
    text = text.replace('―', '-')
    text = text.replace('…', '...')
    text = text.replace('´', "'")
    text = re.sub(r'''(-+|~+|!+|"+|;+|\?+|\++|,+|\)+|\(+|\\+|\/+|\*+|\[+|\]+|}+|{+|\|+|_+)''', r' \1 ', text)
    text = re.sub(r'\s*\n\s*', ' \n ', text)
    text = re.sub(r'[^\S\n]+', ' ', text)
    return text.strip()


class TextEncoder(object):
    """
    mostly a wrapper for a public python bpe tokenizer
    """

    def __init__(self, encoder_path, bpe_path):
        self.nlp = spacy.load(
            'en_core_web_sm', disable=['parser', 'tagger', 'ner', 'textcat'])
        self.encoder = json.load(open(encoder_path))
        self.decoder = {v: k for k, v in self.encoder.items()}
        #merges = array where each element is 1 line in vocab_40000.bpe
        merges = open(bpe_path, encoding='utf-8').read().split('\n')[1:-1]
        #merge = 1 elemnent in merges
        #merges becomes = array of tuples, each tuple contains
        # characters and character sequences delimited by space in 1 element of orignal array 'merges'
        #each string in merges, becomes tuple of the same string split by ' ' character
        merges = [tuple(merge.split()) for merge in merges]
        #self.bpe ranks = dict {1 tuple in merges : index of the tuple in merges
        self.bpe_ranks = dict(zip(merges, range(len(merges))))
        self.cache = {}

    def bpe(self, token):
        word = tuple(token[:-1]) + (token[-1] + '</w>',)
        if token in self.cache:
            return self.cache[token]
        pairs = get_pairs(word)

        if not pairs:
            return token+'</w>'

        while True:
            bigram = min(pairs, key=lambda pair: self.bpe_ranks.get(
                pair, float('inf')))
            if bigram not in self.bpe_ranks:
                #print("Not found")#DEBUG
                break
            first, second = bigram
            new_word = []
            i = 0
            while i < len(word):
                try:
                    j = word.index(first, i)
                    new_word.extend(word[i:j])
                    i = j
                except:
                    new_word.extend(word[i:])
                    break

                if (word[i] == first and i < len(word) - 1 and
                        word[i+1] == second):
                    new_word.append(first+second)
                    i += 2
                else:
                    new_word.append(word[i])
                    i += 1
            new_word = tuple(new_word)
            word = new_word
            if len(word) == 1:
                break
            else:
                pairs = get_pairs(word)
        word = ' '.join(word)
        if word == '\n  </w>':
            word = '\n</w>'
        self.cache[token] = word
        return word

    def encode(self, texts, verbose=True):
        texts_tokens = []
        if verbose:
            for text in tqdm(texts, ncols=80, leave=False):
                text = self.nlp(text_standardize(ftfy.fix_text(text)))
                text_tokens = []
                for token in text:
                    text_tokens.extend(
                        [self.encoder.get(t, 0) for t in
                         self.bpe(token.text.lower()).split(' ')])
                texts_tokens.append(text_tokens)
        else:
            for text in texts:
                #print(text);#DEBUG
                text = self.nlp(text_standardize(ftfy.fix_text(text)))
                #print(text);#DEBUG
                text_tokens = []
                for token in text:
                    #print(token)#DEBUG
                    #print(self.encoder)
                    text_tokens.extend(
                        [self.encoder.get(t, 0) for t in
                         self.bpe(token.text.lower()).split(' ')])
                ################ADRIAN ADDED
                Zeroes=0
                for WrdN in range(len(text_tokens)):
                  if(text_tokens[WrdN]==0):
                    Zeroes+=1
                #if(Zeroes!=0):
                  #print(Zeroes)
                ####################
                texts_tokens.append(text_tokens)
        #print(texts_tokens)#DEBUG
        return texts_tokens
