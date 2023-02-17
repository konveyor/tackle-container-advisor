################################################################################
# Copyright IBM Corporation 2021, 2022
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

FROM registry.access.redhat.com/ubi8/python-38

# Need to be root to install dependencies
USER 0

# Install dependencies before the code
WORKDIR /app

COPY ./benchmarks /app/benchmarks
COPY ./service /app/service
COPY ./kg /app/kg
COPY ./config /app/config
COPY ./entity_standardizer /app/entity_standardizer
COPY ./requirements.txt /app/requirements.txt
COPY ./tca_cli.py /app/tca_cli.py
RUN  python -m pip install --upgrade pip wheel build setuptools; \
     pip install -r entity_standardizer/requirements.txt; \
     cd entity_standardizer; python -m build; pip install dist/entity_standardizer_tca-1.0-py3-none-any.whl; cd ..; \
     pip install -r /app/requirements.txt; \
     python benchmarks/generate_data.py; \
     python benchmarks/run_models.py;

RUN chown -R 1001:0 ./

# Become a non-root user again
USER 1001

# Expose any ports the app is expecting in the environment
ENV PORT 8000
EXPOSE $PORT

ENV GUNICORN_BIND 0.0.0.0:$PORT
CMD ["gunicorn", "-c", "config/gunicorn.py", "service:app"]
