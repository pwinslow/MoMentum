# Mo'Mentum:
## Optimize your momentum for social change

This repo stores the codebase for Mo'mentum, an app I built during a 3 week
sprint as a fellow in the [insight data science program](http://insightdatascience.com/).

Mo'mentum helps [change.org](http://www.change.org) users optimize their petition writing skills
by predicting both the overall probability and time scale of success of a given petition based on
features extracted from user-generated text. Mo'mentum is hosted on AWS and the live version can
be found [here](http://www.pwinslow.com). The backend is built entirely in python while the frontend
was built with a combination of python, javascript, and bootstrap.

## Getting Started

These instructions will allow you to run a copy of the Mo'Mentum app on your local machine.

### Prerequisites

The easiest way to run Mo'mentum is by first installing the [Anaconda python distribution](https://anaconda.org/). After that,
all dependencies are listed in the environment.yml file. To create and source a conda environment with these dependencies, run
```
conda env create -f environment.yml
source activate MoMentum
```
from within the local folder that the repo was forked to.

### Local Deployment

To deploy MoMentum on your local host, run
```
python run.py
```
from the MoMentumApp folder. If deploying on a hosting service, e.g., AWS, replace `app.run(debug = True)` with
 `app.run('0.0.0.0', debug = True)` in the run.py file in the MoMentumApp folder before running gunicorn or any similar service.
