import arrow
import csv
import json
import os
import redis
from collections import namedtuple
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename

redis_con = redis.Redis()

UPLOAD_FOLDER = '/root/steven/csv_directory'
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        upload_file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if upload_file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if upload_file and allowed_file(upload_file.filename):
            filename = secure_filename(str(arrow.utcnow().timestamp))
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            upload_file.save(file_path)
            csv_data = csv.reader(open(file_path, 'r'))
            csv_class = None
            for each_csv in csv_data:
                if not csv_class:
                    attributes = ' '.join(each_csv)
                    csv_class = namedtuple('csv_class', attributes)
                else:
                    csv_obj = csv_class(*each_csv)
                    # print(csv_obj)
                    time_str = '%s %s' % (csv_obj.Date, csv_obj.Time)
                    date_str = '%s' % (csv_obj.Date)
                    time_obj = arrow.get(time_str, 'M/D/YYYY H:m')
                    date_obj = arrow.get(date_str, 'M/D/YYYY')
                    if 'add' in csv_obj.Status.lower():
                        data_str = redis_con.hget('1900-'+str(date_obj), csv_obj.ID)
                        if not data_str:
                            data = json.dumps({
                                'phone': csv_obj.Phone,
                                'time': [time_str]
                            })
                        else:
                            data_json = json.loads(data_str.decode('utf-8'))
                            data_json['phone'] = csv_obj.Phone
                            data_json['time'].append(time_str)
                            data_json['time'] = list(set(data_json['time']))
                            data = json.dumps(data_json)
                        redis_con.hset(str(time_obj), csv_obj.ID, data)
                        redis_con.hset('1900-'+str(date_obj), csv_obj.ID, data)
                    if 'del' in csv_obj.Status.lower():
                        redis_con.hdel(str(time_obj), csv_obj.ID)
                        redis_con.hdel('1900-'+str(date_obj), csv_obj.ID)
            os.remove(file_path)
            return '''File uploaded successfully'''
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
