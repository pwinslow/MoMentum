# Numerical imports
import numpy as np
import pandas as pd

# Visual imports
import matplotlib.pyplot as plt

# Scikit imports
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.cross_validation import train_test_split
from sklearn.feature_selection import SelectFromModel
from sklearn.ensemble import RandomForestClassifier
from sklearn.grid_search import RandomizedSearchCV
from sklearn.metrics import classification_report, roc_auc_score, roc_curve

# Import the wrangler class
from wrangler import Wrangler

# Other imports
import cPickle
from imblearn.over_sampling import RandomOverSampler


def extract_features(df):

    # Extract features for regression and create design matrix and target series
    features_and_targets = df[[u'day_of_week_created_1',
                               u'day_of_week_created_2',
                               u'day_of_week_created_3',
                               u'day_of_week_created_4',
                               u'day_of_week_created_5',
                               u'day_of_week_created_6',
                               u'day_of_week_created_7',
                               u'category_Animals',
                               u'category_Education',
                               u'category_Health',
                               u'category_Justice',
                               u'category_None',
                               u'category_Rights',
                               u'category_SocialGood',
                               u'targetclass_custom',
                               u'targetclass_mixed',
                               u'targetclass_none',
                               u'targetclass_us_government',
                               u'goal',
                               u'target_count',
                               u'org_info_given',
                               u'creator_info_given',
                               u'overview_linkcount',
                               u'letter_body_linkcount',
                               u'title_adjective_count',
                               u'title_polarity',
                               u'title_sentence_count',
                               u'title_subjectivity',
                               u'title_verb_count',
                               u'title_word_per_sentence',
                               u'letter_body_adjective_count',
                               u'letter_body_polarity',
                               u'letter_body_sentence_count',
                               u'letter_body_subjectivity',
                               u'letter_body_verb_count',
                               u'letter_body_word_per_sentence',
                               u'overview_adjective_count',
                               u'overview_polarity',
                               u'overview_sentence_count',
                               u'overview_subjectivity',
                               u'overview_verb_count',
                               u'overview_word_per_sentence',
                               u'signature_rate',
                               u'status']].columns.tolist()

    feature_list = [col for col in features_and_targets
                    if (col != "signature_rate") & (col != "status") & (col != "goal") & (col != "target_count")]
    X = df[feature_list]
    Y = df.status.apply(lambda x: 1 if x == "victory" else 0)

    # Apply SMOTE random over-sampling and restore data to pandas dataframe format
    ros = RandomOverSampler()
    X, Y = ros.fit_sample(X, Y)
    X = pd.DataFrame(X, index=range( len(X) ), columns=feature_list)
    Y = pd.Series(Y)

    return X, Y

def feature_selection(X_dev, Y_dev, X_eval):

    # Perform feature selection
    clf = ExtraTreesClassifier(n_estimators=200)
    _ = clf.fit(X_dev, Y_dev)
    model = SelectFromModel(clf, prefit=True)
    Xdev = model.transform(X_dev)
    Xeval = model.transform(X_eval)

    return Xdev, Xeval

def train_model(Xdev, Ydev):

    # Initialize a random forest classifier algorithm
    rf = RandomForestClassifier()

    # Define a parameter grid to search over
    param_dist = {"n_estimators": range(100, 550, 50),
                  "max_depth": range(5, 17, 2)}

    # Define a randomed grid search class to optimize hyperparameters
    clf = RandomizedSearchCV(rf,
                             param_distributions=param_dist,
                             n_iter=15,
                             cv=5,
                             n_jobs=10,
                             verbose=10)

    # Perform random grid search and extract the best estimator
    _ = clf.fit(Xdev, Y_dev)
    best_estimator = clf.best_estimator_

    return best_estimator

def score_model(best_estimator, Xeval, Y_eval):

    # Calculate the AUC score on the evaluation dataset
    Y_predicted = best_estimator.predict(Xeval)
    roc_auc = roc_auc_score(Y_eval, Y_predicted)

    # Display classification report
    print classification_report(Y_eval,
                                Y_predicted,
                                target_names=["closed", "victory"])
    print "Area under ROC curve: {:0.3f}".format(roc_auc)

    # Plot ROC curve and display AUC score
    rf_probs = best_estimator.predict_proba(Xeval)[:, 1]
    fpr, tpr, thresholds = roc_curve(Y_eval, rf_probs)

    plt.plot(fpr, tpr, lw=1, label='ROC (area = %0.3f)'%(roc_auc))

    plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6), label='Luck')
    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    plt.xlabel('False Positive Rate', fontsize=15)
    plt.ylabel('True Positive Rate', fontsize=15)
    plt.title('Receiver Operating Characteristic (ROC) curve', fontsize=12)
    plt.legend(loc="lower right", frameon = True).get_frame().set_edgecolor('black')
    plt.grid(True, linestyle = 'dotted')
    plt.savefig("Classification_Plot.png")


# Run
if __name__ == "__main__":

    # Create an instance of the wrangler class
    wrangler = Wrangler()

    # Load the filtered data
    rescaled_df = Wrangler.load_from_db("rescaled_data")

    # Rescale non-categorical features
    df = rescaled_df[ rescaled_df.status != "open" ]

    # Extract features and targets for training
    X, Y = extract_features(df)

    # Perform 70/30 development-evaluation split of data
    X_dev, X_eval, Y_dev, Y_eval = train_test_split(X,
                                                    Y,
                                                    train_size=.7,
                                                    random_state=23)

    # Perform feature selection
    Xdev, Xeval = feature_selection(X_dev, Y_dev, X_eval)

    # Perform random grid search of hyperparameter space to determine best estimator
    best_estimator = train_model(Xdev, Y_dev)

    # Display RMSE and return histogram detailing distribution of predictions within 1 and 2 sigma of RMSE
    score_model(best_estimator, Xeval, Y_eval)

    # Export model for app
    with open("models/rf_classifier.pkl", "wb") as f:
        cPickle.dump(best_estimator, f)
