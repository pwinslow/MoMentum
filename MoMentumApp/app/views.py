from flask import render_template, request
from app import app
import cPickle
import pandas as pd
from fetcher import fetch
from constants import clf_feature_list, goal_mean, goal_std
from build_features import json_to_features, fit_daycount


# Load models
with open("models/rf_classifier.pkl", "rb") as f:
	rf_classifier = cPickle.load(f)
with open("models/gbr.pkl", "rb") as f:
    gbr = cPickle.load(f)
with open("models/gbr_upper.pkl", "rb") as f:
    gbr_upper = cPickle.load(f)


@app.route('/')
@app.route('/index')
def index():
	return render_template("input.html")

@app.route('/input')
def cities_input():	#AKA input_sentence
	return render_template("input.html")

@app.route('/output')
def cities_output():

	url = request.args.get('ID') #The link the user provides
	#petition_json, update_json = fetch(url)
	petition_json = fetch(url)
	#if type(petition_json) == str:
	#	print petition_json
	#else:

	# Make classification prediction
	clf_features = json_to_features(petition_json, clf_feature_list)
	class_pred = rf_classifier.predict_proba(clf_features)[0][1] * 100
	class_pred = int(round(class_pred))

	# Make regression predictions
	goal = petition_json["goal"]
	rescaled_goal = (goal - goal_mean) * 1.0 / goal_std
	daycount = goal * 1.0 / gbr.predict(rescaled_goal)[0]

	lower_daycount = goal * 1.0 / gbr_upper.predict(rescaled_goal)[0]
	upper_daycount = daycount + (daycount - lower_daycount)


	sentence1 = "You have a {:.0f}% chance of victory!".format(class_pred)
	sentence2 = "Signature goal expected within {:.1f} - {:.1f} days!".format(lower_daycount, upper_daycount)
	sentence3 = "Hover over the bar chart below to discover recommendations for improving your score."

	return render_template("output.html",
							sentence1 = sentence1,
							sentence2=sentence2,
							sentence3=sentence3,
							success_probability=class_pred)
