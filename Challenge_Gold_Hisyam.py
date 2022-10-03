# Import library for Pandas and text cleansing
from io import StringIO
from string import whitespace
import pandas as pd
import re

# Import Database
import sqlite3


# Import library for Flask
from flask import Flask, jsonify
from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

#create flask app
app = Flask(__name__)
app.json_encoder = LazyJSONEncoder
swagger_template = dict(
info = {
    'title': LazyString(lambda: 'API Documentation for Text Cleansing and File Cleansing'),
    'version': LazyString(lambda: '1.0.0'),
    'description': LazyString(lambda: 'Dokumentasi API untuk Text Cleansing dan File Cleansing'),
    },
    host = LazyString(lambda: request.host)
)
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template,             
                  config=swagger_config)

#Fungsi Connect Database
db = sqlite3.connect('GoldChallenge.db', check_same_thread=False)
cur = db.cursor()

#Fungsi Text Cleansing
def text_cleansing(teks):
    phase_one = re.sub(r"[^\x00-\x7F]+",'', teks)
    phase_two = re.sub(r"[^a-zA-Z0-9\s]+",'', phase_one)
    return phase_two

# Fungsi Save data to Database
def database_textpro(input1, input2):
    db = sqlite3.connect("GoldChallenge.db")
    
    cur.execute("""CREATE TABLE IF NOT EXISTS TextProcessing (input varchar(255), result varchar(255))""")
    cur.execute("INSERT INTO TextProcessing (input, result) VALUES ('" + input1 + "', '" + input2 + "')")
    db.commit()
    #cur.close()
    #db.close()
    print("Data Saved to sqlite3")


#Endpoint for text input processing
@swag_from("docs/text-processing.yaml", methods=['GET'])
@app.route('/text-processing', methods=['GET'])

#define text processing function
def text_processing():
    raw_text = request.args.get('raw_text')
    #Json response for successful message
    if raw_text:
        input1 = raw_text
        input2 = text_cleansing(raw_text)
        database_textpro(input1, input2)
        
        json_response = {
              'status_code': 200,
              'description': "Result from text cleansing",
              'data': text_cleansing(raw_text),
          }

        response_data = jsonify(json_response)
        return response_data
    else:
      #Json response for error message
        json_response = {
              'status_code': 400,
              'description': "Text data is null",
          }

        response_data = jsonify(json_response) 
    return response_data

#Endpoint route for file processing
@swag_from("docs/file-processing.yaml", methods=['POST'])
@app.route('/file-processing', methods=['POST'])
#Define file processing function
def file_processing():
    if "file" in request.files:
      file = request.files['file']
      # Save temporary file in server
      file.save("raw.csv")
      df = pd.read_csv("raw.csv",header=None)
      text = df.values.tolist()
      clean_text = []

      for i in text:
        #text_clean = text_cleansing(i[0])
        clean_text.append(text_cleansing(i[0]))
        #db.commit() #insert i & text clean 
        
        
        
      # Json response for successful request
      json_response = {
              'status_code': 200,
              'description': "Result from clean file",
              'data': clean_text,
          }

      response_data = jsonify(json_response)
      return response_data,200
    
    else:
      #Json response for unsuccessful request
      json_response = {
              'status_code': 400,
              'description': "No file inputed",
          }
    return jsonify(json_response),400

if __name__ == '__main__':
    # run app in debug mode on port 4000
    app.run(host='0.0.0.0',debug=True, port=4000)