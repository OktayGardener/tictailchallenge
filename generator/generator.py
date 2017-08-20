"""Backend recruiting task data generator.

Usage:
  generator.py

"""
from __future__ import division
import random
import math
import csv
import uuid

from docopt import docopt
from faker import Faker


STOCKHOLM = 18.0649000, 59.3325800
RADIUS = 20000

# Since we're dealing with coordinates we need to convert the radius value to degreers
# as if we're near the equator.
RADIUS_IN_DEGREES = RADIUS / 111300

NUM_SHOPS = 10000
NUM_PRODUCTS_PER_STORE = [5, 10]
NUM_TAGS_PER_STORE = [2, 4]


with open('products.txt', 'r') as fd:
    uniques = (set(line.decode('utf-8').strip() for line in fd.readlines()))
    PRODUCTS = list(uniques)


TAGS = [
    'kids',
    'men',
    'women',
    'clothes',
    'fashion',
    'kitchenware',
    'home',
    'shirts',
    'trousers',
    'scandinavian',
    'formal',
    'casual',
    'cool',
    'livingroom',
    'underwear',
    'tops',
    'outerwear',
    'knits',
    'accessories',
    'lights',
    'plates',
    'cutlery',
    'paintings',
    'posters',
    'sweaters',
    'knitwear'
]


faker = Faker()


class Generator(object):
    fields = []

    def __init__(self, *args):
        for i, field in enumerate(self.fields):
            setattr(self, field, args[i])

    def to_dict(self):
        d = {}
        for f in self.fields:
            v = getattr(self, f)
            if isinstance(v, unicode):
                v = v.encode('utf-8')
            d[f] = v
        return d


class Tag(Generator):
    fields = ['id', 'tag']

    @classmethod
    def generate(cls, tag):
        return Tag(uuid.uuid4().hex, tag)


class Shop(Generator):
    fields = ['id', 'name', 'lat', 'lng']

    @classmethod
    def get_coords(cls):
        x0, y0 = STOCKHOLM
        u, v = random.betavariate(1, 5), random.uniform(0, 1)
        w = RADIUS_IN_DEGREES * u
        t = 2 * math.pi * v
        x = (w * math.cos(t)) / math.cos(y0)
        y = w * math.sin(t)
        return x + x0, y + y0

    @classmethod
    def generate(cls):
        name = faker.company()
        lng, lat = cls.get_coords()
        return Shop(uuid.uuid4().hex, name, lat, lng)


class Product(Generator):
    fields = ['id', 'shop_id', 'title', 'popularity', 'quantity']

    @classmethod
    def generate(cls, shop):
        title = random.choice(PRODUCTS)
        popularity = u"%.3f" % random.uniform(0, 1)
        quantity = random.randint(0, 10)
        return Product(uuid.uuid4().hex, shop.id, title, popularity, quantity)

    @classmethod
    def generate_many(cls, shop, count):
        return [cls.generate(shop) for _ in range(count)]


class Tagging(Generator):
    fields = ['id', 'shop_id', 'tag_id']

    @classmethod
    def generate(cls, shop, tag):
        return Tagging(uuid.uuid4().hex, shop.id, tag.id)

    @classmethod
    def generate_many(cls, shop, tags):
        return [cls.generate(shop, tag) for tag in tags]


def main():
    tags, shops, products, taggings = [], [], [], []

    for tag in TAGS:
        tags.append(Tag.generate(tag))

    random.shuffle(tags)

    for _ in xrange(NUM_SHOPS):
        shops.append(Shop.generate())

    random.shuffle(shops)

    for shop in shops:
        np = random.randint(*NUM_PRODUCTS_PER_STORE)
        products.extend(Product.generate_many(shop, np))

        nt = random.randint(*NUM_TAGS_PER_STORE)
        sample_tags = random.sample(tags, nt)
        taggings.extend(Tagging.generate_many(shop, sample_tags))

    random.shuffle(products)
    random.shuffle(taggings)

    write_spec = (
        ('../data/shops.csv', Shop, shops),
        ('../data/tags.csv', Tag, tags),
        ('../data/products.csv', Product, products),
        ('../data/taggings.csv', Tagging, taggings),
    )

    for path, klass, collection in write_spec:
        with open(path, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=klass.fields)
            writer.writeheader()
            for thing in collection:
                writer.writerow(thing.to_dict())


if __name__ == '__main__':
    args = docopt(__doc__, version='0.01')
    main()
