import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as BS
from textblob import TextBlob
import re
from nltk.corpus import stopwords
from constants import norms_dict


def link_count(html):
    soup = BS(html, "lxml")
    link_list = soup.find_all("a")
    cnt = len(link_list)
    return cnt

def nlp_data(text):

    # Organize text data into text blob
    soup = BS(text, "lxml")
    text = re.sub("'", "", soup.text)
    blob = TextBlob(text)

    # Get sentence count
    sentence_count = len(blob.sentences)

    # Get word count
    words = set(
        [word.lemmatize() for word in blob.words if word.lower() not in set(stopwords.words("english"))]
            )
    word_count = len(words)

    # Get word per sentence
    if sentence_count > 0:
        word_per_sentence = word_count * 1.0 / sentence_count
    else:
        word_per_sentence = 0

    # Get verb count
    verb_list = [pos[0].lemmatize() for pos in blob.pos_tags
                 if ("VB" in pos[1]) and (pos[0] not in set(stopwords.words("english")))]
    verb_count = len(verb_list)

    # Get adjective count
    adjective_list = [pos[0].lemmatize() for pos in blob.pos_tags
                      if ("JJ" in pos[1]) and (pos[0] not in set(stopwords.words("english")))]
    adjective_count = len(adjective_list)

    # Get polarity
    polarity = blob.polarity

    # Get subjectivity
    subjectivity = blob.subjectivity

    # Return a dataframe of all above features
    return pd.Series(dict(sentence_count=sentence_count,
                          word_per_sentence=word_per_sentence,
                          verb_count=verb_count,
                          adjective_count=adjective_count,
                          polarity=polarity,
                          subjectivity=subjectivity))

def json_to_features(json_data, feature_list):

    target_count = len(json_data["targets"])
    overview_linkcount = link_count(json_data["overview"])
    print "linkcount: {}".format(type(overview_linkcount))

    title_data = nlp_data(json_data["title"])
    title_data.index = ["title_" + x for x in title_data.index.tolist()]
    letter_body_data = nlp_data(json_data["letter_body"])
    letter_body_data.index = ["letter_body_" + x for x in letter_body_data.index.tolist()]
    overview_data = nlp_data(json_data["overview"])
    overview_data.index = ["overview_" + x for x in overview_data.index.tolist()]
    data = pd.concat([title_data, letter_body_data, overview_data], axis=0)
    data["target_count"] = target_count
    data["overview_linkcount"] = overview_linkcount

    to_norm = [x for x in data.index.tolist() if ("polarity" not in x) and ("subjectivity" not in x)]
    dont_norm = [x for x in data.index.tolist() if ("polarity" in x) or ("subjectivity" in x)]

    features = []
    for feature in feature_list:
        if feature in dont_norm:
            features.append( data[feature] )
        elif feature in to_norm:
            normed_feature = (data[feature] - norms_dict[feature + "_mean"]) * 1.0 / norms_dict[feature + "_std"]
            features.append( normed_feature )

    features = np.array(features)

    return features

def fit_daycount(update_json, goal):

    update_df = pd.DataFrame([[update["created_at"], update["title"]]
                               for update in update_json["updates"]],
                             columns=("times", "counts"))

    update_df.times = update_df.times.apply(pd.to_datetime)
    update_df["days"] = (update_df.times - update_df.times.shift(1)).drop(0).apply(lambda x: x.days)
    update_df["minutes"] = (update_df.times - update_df.times.shift(1)).drop(0).apply(lambda x: x.seconds * 1.0 / 60)

    update_df = update_df.drop(0)

    update_df.days = update_df.days.cumsum()
    update_df.minutes = update_df.minutes.cumsum()

    update_df = update_df[ update_df.counts.apply(lambda x: x.isdigit()) ]

    result = pd.ols(y=update_df["counts"], x=update_df.days, intercept=True)
    intercept, slope = result.beta.intercept, result.beta.x

    if (slope == 0) or ((goal - intercept) * 1.0 / slope > 400):

        result = pd.ols(y=update_df["counts"], x=update_df.minutes, intercept=True)
        intercept, slope = result.beta.intercept, result.beta.x

        daycount = (1.0 / (60*24)) * (goal - intercept) * 1.0 / slope

        return daycount

    else:

        daycount = (goal - intercept) * 1.0 / slope

        return daycount
