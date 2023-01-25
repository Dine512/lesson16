from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
# from users.users import users_blueprint
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship

# from db import users, offers, orders
from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(20))
    last_name = Column(String(20))
    age = Column(Integer)
    email = Column(String(50))
    role = Column(String(30))
    phone = Column(String(15))

    def __repr__(self):
        return f"{self.id}"


class Offer(db.Model):
    __tablename__ = 'Offers'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("Orders.id"))
    executor_id = Column(Integer, ForeignKey("Users.id"))

    def __repr__(self):
        return f"{self.id}"


class Order(db.Model):
    __tablename__ = 'Orders'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    description = Column(String(500))
    start_date = Column(Date)
    end_date = Column(Date)
    address = Column(String(80))
    price = Column(Integer)
    customer_id = Column(Integer, ForeignKey("Users.id"))
    executor_id = Column(Integer, ForeignKey("Users.id"))
    customers = relationship("User", foreign_keys=[customer_id])
    executor = relationship("User", foreign_keys=[executor_id])

    def __repr__(self):
        return f"{self.id}"


#
# add_db_users = []
# for user in users:
#     add_db_users.append(User(
#         id=user['id'],
#         first_name=user['first_name'],
#         last_name=user['last_name'],
#         age=user['age'],
#         email=user['email'],
#         role=user['role'],
#         phone=user['phone']
#     ))
#
#
# add_db_offers = []
# for offer in offers:
#     add_db_offers.append(Offer(
#         id=offer["id"],
#         order_id=offer["order_id"],
#         executor_id=offer["executor_id"]
#     ))
#
#
# add_db_orders = []
# for order in orders:
#     add_db_orders.append(Order(
#         id=order["id"],
#         name=order["name"],
#         description=order["description"],
#         start_date=datetime.strptime(order["start_date"], "%m/%d/%Y"),
#         end_date=datetime.strptime(order["end_date"], "%m/%d/%Y"),
#         address=order["address"],
#         price=order["price"],
#         customer_id=order["customer_id"],
#         executor_id=order["executor_id"]
#     ))


@app.route('/users/', methods=["GET", "POST"])
def all_users():
    if request.method == "GET":
        all_users_json = []
        with app.app_context():
            query_all_users = db.session.query(User).all()
        for user in query_all_users:
            all_users_json.append({
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "age": user.age,
                "email": user.email,
                "role": user.role,
                "phone": user.phone
            })
        return jsonify(all_users_json)
    elif request.method == "POST":
        user = User(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            age=request.form['age'],
            email=request.form['email'],
            role=request.form['role'],
            phone=request.form['phone']
        )
        with app.app_context():
            db.session.add(user)
            db.session.commit()
        return "Пользователь успешно добавлен"


@app.route('/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
def one_user(user_id):
    if request.method == 'GET':
        with app.app_context():
            query_user = db.session.query(User).get(user_id)
        user = {
            "id": query_user.id,
            "first_name": query_user.first_name,
            "last_name": query_user.last_name,
            "age": query_user.age,
            "email": query_user.email,
            "role": query_user.role,
            "phone": query_user.phone
        }
        return user
    elif request.method == 'PUT':
        user_data_json = request.get_json()
        with app.app_context():
            user = db.session.query(User).get(user_id)
            user.first_name = user_data_json['first_name']
            user.last_name = user_data_json['last_name']
            user.age = user_data_json['age']
            user.email = user_data_json['email']
            user.role = user_data_json['role']
            user.phone = user_data_json['phone']
            db.session.add(user)
            db.session.commit()
        return "Пользователь успешно изменён"
    elif request.method == "DELETE":
        with app.app_context():
            user = db.session.query(User).get(user_id)
            db.session.delete(user)
            db.session.commit()
        return "Пользователь успешно удалён"


@app.route('/orders/', methods=["GET", "POST"])
def all_orders():
    if request.method == "GET":
        all_orders_json = []
        with app.app_context():
            query_all_orders = db.session.query(Order).all()
            for order in query_all_orders:

                if db.session.query(User).get(order.customer_id) is None:
                    query_customer_id = 'Данные отсутствуют'
                else:
                    query_customer_id = db.session.query(User).get(order.customer_id).first_name

                if db.session.query(User).get(order.executor_id) is None:
                    query_executor_id = 'Данные отсутствуют'
                else:
                    query_executor_id = db.session.query(User).get(order.executor_id).first_name

                all_orders_json.append({
                    "id": order.id,
                    "name": order.name,
                    "description": order.description,
                    "start_date": order.start_date,
                    "end_date": order.end_date,
                    "address": order.address,
                    "price": order.price,
                    "customer_name": query_customer_id,
                    "executor_name": query_executor_id
                })
        return jsonify(all_orders_json)
    elif request.method == "POST":
        order = Order(
            name=request.form["name"],
            description=request.form["description"],
            start_date=datetime.strptime(request.form["start_date"], "%m/%d/%Y"),
            end_date=datetime.strptime(request.form["end_date"], "%m/%d/%Y"),
            address=request.form["address"],
            price=request.form["price"],
            customer_id=request.form["customer_id"],
            executor_id=request.form["executor_id"]
        )
        with app.app_context():
            db.session.add(order)
            db.session.commit()
        return "Заказ успешно добавлен"


@app.route('/orders/<int:order_id>', methods=["GET", "PUT", "DELETE"])
def one_order(order_id):
    if request.method == "GET":
        with app.app_context():
            query_order = db.session.query(Order).get(order_id)
            if db.session.query(User).get(query_order.customer_id) is None:
                query_customer_id = 'Данные отсутствуют'
            else:
                query_customer_id = db.session.query(User).get(query_order.customer_id).first_name

            if db.session.query(User).get(query_order.executor_id) is None:
                query_executor_id = 'Данные отсутствуют'
            else:
                query_executor_id = db.session.query(User).get(query_order.executor_id).first_name

        order = {
            "id": query_order.id,
            "name": query_order.name,
            "description": query_order.description,
            "start_date": query_order.start_date,
            "end_date": query_order.end_date,
            "address": query_order.address,
            "price": query_order.price,
            "customer_name": query_customer_id,
            "executor_name": query_executor_id
        }
        return order
    elif request.method == 'PUT':
        order_data_json = request.get_json()
        with app.app_context():
            order = db.session.query(Order).get(order_id)
            order.name = order_data_json['name']
            order.description = order_data_json['description']
            order.start_date = datetime.strptime(order_data_json["start_date"], "%m/%d/%Y")
            order.end_date = datetime.strptime(order_data_json["end_date"], "%m/%d/%Y")
            order.address = order_data_json['address']
            order.price = order_data_json['price']
            order.customer_id = order_data_json['customer_id']
            order.executor_id = order_data_json['executor_id']
            db.session.add(order)
            db.session.commit()
        return "Заказ успешно изменён"
    elif request.method == "DELETE":
        with app.app_context():
            order = db.session.query(Order).get(order_id)
            db.session.delete(order)
            db.session.commit()
        return "Заказ успешно удалён"


@app.route('/offers/', methods=["GET", "POST"])
def all_offers():
    if request.method == "GET":
        all_offers_json = []
        with app.app_context():
            query_all_offers = db.session.query(Offer).all()
            for offer in query_all_offers:
                if db.session.query(Order).get(offer.order_id) is None:
                    query_order_name = 'Данные отсутствуют'
                else:
                    query_order_name = db.session.query(Order).get(offer.order_id).name

                if db.session.query(User).get(offer.executor_id) is None:
                    query_executor_name = 'Данные отсутствуют'
                else:
                    query_executor_name = db.session.query(User).get(offer.executor_id).first_name

                all_offers_json.append({
                    "id": offer.id,
                    "order_name": query_order_name,
                    "executor_name": query_executor_name
                })
        return jsonify(all_offers_json)
    elif request.method == "POST":
        offer = Offer(
            order_id=request.form["order_id"],
            executor_id=request.form["executor_id"]
        )
        with app.app_context():
            db.session.add(offer)
            db.session.commit()
        return "Предложение успешно добавлено"


@app.route('/offers/<int:offer_id>', methods=["GET", "PUT", "DELETE"])
def one_offer(offer_id):
    if request.method == "GET":
        with app.app_context():
            query_offer = db.session.query(Offer).get(offer_id)
            if db.session.query(Order).get(query_offer.order_id) is None:
                query_order_name = 'Данные отсутствуют'
            else:
                query_order_name = db.session.query(Order).get(query_offer.order_id).name

            if db.session.query(User).get(query_offer.executor_id) is None:
                query_executor_name = 'Данные отсутствуют'
            else:
                query_executor_name = db.session.query(User).get(query_offer.executor_id).first_name

        offer = {
            "id": query_offer.id,
            "order_name": query_order_name,
            "executor_name": query_executor_name
        }
        return offer
    elif request.method == 'PUT':
        offer_data_json = request.get_json()
        with app.app_context():
            offer = db.session.query(Offer).get(offer_id)
            offer.order_id = offer_data_json["order_id"]
            offer.executor_id = offer_data_json['executor_id']
            db.session.add(offer)
            db.session.commit()
        return "Предложение успешно изменено"
    elif request.method == "DELETE":
        with app.app_context():
            offer = db.session.query(Offer).get(offer_id)
            db.session.delete(offer)
            db.session.commit()
        return "Предложение успешно удалено"




app.run()
