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

FROM registry.access.redhat.com/ubi8/python-38

# Need to be root to install dependencies
USER 0

# Install dependencies before the code
WORKDIR /app

COPY ./benchmarks /app/benchmarks
COPY ./service /app/service
COPY ./config.py /app/config.py
COPY ./planner.py /app/planner.py
COPY ./multiprocessing_mapreduce.py /app/multiprocessing_mapreduce.py
COPY ./kg /app/kg
COPY ./config /app/config
COPY ./entity_standardizer /app/entity_standardizer
RUN  python -m pip install --upgrade pip wheel build setuptools; \
     pip install -r entity_standardizer/requirements.txt; \
     cd entity_standardizer; python -m build; pip install dist/entity_standardizer_tca-1.0-py3-none-any.whl; cd ..; \
     pip install -r service/requirements.txt; \
     python benchmarks/generate_data.py; \
     python benchmarks/run_models.py;
     
RUN chown -R 1001:0 ./

# Become a non-root user again
USER 1001

# Expose any ports the app is expecting in the environment
ENV PORT 8000
EXPOSE $PORT

ENV GUNICORN_BIND 0.0.0.0:$PORT
CMD ["gunicorn", "--workers=2", "--threads=500", "--timeout", "300", "service:app"]
