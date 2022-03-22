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
COPY ./service.requirements.txt .
COPY ./aca_entity_standardizer/tfidf/dist/tfidf-1.0-py3-none-any.whl .
COPY ./aca_entity_standardizer/gnn/dist/gnn-1.0-py3-none-any.whl .
RUN python -m pip install --upgrade pip wheel && \
    pip install -r service.requirements.txt
    pip install tfidf-1.0-py3-none-any.whl
    pip install gnn-1.0-py3-none-any.whl

# COPY the code to the working directory
COPY ./service /app/service
COPY ./config.py /app/config.py
COPY ./planner.py /app/planner.py
COPY ./multiprocessing_mapreduce.py /app/multiprocessing_mapreduce.py
COPY ./models /app/models
COPY ./kg /app/kg
COPY ./config /app/config
RUN chown -R 1001:0 ./

# Become a non-root user again
USER 1001

# Expose any ports the app is expecting in the environment
ENV PORT 8000
EXPOSE $PORT

ENV GUNICORN_BIND 0.0.0.0:$PORT
CMD ["gunicorn", "--workers=2", "--threads=500", "--timeout", "300", "service:app"]
