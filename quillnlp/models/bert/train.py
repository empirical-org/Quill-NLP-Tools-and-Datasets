import os
from typing import List, Dict

import torch
import numpy as np
from tqdm import tqdm_notebook as tqdm, trange
from torch.utils.data import DataLoader

from pytorch_transformers.optimization import AdamW, WarmupLinearSchedule
from pytorch_transformers.modeling_bert import BertModel


def warmup_linear(x, warmup=0.002):
    if x < warmup:
        return x/warmup
    return 1.0 - x


def train(model: BertModel, train_dataloader: DataLoader, dev_dataloader: DataLoader,
          batch_size, gradient_accumulation_steps, device, num_train_epochs=20,
          warmup_proportion=0.1, learning_rate=1e-5, patience=5,
          output_dir="/tmp/", model_file_name="model.bin"):

    output_model_file = os.path.join(output_dir, model_file_name)

    num_train_steps = int(len(train_dataloader.dataset) / batch_size / gradient_accumulation_steps * num_train_epochs)

    param_optimizer = list(model.named_parameters())
    no_decay = ['bias', 'LayerNorm.bias', 'LayerNorm.weight']
    optimizer_grouped_parameters = [
        {'params': [p for n, p in param_optimizer if not any(nd in n for nd in no_decay)], 'weight_decay': 0.01},
        {'params': [p for n, p in param_optimizer if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
        ]

    optimizer = AdamW(optimizer_grouped_parameters, lr=learning_rate, correct_bias=False)
    scheduler = WarmupLinearSchedule(optimizer, warmup_steps=100, t_total=num_train_steps)

    global_step = 0
    loss_history = []
    best_epoch = 0
    for epoch in trange(int(num_train_epochs), desc="Epoch"):

        model.train()
        tr_loss = 0
        for step, batch in enumerate(tqdm(train_dataloader, desc="Training iteration")):
            batch = tuple(t.to(device) for t in batch)
            input_ids, input_mask, segment_ids, label_ids = batch
            outputs = model(input_ids, segment_ids, input_mask, label_ids)
            loss = outputs[0]

            if gradient_accumulation_steps > 1:
                loss = loss / gradient_accumulation_steps

            loss.backward()

            tr_loss += loss.item()

            if (step + 1) % gradient_accumulation_steps == 0:
                lr_this_step = learning_rate * warmup_linear(global_step / num_train_steps, warmup_proportion)
                for param_group in optimizer.param_groups:
                    param_group['lr'] = lr_this_step
                optimizer.step()
                optimizer.zero_grad()
                global_step += 1

        dev_loss, _, _ = evaluate(model, dev_dataloader, device)

        print("Loss history:", loss_history)
        print("Dev loss:", dev_loss)

        if len(loss_history) == 0 or dev_loss < min(loss_history):
            model_to_save = model.module if hasattr(model, 'module') else model
            torch.save(model_to_save.state_dict(), output_model_file)
            best_epoch = epoch

        if epoch - best_epoch >= patience:
            print("No improvement on development set. Finish training.")
            break

        loss_history.append(dev_loss)

    return output_model_file


def evaluate(model: BertModel, dataloader: DataLoader, device: str) -> (int, List[int], List[int]):

    model.eval()

    eval_loss = 0
    nb_eval_steps = 0
    predicted_labels, correct_labels = [], []

    for step, batch in enumerate(tqdm(dataloader, desc="Evaluation iteration")):
        batch = tuple(t.to(device) for t in batch)
        input_ids, input_mask, segment_ids, label_ids = batch

        with torch.no_grad():
            tmp_eval_loss, logits = model(input_ids, segment_ids, input_mask, label_ids)

        outputs = np.argmax(logits.to('cpu'), axis=1)
        label_ids = label_ids.to('cpu').numpy()

        predicted_labels += list(outputs)
        correct_labels += list(label_ids)

        eval_loss += tmp_eval_loss.mean().item()
        nb_eval_steps += 1

    eval_loss = eval_loss / nb_eval_steps

    correct_labels = np.array(correct_labels)
    predicted_labels = np.array(predicted_labels)

    return eval_loss, correct_labels, predicted_labels

