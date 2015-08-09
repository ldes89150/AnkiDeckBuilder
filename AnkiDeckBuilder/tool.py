import requests
import os
import warnings

from lxml import etree


def get_html(url):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        r = requests.get(url)
    return r.text

class basedict():
    def __init__(self):
        pass

    def search(self, word):
        pass

    @property
    def description(self):
        return ""

    @property
    def pronunciation(self):
        return ""


class ydict(basedict):
    xpath = {
        "description": u"/html[@id='Stencil']/body[@id='ysch']/div[@id='doc']/div[@id='bd']/div[@id='results']/div[@id='cols']/div[@id='left']/div/div[@id='main']/div/div[@id='web']/ol/li/div[@class='dd algo mt-20 lst DictionaryResults']",
        "pronunciation": u"/html[@id='Stencil']/body[@id='ysch']/div[@id='doc']/div[@id='bd']/div[@id='results']/div[@id='cols']/div[@id='left']/div/div[@id='main']/div/div[@id='web']/ol/li/div/div/div/span[@id='pronunciation_pos']"
    }

    def __init__(self):
        self.tree = None

    def search(self, word):
        url = "https://tw.dictionary.search.yahoo.com/search;?p={0}".format(word)
        html = get_html(url)
        self.tree = etree.HTML(html)


    def extract(self, item, pretty_print=False):
        if self.tree == None:
            return None
        nodes = self.tree.xpath(self.xpath[item])
        try:
            node = nodes[0]
        except IndexError:
            return ""

        for e in node.iter():
            for i in ("class","style","id","title"):
                try:
                    e.attrib.pop(i)
                except KeyError:
                    continue

        return etree.tostring(node, pretty_print=pretty_print)


    @property
    def description(self, pretty_print=False):
        return self.extract("description", pretty_print=pretty_print)

    @property
    def pronunciation(self, pretty_print=False):
        return self.extract("pronunciation", pretty_print=pretty_print)


class Word():
    def __init__(self, vocabulary="", pronunciation=""):
        self.vocabulary = vocabulary
        self.pronunciation = pronunciation
        self.description = ""

        self.MP3 = None


    def __str__(self):
        return self.vocabulary

    def auto_gen_content(self):
        self.downloadMP3()
        self.check_dict()

    def downloadMP3(self):
        url = "http://translate.google.com/translate_tts?tl=en&q={0}&ie=UTF-8&total=1&idx=0&client=t".format(self.vocabulary.lower())

        r = requests.get(url)
        self.MP3 = r.content

    def check_dict(self):
        d = ydict()
        d.search(self.vocabulary)
        self.description = d.description
        self.pronunciation = d.pronunciation


class Deck():
    def __init__(self, wordlist):
        self.wordlist = [Word(i) for i in wordlist]

    def auto_build(self):
        for i in self.wordlist:
            try:
                i.auto_gen_content()
                print "Success to build {0}".format(i.vocabulary)
            except:
                print "Fail to build {0}".format(i.vocabulary)

    def to_file(self, path):
        deckpath = os.path.join(path, "deck.txt")
        with open(deckpath, 'w') as deckfile:
            for i in self.wordlist:
                mp3path = os.path.join(path, "{0}.mp3".format(i.vocabulary))
                with open(mp3path, "wb") as mp3file:
                    mp3file.write(i.MP3)
                line = "[sound:{0}.mp3]<div><h1>{0}</h1></div><div>{1}</div>\t<div>{2}</div>\n".format(i.vocabulary, i.pronunciation,
                                                                                   i.description)
                deckfile.write(line)

