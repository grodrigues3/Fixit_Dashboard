#!/usr/bin/env python

# Copyright 2016 The Kubernetes Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, request, url_for, render_template
from identify_test_ownership import find_tests, split_tests

app = Flask(__name__)
logFile = '/tmp/fixit-dashboard.log'
logSize = 1024*1024*100
k8s_root_dir = '/go/kubernetes'
#k8s_root_dir = '/usr/local/google/home/grod/work/src/k8s.io/kubernetes'

@app.errorhandler(500)
def internal_error(exception):
    return str(exception), 500

@app.route("/", methods=['GET'])
def show_tests():
    #title = request.form.get('title', '')
    #body = request.form.get('body', '')
    fileNames, testNames = find_tests(k8s_root_dir)
    hasOwner, needsOwner, ownerMap = split_tests(fileNames, k8s_root_dir)
    return render_template('simple_home.html', notOwned = needsOwner, owned=ownerMap)


def configure_logger():
    FORMAT = '%(asctime)-20s %(levelname)-10s %(message)s'
    file_handler = RotatingFileHandler(logFile, maxBytes=logSize, backupCount=3)
    formatter = logging.Formatter(FORMAT)
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

if __name__ == "__main__":
    configure_logger()
    app.run(host="0.0.0.0")
