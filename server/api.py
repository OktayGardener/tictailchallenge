# -*- coding: utf-8 -*-

from __future__ import print_function
from flask import Blueprint, current_app, jsonify
from flask_cors import CORS, cross_origin
import pandas as pd
import numpy as np
import sys

api = Blueprint('api', __name__)
CORS(api)

def data_path(filename):
    data_path = current_app.config['DATA_PATH']
    return u"%s/%s" % (data_path, filename)

@api.before_app_first_request
def parse_csv_files():
    load_data()
    print(current_app.shops.head(), file=sys.stderr)

def load_data():
    current_app.shops = pd.read_csv(data_path('shops.csv'))
    current_app.products = pd.read_csv(data_path('products.csv'))
    current_app.tags = pd.read_csv(data_path('tags.csv'))
    current_app.taggings = pd.read_csv(data_path('taggings.csv'))



@api.route('/search', methods=['GET'])
def search():
    return jsonify({'products': ['hej']})
