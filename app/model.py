import numpy as np
import pandas as pd
import transformers
import torch
from torch.utils.data import Dataset, DataLoader, RandomSampler, SequentialSampler
from transformers import BertTokenizer, BertModel, BertConfig, BertTokenizerFast
from torch import cuda


class BERTClass(torch.nn.Module):
    def __init__(self):
        super(BERTClass, self).__init__()
        self.l1 = BertModel.from_pretrained("allenai/scibert_scivocab_uncased")
        self.dropout = torch.nn.Dropout(0.0)
        self.classifier = torch.nn.Linear(768, 124)

    def forward(self, ids, mask, token_type_ids):
        _, output_1= self.l1(ids, attention_mask = mask, token_type_ids = token_type_ids, return_dict=False)
        output_2 = self.dropout(output_1)
        output = self.classifier(output_2)
        return output


device = 'cuda' if cuda.is_available() else 'cpu'
tokenizer = BertTokenizerFast.from_pretrained(
    'allenai/scibert_scivocab_uncased')
max_len = 403
model = BERTClass()
model.to(device)
model.load_state_dict(torch.load('checkpoint.bin'))

from datasets import load_dataset
dataset = load_dataset("Javtor/biomedical-topic-categorization-validation")
data = dataset['validation'].to_pandas()
data.drop(['PMID'], inplace=True, axis=1)
data.drop(['MeshTerms'], inplace=True, axis=1)
df_onehot = pd.concat([data.drop('SemanticTypes', 1), data['SemanticTypes'].str.get_dummies(sep=";")], 1)

stypes = list(df_onehot.columns)
stypes.pop(0)
new_df = pd.DataFrame()
new_df['text'] = df_onehot['Title/Abstract']
new_df['labels'] = df_onehot.iloc[:, 1:].values.tolist()

typenames = pd.read_csv('STY_CNT_Full_dataset.tsv', sep=',')
typenames = dict(zip(typenames['Semantic Types'], typenames['Preferred Label']))

def predict(text):
    model.eval()
    fin_outputs = []
    text = str(text)
    text = " ".join(text.split())
    inputs = tokenizer.encode_plus(
        text,
        None,
        truncation=True,
        add_special_tokens=True,
        max_length=max_len,
        pad_to_max_length=True,
        return_token_type_ids=True
    )
    ids = torch.tensor(inputs['input_ids'], dtype=torch.long).unsqueeze(0).to(
        device, dtype=torch.long)
    mask = torch.tensor(inputs['attention_mask'], dtype=torch.long).unsqueeze(0).to(
        device, dtype=torch.long)
    token_type_ids = torch.tensor(
        inputs["token_type_ids"], dtype=torch.long).unsqueeze(0).to(device, dtype=torch.long)
    with torch.no_grad():
        outputs = model(ids, mask, token_type_ids)
        fin_outputs.extend(torch.sigmoid(
            outputs).cpu().detach().numpy().tolist())
        final_outputs = np.array(fin_outputs) >=0.5
        final_outputs = final_outputs[0].tolist()
        semantic_types = []
        for i in range(124):
          if final_outputs[i]:
            semantic_types.append(stypes[i]+' - '+typenames[stypes[i]])
    return final_outputs, semantic_types
