import stopword_removal_stemming
import nltk
import json
import jsonpickle
import re
import preprocessing
import slang_removal
import tfidf
import pandas as pd
from nltk import tag
from flask import Flask, jsonify

app = Flask(__name__)

def processing(data, username):
    data = preprocessing.remove_links(data)
    data = preprocessing.remove_username("@"+ username, data)
    data = preprocessing.remove(":", data)
    data = preprocessing.remove("\n", data)
    data = preprocessing.remove("RT", data)
    emoji_pattern = re.compile("["u"\U0001F600-\U0001F64F""]+", flags=re.UNICODE)
    data = preprocessing.remove_emoji(emoji_pattern,data)
    emoji_pattern = re.compile("["u"\U0001F300-\U0001F5FF""]+", flags=re.UNICODE)
    data = preprocessing.remove_emoji(emoji_pattern,data)
    return data


def pos_tag(i):
    test_data = []
    test_data_list = {"user": [], "data": []}
    test_data = stopword_removal_stemming.read_tweets("tw_db/t" + i + ".txt")
    if "\n" in test_data[0]:
        user = test_data[0].replace("\n", "")
    test_data_list["user"].append(user)
    test_data = processing(test_data,test_data[0])
    test_data = stopword_removal_stemming.tag_pos(test_data)
    test_data = slang_removal.slang_removal(test_data,slang_removal.Replace, slang_removal.Dismiss)
    test_data = stopword_removal_stemming.stemming_stop_removal(nltk.PorterStemmer(), test_data)
    test_data_list["data"].append(test_data)
    test_data = []
    return test_data_list

pos_data = pos_tag("0")

def return_keywords(data):
    keywords_list = []
    keywords = []
    for row in data:
        for tweet in row:
            if len(tweet) != 0:
                for (word, tag) in tweet:
                    if tag == "NN" or tag == "NNP" or tag == "NNS":
                        if word != "@" or word != "✨" or word != "❤" or word != "":
                            keywords.append(word)
            keywords_list.append(keywords)
            keywords = []
    return keywords_list

keywords = return_keywords(pos_data["data"])
#
# def write_to_file(file, data):
#     f = open(file, "w")
#     for row in data:
#         for tweet in row:
#             for word in tweet:
#                 f.write(word)
#                 f.write(",")
#             f.write("\n")
#         f.write("\n")
#
# write_to_file("keywords.txt", keywords)

tags = []
tf = []

user_keywords = tfidf.tfidf_rank_user(keywords,99,pos_data["user"][0])
for y in user_keywords.values():
    for x in y:
        tags.append(x)
    for x in y.values():
        tf.append(x)

df = pd.DataFrame(tags)
df['1'] = tf
df = df.rename(columns={0: 'word', '1': 'tf'})

finalJSON = df.reset_index().to_json(orient='records')
finalJSON = jsonpickle.decode(finalJSON)

@app.route('/TwitterRecommenderSystem/api/v1.0/tags', methods=['GET'])
def get_tasks():
    return jsonify({'tags': finalJSON})

if __name__ == '__main__':
    app.run(debug=True)