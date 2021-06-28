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

USER 0
WORKDIR /app

ADD ./service /app/service
ADD ./config.py /app/config.py
ADD ./planner.py /app/planner.py
ADD ./model_objects /app/model_objects
ADD ./ontologies /app/ontologies
ADD ./config.ini /app/config.ini
ADD ./requirements.txt .
RUN chown -R 1001:0 ./
USER 1001

#RUN pip install -r ./requirements.txt
RUN pip install -U "pip>=19.3.1" && \
    pip install -r requirements.txt

# Unit Test
#RUN python -m unittest discover -v -s './service/test' -p 'test_*.py'


# Expose any ports the app is expecting in the environment
ENV PORT 8000
EXPOSE $PORT

ENV GUNICORN_BIND 0.0.0.0:$PORT
CMD ["gunicorn", "--workers=3", "--timeout", "300", "service:app"]
