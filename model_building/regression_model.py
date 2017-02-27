# Numerical imports
import pandas as pd
import numpy as np

# Visual imports
import matplotlib.pyplot as plt

# Scikit imports
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.cross_validation import train_test_split
from sklearn.feature_selection import SelectFromModel
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.grid_search import RandomizedSearchCV
from sklearn.metrics import r2_score, mean_squared_error

# Import the wrangler class
from wrangler import Wrangler

# Other imports
import cPickle
import warnings
warnings.filterwarnings('ignore')


def extract_features(df):

    # Extract features for regression and create design matrix and target series
    features_and_targets = df[[u'overview_linkcount',
                               u'letter_body_linkcount',
                               u'title_adjective_count',
                               u'title_polarity',
                               u'title_sentence_count',
                               u'title_subjectivity',
                               u'title_verb_count',
                               u'goal',
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
                               u'signature_rate']].columns.tolist()
    feature_list = [col for col in features_and_targets if (col != "signature_rate")]
    X = df[feature_list]
    Y = df.signature_rate

    return X, Y

def feature_selection(X_dev, Y_dev, X_eval):

    # Perform feature selection
    clf = ExtraTreesRegressor(n_estimators=200)
    _ = clf.fit(X_dev, Y_dev)
    model = SelectFromModel(clf, prefit=True)
    Xdev = model.transform(X_dev)
    Xeval = model.transform(X_eval)

    return Xdev, Xeval

def train_model(Xdev, Ydev):

    # Initialize a gradient boosting regression algorithm with least-squared loss function
    gbr = GradientBoostingRegressor(loss='ls')

    # Define a parameter grid to search over
    param_dist = {"n_estimators": range(100, 550, 50),
                  "max_depth": range(3, 11, 2),
                  "learning_rate": [.03, .1, .3]}

    # Define a randomed grid search class to optimize hyperparameters
    rgn = RandomizedSearchCV(gbr,
                             param_distributions=param_dist,
                             n_iter=15,
                             cv=5,
                             n_jobs=10,
                             verbose=10)

    # Perform random grid search and extract the best estimator
    _ = rgn.fit(Xdev, Y_dev)
    best_estimator = rgn.best_estimator_

    # Fit models for upper and lower confidence interval boundaries
    best_params = best_estimator.get_params()
    alpha=0.975

    upper_gbr = GradientBoostingRegressor(**best_params)
    upper_gbr.set_params(loss="quantile", alpha=alpha)
    print "Fitting upper limit..."
    upper_gbr.fit(Xdev, Y_dev)
    ci_upper = upper_gbr

    lower_gbr = GradientBoostingRegressor(**best_params)
    lower_gbr.set_params(loss="quantile", alpha=1-alpha)
    print "Fitting lower limit..."
    lower_gbr.fit(Xdev, Y_dev)
    ci_lower = lower_gbr

    return best_estimator, ci_upper, ci_lower

def score_model(best_estimator, Xeval, Y_eval):

    # Calculate the RMSE of the model using the evaluation dataset
    Y_pred = best_estimator.predict(Xeval)
    RMSE = np.sqrt(mean_squared_error(Y_eval, Y_pred))
    print "RMSE score: {}".format(RMSE)

    # Calculate the number of predictions for the evaluation dataset that lie within 1 and 2 sigma of RMSE
    within_rmse = ( (Y_eval - Y_pred) / RMSE )
    onesigma = 100 * within_rmse[ abs(within_rmse) <= 1].count() * 1.0 / within_rmse.count()
    twosigma = 100 * within_rmse[ abs(within_rmse) <= 2].count() * 1.0 / within_rmse.count()
    within_rmse.hist(bins=75)
    plt.xlim(-2, 2)
    plt.xlabel(r"$(Y_{true}-Y_{pred})/RMSE$", fontsize=25)
    plt.xticks(fontsize=12)
    plt.ylabel("Petition Count", fontsize=15)
    plt.yticks(fontsize=12)
    plt.savefig("Regression_Plot.png")

# Run
if __name__ == "__main__":

    # Create an instance of the wrangler class
    wrangler = Wrangler()

    # Load the filtered data
    rescaled_df = Wrangler.load_from_db("rescaled_data")

    # Extract features and targets for training
    X, Y = extract_features(rescaled_df)

    # Perform 70/30 development-evaluation split of data
    X_dev, X_eval, Y_dev, Y_eval = train_test_split(X,
                                                    Y,
                                                    train_size=.7,
                                                    random_state=23)

    # Perform feature selection
    Xdev, Xeval = feature_selection(X_dev, Y_dev, X_eval)

    # Perform random grid search of hyperparameter space to determine best estimator
    best_estimator, ci_upper, ci_lower = train_model(Xdev, Y_dev)

    # Display RMSE and return histogram detailing distribution of predictions within 1 and 2 sigma of RMSE
    score_model(best_estimator, Xeval, Y_eval)

    # Export models for app
    with open("models/gbr.pkl", "wb") as f:
        cPickle.dump(best_estimator, f)
    with open("models/gbr_upper.pkl", "wb") as f:
        cPickle.dump(ci_upper, f)
    with open("models/gbr_lower.pkl", "wb") as f:
        cPickle.dump(ci_lower, f)
