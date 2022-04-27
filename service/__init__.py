# *****************************************************************
# Copyright IBM Corporation 2021
# Licensed under the Eclipse Public License 2.0, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# *****************************************************************



import os
import sys
import logging
from flask import Flask

import shutil
from pathlib import Path
from flask import Flask, render_template

app = Flask(__name__)
app.config.from_object('config')

# Set up logging
if __name__ != '__main__':
        app.logger.setLevel(logging.INFO)
        ch = app.logger.handlers[0]
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(filename)s:%(lineno)s - %(message)s")
        ch.setFormatter(formatter)

app.logger.info(70 * '*')
app.logger.info('  Runtime Graph API  '.center(70, '*'))
app.logger.info(70 * '*')

# Load the routes
import service.routes
