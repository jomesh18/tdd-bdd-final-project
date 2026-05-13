# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """It should Read a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        new_product = Product.find(product.id)
        self.assertEqual(str(product), f"<Product {product.name} id=[{product.id}]>")
        self.assertTrue(new_product is not None)
        self.assertEqual(product.id, new_product.id)
        self.assertEqual(product.name, new_product.name)
        self.assertEqual(product.description, new_product.description)
        self.assertEqual(product.available, new_product.available)
        self.assertEqual(product.price, new_product.price)
        self.assertEqual(product.category, new_product.category)

    def test_update_a_product(self):
        """It should update a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        old_id = product.id
        product.description = 'new description'
        product.update()
        self.assertEqual(product.description, 'new description')
        self.assertEqual(product.id, old_id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        fetched_product = products[0]
        self.assertEqual(product.description, fetched_product.description)
        self.assertEqual(product.id, fetched_product.id)

    def test_delete_a_product(self):
        """It should delete a product"""
        product = ProductFactory()
        product.create()
        products = Product.all()
        self.assertEqual(len(products), 1)
        product.delete()
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_show_all_product(self):
        """It should show all products"""
        products = Product.all()
        self.assertEqual(len(products), 0)
        for _ in range(5):
            ProductFactory().create()
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_product_by_name(self):
        """It should find product by name"""
        for _ in range(5):
            ProductFactory().create()
        products = Product.all()
        product_name = products[0].name
        count = sum(1 for product in products if product.name == product_name)
        fetched_products = Product.find_by_name(product_name)
        self.assertEqual(fetched_products.count(), count)
        for product in fetched_products:
            self.assertEqual(product.name, product_name)

    def test_find_product_by_availability(self):
        """It should find product by availability"""
        for _ in range(10):
            ProductFactory().create()
        products = Product.all()
        product_availability = products[0].available
        count = sum(1 for product in products if product.available == product_availability)
        fetched_products = Product.find_by_availability(product_availability)
        self.assertEqual(fetched_products.count(), count)
        for product in fetched_products:
            self.assertEqual(product.available, product_availability)

    def test_find_product_by_category(self):
        """It should find product by category"""
        for _ in range(10):
            ProductFactory().create()
        products = Product.all()
        product_category = products[0].category
        count = sum(1 for product in products if product.category == product_category)
        fetched_products = Product.find_by_category(product_category)
        self.assertEqual(fetched_products.count(), count)
        for product in fetched_products:
            self.assertEqual(product.category, product_category)

    def test_update_without_id(self):
        """ update without id """
        product = ProductFactory()
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_invalid_boolean_type(self):
        """ Invalid attribute """
        product = ProductFactory()
        data = product.serialize()
        data['category'] = 'invalid_category'
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_type_error(self):
        """ Type error """
        product = ProductFactory()
        data = None
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_invalid_boolean_error(self):
        """ Invalid boolean """
        product = ProductFactory()
        data = product.serialize()
        data['available'] = 'yes'
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_find_by_price_string_price(self):
        """It should find product by price"""
        for _ in range(5):
            ProductFactory().create()
        products = Product.all()
        product_price = products[0].price
        count = sum(1 for product in products if product.price == product_price)
        fetched_products = Product.find_by_price(str(product_price))
        self.assertEqual(fetched_products.count(), count)
        for product in fetched_products:
            self.assertEqual(product.price, product_price)
