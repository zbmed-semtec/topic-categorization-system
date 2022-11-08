from syne_tune.backend import LocalBackend
from syne_tune.optimizer.schedulers import HyperbandScheduler
from syne_tune import Tuner, StoppingCriterion
from syne_tune.config_space import loguniform, randint, uniform, choice

if __name__ == '__main__':
    max_epochs = 8
    config_space = {
        "epochs": max_epochs,
        "lr": loguniform(5e-6, 1e-4),
        "dropout_rate": uniform(0.0, 1.0),
        "model_name": choice(["dmis-lab/biobert-v1.1", "distilbert-base-uncased", "allenai/scibert_scivocab_uncased", "emilyalsentzer/Bio_ClinicalBERT",
                             "bert-base-uncased"]),
        "sample_frac": 0.1,
        "max_len": randint(100,512),
        "pre_classifier_size": 768,
        "batch_size": randint(4,64),
        "num_workers": randint(1,8),
        "save": False,
    }
    scheduler = HyperbandScheduler(
        config_space,
        max_t=max_epochs,
        resource_attr='epoch',
        searcher='bayesopt',
        metric="val_acc",
        mode="max",        
    )

    tuner = Tuner(
        trial_backend=LocalBackend(entry_point="train.py"),
        scheduler=scheduler,
        stop_criterion=StoppingCriterion(max_wallclock_time=388800),
        n_workers=1,
    )

    tuner.run()
