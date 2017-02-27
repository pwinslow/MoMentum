'''
This file contains the wrangler class.
'''

# Numerical imports
import pandas as pd
from numpy import isnan

# NLP and text processing imports
import re
from textblob import TextBlob
from nltk.corpus import stopwords
from bs4 import BeautifulSoup as BS

# Other imports
import datetime as dt
from datetime import timedelta
from sqlalchemy import create_engine


class Wrangler(object):
    '''The Wrangler class contains a number of static methods designed to
       load and clean the raw data, extract features using basic NLP methods,
       filter outliers, rescale features, and save/load the data to/from a
       PostgresSQL database.'''

    def __init__(self):
        pass

    @staticmethod
    def load_from_csv(data_path):

        print "Loading data..."

        # Read data into a pandas dataframe
        country_code = ['CA', 'AU', 'GB', 'US']
        for code in country_code:
            if code == "US":
                for i in range(1, 5):
                    df_name = "{0}_{1}".format(code, i)
                    data = data_path + "{0}_data.csv".format(df_name)
                    globals()[df_name] = pd.read_csv(data)
            else:
                for i in range(1, 3):
                    df_name = "{0}_{1}".format(code, i)
                    data = data_path + "{0}_data.csv".format(df_name)
                    globals()[df_name] = pd.read_csv(data)

        # Glue datasets back together and reindex
        df = pd.concat([AU_1, AU_2, CA_1, CA_2, GB_1, GB_2, US_1, US_2, US_3, US_4])
        df.index = range(df.shape[0])

        # Set schema to proper dtype for signature counts, goals, and signature accumulation rate
        df.signature_count = df.signature_count.astype(int)
        df.goal = df.goal.astype(int)
        df.signature_rate = df.signature_rate.astype(float)

        return df

    @staticmethod
    def drop_nulls_and_duplicates(df):

        print "Dropping null and duplicate values in data..."

        # Remove petitions with no title (there are only two)
        df = df[df.title.isnull() == False]

        # Remove petitions with no letter body (there are only three)
        df = df[df.letter_body.isnull() == False]

        # Drop petitions with duplicated titles
        df = df[df.title.duplicated() == False]

        return df

    @staticmethod
    def reformat_df(df):

        print "Reformatting data..."

        print "Reformatting target info..."
        # Reformat the targets column to extract types of targets
        def target_class(target):
            target_list = [x.strip().split()[1][2:-1] for x in target.split(',') if "u'type':" in x]
            target_set = list(set(target_list))
            if len(target_list) == 0:
                return "none"
            if len(target_set) > 1:
                return "mixed"
            else:
                return target_set[0]
        df["target_class"] = df.targets.apply(target_class)

        # Generate dummy variables for target_classes
        target_class_dummies = pd.get_dummies(df["target_class"], prefix="targetclass")
        df = pd.concat([target_class_dummies, df], axis=1)

        # Reformat targets column to extract number of targets
        def target_count(target):
            target_list = [x.strip().split()[1][2:-1] for x in target.split(',') if "u'type':" in x]
            return len(target_list)
        df["target_count"] = df.targets.apply(target_count)

        print "Reformatting organization info..."
        # Add column to say whether organization info is given or not
        def org_info(row):
            name = row['organization_name']
            url = row['organization_url']
            if (type(name) == float) or (type(url) == float):
                if (isnan(name) and not isnan(url)) or (not isnan(name) and isnan(url)):
                    return "partial"  # This case isn't present in the data
                elif (isnan(name) and isnan(url)):
                    return 0  # False if both are missing
            else:
                return 1  # True if both are present
        df["org_info_given"] = df.apply(org_info, axis=1)

        print "Reformatting creator info..."
        # Add column to say whether creator info is given or not
        def creator_info(row):
            name = row['creator_name']
            url = row['creater_url']
            if (type(name) == float) or (type(url) == float):
                if (isnan(name) and not isnan(url)) or (not isnan(name) and isnan(url)):
                    return "partial"  # This case isn't present in the data
                elif (isnan(name) and isnan(url)):
                    return 0  # False if both are missing
            else:
                return 1  # True if both are present
        df["creator_info_given"] = df.apply(creator_info, axis=1)

        print "Reformatting category info..."
        # Replace nan's in category column with string
        def category_cleaner(category):
            if type(category) == str:
                return category
            elif isnan(category):
                return "None"
        df.category = df.category.apply(category_cleaner)

        # Map fringe categories to umbrella category
        category_map = {"Animal Rights": "Animals",
                        "Human Rights": "Rights",
                        "Women's Rights": "Rights",
                        "Gay Rights": "Rights",
                        "Immigrant Rights": "Rights",
                        "Criminal Justice": "Justice",
                        "Economic Justice": "Justice",
                        "Human Trafficking": "Trafficking",
                        "End Sex Trafficking": "Trafficking",
                        "Sustainable Food": "SocialGood",
                        "Social Entrepreneurship": "SocialGood",
                        "Environment": "SocialGood",
                        "Peace in the Middle East": "warANDpeace",
                        "Autism": "Health"}
        df.category = df.category.map(category_map)

        # Drop lower performing categories
        df = df[df.category.isin(['Animals',
                                  'Rights',
                                  'Justice',
                                  'SocialGood',
                                  'Health',
                                  'None',
                                  'Education'])]

        # Generate dummy variables for categories
        category_dummies = pd.get_dummies(df["category"], prefix="category")
        df = pd.concat([category_dummies, df], axis=1)

        print "Reformatting datetime info..."
        # Convert created_at and end_at columns to datetime format
        df.created_at = df.created_at.apply(pd.to_datetime)
        df.end_at = df.end_at.apply(pd.to_datetime)

        # Filter petitions that were expected to last less than one day
        df = df[ (df.end_at - df.created_at) >= timedelta(days=1) ]

        # Filter petitions that were expected to last over a year
        df = df[ (df.end_at - df.created_at) <= timedelta(years=1) ]

        # If petition has gone past its expiration date but is still listed as open,
        # set status to closed
        def past_due(row):
            status = row["status"]
            end_at = row["end_at"]
            if (status == "open") and (end_at <= dt.datetime.utcnow()):
                return "closed"
            else:
                return status
        df.status = df.apply(past_due, axis=1)

        # Add columns representing day-of-week and month that petition was submitted at
        day_map = {0: 1,
                   1: 2,
                   2: 3,
                   3: 4,
                   4: 5,
                   5: 6,
                   6: 7}
        df["day_of_week_created"] = pd.to_datetime(df.created_at).dt.dayofweek
        df["month_created"] = df.created_at.apply(lambda x: x.to_datetime().month)
        df.day_of_week_created = df.day_of_week_created.map(day_map)

        # Generate dummy variables for day_of_week and month
        day_dummies = pd.get_dummies(df["day_of_week_created"], prefix="day_of_week_created")
        df = pd.concat([day_dummies, df], axis=1)
        month_dummies = pd.get_dummies(df["month_created"], prefix="month_created")
        df = pd.concat([month_dummies, df], axis=1)

        print "Counting links in text info..."
        # Add columns counting links in both the overview and the letter body
        def link_count(html):
            soup = BS(html, "lxml")
            link_list = soup.find_all("a")
            cnt = len(link_list)
            return cnt

        df["overview_linkcount"] = df.overview.apply(link_count)
        df["letter_body_linkcount"] = df.letter_body.apply(link_count)

        print "Performing NLP on text info..."
        # Gather info on sentence count, words per sentence, verb count, adjective count,
        # polarity, and subjectivity
        def nlp_data(text):

            # Organize text data into text blob
            soup = BS(text, "lxml")
            text = re.sub("'", "", soup.text)
            blob = TextBlob(text)

            # Get sentence count
            sentence_count = len(blob.sentences)

            # Get word count
            words = set(
                        [word.lemmatize() for word in blob.words
                         if word.lower() not in set(stopwords.words("english"))]
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

        # Iterate over all textual data columns, applying nlp_data method and merging
        # resulting dataframe with df
        text_columns = ["title", "letter_body", "overview"]
        for column in text_columns:
            temp_df = df[column].apply(nlp_data)
            var_list = temp_df.columns
            for var in var_list:
                df[column + "_" + var] = temp_df[var]
            print "\tFinished with {} column data...".format(column)

        print "Done reformatting data..."
        return df

    @staticmethod
    def filter_outliers(df):

        '''
        Original plan was to impose the interquartile rule (IQR). However, many of the
        interquartile ranges are zero, meaning that IQR rule isn't useful for removing
        outliers here. In the absence of a better way, I derived some very conservative
        limits with the help of seaborn pairplot visualizations and impose them below.
        '''

        print "Filtering outliers..."
        df = df[(    (df.overview_linkcount <= 80)
                   & (df.letter_body_linkcount <= 20)
                   & (df.letter_body_sentence_count <= 300)
                   & (df.letter_body_word_per_sentence <= 100)
                   & (df.letter_body_verb_count <= 800)
                   & (df.letter_body_adjective_count <= 450)
                   & (df.overview_sentence_count <= 400)
                   & (df.overview_word_per_sentence <= 150)
                   & (df.overview_verb_count <= 800)
                  )]

        return df

    @staticmethod
    def drop_spurious_columns(df):

        print "Dropping spurious info..."
        # Drop leftover columns that are not used for modeling
        df.drop(["organization_name", "organization_url", "targets", "creator_name",
                 "creater_url", "image_url", "url"], axis=1, inplace=True)

        return df

    @staticmethod
    def feature_scaling(df, method="standard"):

        print "Rescaling features..."
        # Keep list of maxes used to normalize so you can reinterpret results from ML
        norm_list = ["target_count", "goal", "overview_linkcount",
                     "letter_body_linkcount", "title_adjective_count", "title_verb_count",
                     "title_sentence_count", "title_word_per_sentence", "letter_body_adjective_count",
                     "letter_body_sentence_count", "letter_body_verb_count", "letter_body_word_per_sentence",
                     "overview_adjective_count", "overview_sentence_count", "overview_verb_count",
                     "overview_word_per_sentence"]

        # Return values used to normalize numerical features so we can un-normalize later
        norm_dict = {}
        for feature in norm_list:
            norm_dict[feature + "_max"] = df[feature].max()
        for feature in norm_list:
            norm_dict[feature + "_min"] = df[feature].min()
        for feature in norm_list:
            norm_dict[feature + "_mean"] = df[feature].mean()
        for feature in norm_list:
            norm_dict[feature + "_std"] = df[feature].std()

        # Normalize all non-categorical features
        if method == "standard":
            for col in norm_list:
                df[col] = (df[col] - df[col].mean()) * 1.0 / df[col].std()
        else:
            for col in norm_list:
                df[col] = df[col] * 1.0 / df[col].max()

        return df, norm_dict

    @staticmethod
    def save_to_db(df, table_name):

        print "Saving to database..."
        # Create postgres engine for changeORG database
        engine = create_engine('postgresql://postgres:@localhost/postgres')

        # Put dataframe into table
        df.to_sql(table_name, engine, if_exists="replace", index=False)

    @classmethod
    def load_from_db(cls, table_name):

        print "Loading from database..."
        # Create postgres engine for changeORG database
        engine = create_engine('postgresql://postgres:@localhost/postgres')

        # Put dataframe into table
        df = pd.read_sql("SELECT * FROM {};".format(table_name), engine)

        return df
