from os.path import exists
from syne_tune.report import Reporter
from argparse import ArgumentParser
from torch import cuda
from transformers import BertTokenizer, BertModel, DistilBertTokenizer, DistilBertModel
from torch.utils.data import Dataset, DataLoader, RandomSampler, SequentialSampler
import torch
from sklearn import metrics
from tqdm import tqdm
import pandas as pd
import numpy as np
import warnings
warnings.simplefilter('ignore')

def hamming_score(y_true, y_pred):
    acc_list = []
    for i in range(y_true.shape[0]):
        set_true = set(np.where(y_true[i])[0])
        set_pred = set(np.where(y_pred[i])[0])
        tmp_a = None
        if len(set_true) == 0 and len(set_pred) == 0:
            tmp_a = 1
        else:
            tmp_a = len(set_true.intersection(set_pred)) /\
                float(len(set_true.union(set_pred)))
        acc_list.append(tmp_a)
    return np.mean(acc_list)


def load_dataset(sample_frac):
    print("loading dataset...")
    data = pd.read_csv('final_dataset.tsv', sep='\t')
    data.drop(['PMID'], inplace=True, axis=1)
    data.drop(['MeshTerms'], inplace=True, axis=1)
    df_onehot = pd.concat([data.drop('SemanticTypes', 1),
                          data['SemanticTypes'].str.get_dummies(sep=";")], 1)
    new_df = pd.DataFrame()
    new_df['text'] = df_onehot['Title/Abstract']
    new_df['labels'] = df_onehot.iloc[:, 1:].values.tolist()
    print("dataset loaded!")

    print("sampling dataset...")
    df = new_df.sample(frac=sample_frac, random_state=200)
    df = df.reset_index(drop=True)
    print("dataset sampled!")

    return df


def get_train_test(df):
    train_size = 0.8
    train_data = df.sample(frac=train_size, random_state=200)
    test_data = df.drop(train_data.index).reset_index(drop=True)
    train_data = train_data.reset_index(drop=True)
    return train_data, test_data


class MultiLabelDataset(Dataset):

    def __init__(self, dataframe, tokenizer, max_len):
        self.tokenizer = tokenizer
        self.data = dataframe
        self.text = dataframe.text
        self.targets = self.data.labels
        self.max_len = max_len

    def __len__(self):
        return len(self.text)

    def __getitem__(self, index):
        text = str(self.text[index])
        text = " ".join(text.split())

        inputs = self.tokenizer.encode_plus(
            text,
            None,
            truncation=True,
            add_special_tokens=True,
            max_length=self.max_len,
            pad_to_max_length=True,
            return_token_type_ids=True
        )
        ids = inputs['input_ids']
        mask = inputs['attention_mask']
        token_type_ids = inputs["token_type_ids"]

        return {
            'ids': torch.tensor(ids, dtype=torch.long),
            'mask': torch.tensor(mask, dtype=torch.long),
            'token_type_ids': torch.tensor(token_type_ids, dtype=torch.long),
            'targets': torch.tensor(self.targets[index], dtype=torch.float)
        }


class BERTClass(torch.nn.Module):
    def __init__(self, model_name, dropout_rate, pre_classifier_size):
        super(BERTClass, self).__init__()
        self.l1 = BertModel.from_pretrained(model_name)
        bert_out = 1024 if "large" in model_name else 768
        self.dropout = torch.nn.Dropout(dropout_rate)
        self.classifier = torch.nn.Linear(bert_out, 124)

    def forward(self, ids, mask, token_type_ids):
        _, output_1 = self.l1(ids, attention_mask=mask,
                              token_type_ids=token_type_ids, return_dict=False)
        output_2 = self.dropout(output_1)
        output = self.classifier(output_2)
        return output


class DistilBERTClass(torch.nn.Module):
    def __init__(self, model_name, dropout_rate, pre_classifier_size):
        super(DistilBERTClass, self).__init__()
        self.l1 = DistilBertModel.from_pretrained(model_name)
        bert_out = 1024 if "large" in model_name else 768
        self.pre_classifier = torch.nn.Linear(bert_out, bert_out)
        self.dropout = torch.nn.Dropout(dropout_rate)
        self.classifier = torch.nn.Linear(bert_out, 124)

    def forward(self, input_ids, attention_mask, token_type_ids):
        output_1 = self.l1(input_ids=input_ids, attention_mask=attention_mask)
        hidden_state = output_1[0]
        pooler = hidden_state[:, 0]
        pooler = self.pre_classifier(pooler)
        pooler = torch.nn.Tanh()(pooler)
        pooler = self.dropout(pooler)
        output = self.classifier(pooler)
        return output


def loss_fn(outputs, targets):
    return torch.nn.BCEWithLogitsLoss()(outputs, targets)


def train(epoch, model, training_loader, optimizer, device, model_name, save):
    model.train()
    for _, data in tqdm(enumerate(training_loader, 0)):
        ids = data['ids'].to(device, dtype=torch.long)
        mask = data['mask'].to(device, dtype=torch.long)
        token_type_ids = data['token_type_ids'].to(device, dtype=torch.long)
        targets = data['targets'].to(device, dtype=torch.float)

        outputs = model(ids, mask, token_type_ids)

        optimizer.zero_grad()
        loss = loss_fn(outputs, targets)
        if _ % 1000 == 0:
            print(f'Epoch: {epoch}, Loss:  {loss.item()}')
            # if save:
            #   torch.save(model.state_dict(), model_name+'.bin')
        loss.backward()
        optimizer.step()


def validation(testing_loader, model):
    model.eval()
    fin_targets = []
    fin_outputs = []
    with torch.no_grad():
        for _, data in tqdm(enumerate(testing_loader, 0)):
            ids = data['ids'].to(device, dtype=torch.long)
            mask = data['mask'].to(device, dtype=torch.long)
            token_type_ids = data['token_type_ids'].to(
                device, dtype=torch.long)
            targets = data['targets'].to(device, dtype=torch.float)
            outputs = model(ids, mask, token_type_ids)
            fin_targets.extend(targets.cpu().detach().numpy().tolist())
            fin_outputs.extend(torch.sigmoid(
                outputs).cpu().detach().numpy().tolist())
    return fin_outputs, fin_targets


def validate(targets, outputs):
    accuracy = metrics.accuracy_score(targets, outputs)
    f1_score_micro = metrics.f1_score(targets, outputs, average='micro')
    f1_score_macro = metrics.f1_score(targets, outputs, average='macro')
    val_hamming_loss = metrics.hamming_loss(targets, outputs)
    val_hamming_score = hamming_score(
        np.array(targets), np.array(outputs))

    print(f"Hamming Score = {val_hamming_score}")
    print(f"Accuracy Score = {accuracy}")
    print(f"F1 Score (Micro) = {f1_score_micro}")
    print(f"F1 Score (Macro) = {f1_score_macro}")
    print(f"Hamming Loss = {val_hamming_loss}")
    print()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--lr', type=float, default=3e-05)
    parser.add_argument('--dropout_rate', type=float, default=0.3)
    parser.add_argument('--model_name', type=str,
                        default="distilbert-base-uncased")
    parser.add_argument('--sample_frac', type=float, default=1.0)
    parser.add_argument('--max_len', type=int, default=128)
    parser.add_argument('--pre_classifier_size', type=int, default=768)
    parser.add_argument('--batch_size', type=int, default=8)
    parser.add_argument('--num_workers', type=int, default=8)
    parser.add_argument('--save', type=bool, default=True)
    parser.add_argument('--epochs', type=int, default=10)

    args, _ = parser.parse_known_args()
    report = Reporter()

    device = 'cuda' if cuda.is_available() else 'cpu'
    tokenizer = DistilBertTokenizer.from_pretrained(
        args.model_name) if "distilbert" in args.model_name else BertTokenizer.from_pretrained(args.model_name)

    df = load_dataset(args.sample_frac)
    train_data, test_data = get_train_test(df)

    print("FULL Dataset: {}".format(df.shape))
    print("TRAIN Dataset: {}".format(train_data.shape))
    print("TEST Dataset: {}".format(test_data.shape))

    training_set = MultiLabelDataset(train_data, tokenizer, args.max_len)
    testing_set = MultiLabelDataset(test_data, tokenizer, args.max_len)

    model = DistilBERTClass(args.model_name, args.dropout_rate, args.pre_classifier_size) if "distilbert" in args.model_name else BERTClass(
        args.model_name, args.dropout_rate, args.pre_classifier_size)
    model.to(device)

    optimizer = torch.optim.Adam(params=model.parameters(), lr=args.lr)

    train_params = {'batch_size': args.batch_size,
                    'shuffle': True,
                    'num_workers': args.num_workers,

                    }

    test_params = {'batch_size': args.batch_size,
                   'shuffle': True,
                   'num_workers': args.num_workers,

                   }

    training_loader = DataLoader(training_set, **train_params)
    testing_loader = DataLoader(testing_set, **test_params)

    # if not exists(args.model_name+'.bin') and args.save:
    #     torch.save(model.state_dict(), args.model_name+'.bin')

    # if args.save:
    #     model.load_state_dict(torch.load(args.model_name+'.bin'))

    print("Starting Training!")
    for epoch in range(1, args.epochs+1):
        train(epoch, model, training_loader,
              optimizer, device, args.model_name, True)

        outputs, targets = validation(testing_loader, model)
        final_outputs = np.array(outputs) >= 0.5
        validate(targets, final_outputs)
        val_acc = metrics.f1_score(targets, final_outputs, average='micro')
        report(epoch=epoch, val_acc=val_acc)
