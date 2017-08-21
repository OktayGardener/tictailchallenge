# -*- coding: utf-8 -*-

from __future__ import print_function
from collections import defaultdict
from flask import Blueprint, current_app, jsonify, request
from flask_cors import CORS, cross_origin
import pandas as pd
import numpy as np
import sys
import math

api = Blueprint('api', __name__)
CORS(api)

@api.before_app_first_request
def parse_csv_files():
    load_data()

def data_path(filename):
    data_path = current_app.config['DATA_PATH']
    return u"%s/%s" % (data_path, filename)

def load_data():
    current_app.shops = pd.read_csv(data_path('shops.csv'), index_col=0)
    current_app.products = pd.read_csv(data_path('products.csv'), index_col=0)
    current_app.tags = pd.read_csv(data_path('tags.csv'), index_col=0)
    current_app.taggings = pd.read_csv(data_path('taggings.csv')).reset_index()
    current_app.taggings.drop(['id'], axis=1, inplace=True)

def item_request_query(count, radius, lat, lng, tags=None):
    current_app.shops['dist'] = haversine_np(lng, lat,
    current_app.shops['lng'], current_app.shops['lat'])

    shops = current_app.shops[current_app.shops['dist'] < radius]
    closest_shops = shops.sort_values(['dist'], ascending=False).index.tolist()

    if tags:
        closest_shops = filter_items_tags(closest_shops, tags)

    items = most_popular_items(closest_shops, count)

    return items['title'].tolist()

def most_popular_items(shops, n):
    items = current_app.products[current_app.products['shop_id'].isin(shops)]
    popular = items.sort_values(['popularity'], ascending=False)
    return popular.head(n)

def filter_items_tags(shops, tags):
    if len(current_app.tags['tag'].isin(tags)) == 0:
        return shops
    else:
        tag_ids = current_app.tags[current_app.tags['tag'].isin(tags)].index.tolist()
        shop_tag_ids = current_app.taggings[current_app.taggings['shop_id'].isin(shops)]
        shops_with_tags = shop_tag_ids[shop_tag_ids['tag_id'].isin(tag_ids)].shop_id.tolist()
        if len(shops_with_tags) == 0:
            return shops
        return shops_with_tags

def haversine_np(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2

    c = 2 * np.arcsin(np.sqrt(a))
    m = 6367 * c * 1000
    return m

def validate_request(args):
    valid_args = defaultdict()
    params = [('count', int), ('lat', float), ('lng', float), ('radius', int)]

    for param, dtype in params:
        try:
            valid_args[param] = args.get(param, type=dtype)
        except ValueError:
            pass
    tags = args.get('tags', None)
    if tags:
        valid_args['tags'] = map(lambda tag: tag.strip(), tags.split(','))
    return valid_args

@api.route('/search', methods=['GET'])
def search():
    params = validate_request(request.args)
    print(params)
    items = item_request_query(**params)
    print(items)
    return jsonify({'products': items})
