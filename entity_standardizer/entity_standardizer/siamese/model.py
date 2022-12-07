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

import torch.nn as nn
from transformers import AutoModel, AutoTokenizer
import transformers
transformers.utils.logging.set_verbosity_error()

class Model(nn.Module):
    def __init__(self, params):
        super().__init__()
        self.backbone = params["model"].get("backbone", "prajjwal1/bert-small")
        self.tokenizer = AutoTokenizer.from_pretrained(self.backbone)
        self.encoder = AutoModel.from_pretrained(self.backbone)

    def forward(self, inputs, device):
        inputs = self.tokenizer(inputs, padding=True, return_tensors='pt')
        inputs = inputs.to(device)
        outputs = self.encoder(**inputs)
        cls = outputs.last_hidden_state[:,0,:]
        del inputs
        return cls