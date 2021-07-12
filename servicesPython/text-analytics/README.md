NLP Text Analytics
-------------------------------
TO-DO - fill in README

### Running the service
To run the app on its own, from the root directory execute the following:
```bash
export FLASK_APP=text_analytics/app.py
gradle clean build
source build/venv/bin/activate
flask run
```

#### Docker: 
To build the image locally, run `docker build -t text-analytics-flask:latest`

Then run with port 5000 exposed via `docker run -d -p 5000:5000 text-analytics-flask`

Future work will configure gradle to automatically publish the image to a remote repository for deployment

### Using the service
The app currently supports running NLP via two different services, IBM's Annotator for Clinical Data (ACD) and the 
open-source QuickUMLS.  The app defaults to using QuickUMLS, but can be changed using the /configure endpoint. 

TO-DO : table for endpoints, like in deid/terminology