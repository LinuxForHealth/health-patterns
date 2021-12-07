from flask import Flask, request, make_response, jsonify
from datetime import datetime
import logging
import subprocess
import tempfile
import os

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

@app.route("/healthcheck", methods=['GET'])
def healthcheck():
    now = datetime.now()
    current_time_date = now.strftime("%Y-%m-%d %H:%M:%S")
    return generate_response(200, {"message": "FHIR Data Quality (Deequ) service is running..." + current_time_date + "GMT"})

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

@app.route("/", methods=['POST'])
def run_deequ():

  with tempfile.NamedTemporaryFile() as f: 
    f.write(request.data)

    bashCommand = ("/fhir-data-quality/spark/bin/spark-submit "
                   "--master " 
                   "local[*] "
                   "--class org.alvearie.Main "
                   "/fhir-data-quality/fhir-data-quality.jar "
                   "dataPath="+f.name+" "
                   "dqConfigPath=/fhir-data-quality/config/defaultDataQualityConfig.json"
                   )
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    try:
      output, error = process.communicate(timeout=REQUEST_TIMEOUT)
    except subprocess.TimeoutExpired:
      process.kill()
      return make_response("Timeout processing Spark request.", 408)

  if error is not None:
      return make_response(str(error),400)

  output=output.decode("utf-8")
  results=""
  match=False
  for line in output.splitlines():
    if "Running" in line:
      match=True
    if match:
      results+=line+"\n"
  
  response = make_response(results, 200)
  response.mimetype = "text/plain"
  return response

if __name__ == '__main__':
   app.run(host='0.0.0.0')