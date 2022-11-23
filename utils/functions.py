from sklearn.ensemble import RandomForestClassifier
import pickle
from datetime import datetime
import pandas as pd
import os

train_data = '../data/train.csv'
test_data = '../data/test.csv'

filename = 'model_'

model_path = '../models/'