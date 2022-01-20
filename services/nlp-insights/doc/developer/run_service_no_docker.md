# Running the service outside of a docker container
It is recommended that the service be deployed as a docker container, following the instructions [here](../examples/setup/start_nlp_insights.md). However you can run it outside of docker if you need to.

1. Build and install nlp-insights to a virtual environment  
    `./gradlew install`
   
1. Switch to the [virtual env](https://docs.python.org/3/library/venv.html) where nlp-insights is installed  
   `source ./build/venv/bin/activate`  
   
1. Set the FLASK_APP environment variable to the installed package  
    `export FLASK_APP=nlp_insights.app`
    
1. Start the service (5000 is the default port, however this value can be changed to suit your needs)  
   `python -m flask run --port=5000`