from datetime import datetime

from app import app, db
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, DateTime, Float
from sqlalchemy.orm import Relationship
from enum import Enum as CommonEnum
from flask_login import UserMixin
from flask import url_for


class UserRole(CommonEnum):
    ADMIN = 1
    RECEPTIONIST = 2
    CUSTOMER = 3


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)


class User(BaseModel, UserMixin):
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CUSTOMER)
    email = Column(String(50), unique=True, nullable=False)
    phone = Column(String(50), nullable=False, unique=True)
    avatar = Column(String(100), default='https://cdn.pixabay.com/photo/2020/07/14/13/07/icon-5404125_1280.png')
    gender = Column(Boolean, default=True)  # True = 1 is 'Man'


class Administrator(db.Model):
    id = Column(Integer, ForeignKey(User.id), nullable=False, primary_key=True)
    name = Column(String(50), nullable=False)


class Receptionist(db.Model):
    id = Column(Integer, ForeignKey(User.id), nullable=False, primary_key=True)
    name = Column(String(50), nullable=False)
    reservations = Relationship('Reservation', backref='receptionist', lazy=True)
    room_rentals = Relationship('RoomRental', backref='receptionist', lazy=True)


class CustomerType(BaseModel):
    type = Column(String(50), default='DOMESTIC')
    customers = Relationship('Customer', backref='customer_type', lazy=True)

    def __str__(self):
        return self.type


class Customer(db.Model):
    id = Column(Integer, ForeignKey(User.id), unique=True)  # khóa ngoại tham chiếu đến User
    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    identification = Column(String(15), unique=True)
    customer_type_id = Column(Integer, ForeignKey(CustomerType.id), nullable=False)
    reservations = Relationship('Reservation', backref='customer', lazy=True)
    comments = Relationship('Comment', backref='customer', lazy=True)
    reservation_details = Relationship('ReservationDetail', backref='customer', lazy=True)

    def __str__(self):
        return self.name


class RoomType(BaseModel):
    name = Column(String(50), nullable=False, unique=True)
    rooms = Relationship('Room', backref='room_type', lazy=True)

    def __str__(self):
        return self.name


class Room(BaseModel):
    name = Column(String(50), nullable=False, unique=True)
    image = Column(String(500), nullable=False)
    room_type_id = Column(Integer, ForeignKey(RoomType.id), nullable=False)
    reservations = Relationship('Reservation', backref='room', lazy=True)
    room_rentals = Relationship('RoomRental', backref='room', lazy=True)
    comments = Relationship('Comment', backref='room', lazy=True)

    def __str__(self):
        return self.name


class Reservation(BaseModel):
    customer_id = Column(Integer, ForeignKey(Customer.customer_id))
    receptionist_id = Column(Integer, ForeignKey(Receptionist.id))
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False)
    checkin_date = Column(DateTime, nullable=False)
    checkout_date = Column(DateTime, nullable=False)
    is_checkin = Column(Boolean, default=False)
    deposit = Column(Float, nullable=False)
    reservation_details = Relationship('ReservationDetail', backref='reservation', lazy=True)


class ReservationDetail(BaseModel):
    customer_id = Column(Integer, ForeignKey(Customer.customer_id), primary_key=True)
    reservation_id = Column(Integer, ForeignKey(Reservation.id), primary_key=True)


class RoomRental(BaseModel):
    # customer_id = Column(Integer, ForeignKey(Customer.customer_id))
    receptionist_id = Column(Integer, ForeignKey(Receptionist.id), nullable=False)
    room_id = Column(Integer, ForeignKey(Room.id))  # null if is_received_room == True
    reservation_id = Column(Integer, ForeignKey(Reservation.id))  # null if is_received_room == False
    checkin_date = Column(DateTime, default=datetime.now())
    checkout_date = Column(DateTime)
    deposit = Column(Float)
    is_paid = Column(Boolean, default=False)
    room_rental_details = Relationship('RoomRentalDetail', backref='room_rental', lazy=True)

    receipt = Relationship('Receipt', uselist=False, back_populates='room_rental')


class RoomRentalDetail(BaseModel):
    customer_id = Column(Integer, ForeignKey(Customer.customer_id), primary_key=True)
    room_rental_id = Column(Integer, ForeignKey(RoomRental.id), primary_key=True)


class Receipt(BaseModel):
    receptionist_id = Column(Integer, ForeignKey(Receptionist.id), nullable=False)
    rental_room_id = Column(Integer, ForeignKey(RoomRental.id), nullable=False)
    room_rental = Relationship('RoomRental', back_populates='receipt')
    total_price = Column(Float, nullable=False)
    created_date = Column(DateTime, nullable=False, default=datetime.now())


class Comment(BaseModel):
    customer_id = Column(Integer, ForeignKey(Customer.id), nullable=False)
    content = Column(String(1000), nullable=False)
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False, primary_key=True)
    created_date = Column(DateTime, default=datetime.now())


class RoomRegulation(BaseModel):
    room_type_id = Column(Integer, ForeignKey(RoomType.id), nullable=False, primary_key=True)
    admin_id = Column(Integer, ForeignKey(Administrator.id), nullable=False)
    room_quantity = Column(Integer, default=10)
    capacity = Column(Integer, default=2)
    price = Column(Float, default=100000)
    surcharge = Column(Float, default=0.25)
    deposit_rate = Column(Float, default=0.3)
    distance = Column(Integer, nullable=False, default=28)


class CustomerTypeRegulation(BaseModel):
    rate = Column(Float, default=1.0, nullable=False)
    admin_id = Column(Integer, ForeignKey(Administrator.id), nullable=False)
    customer_type_id = Column(Integer, ForeignKey(CustomerType.id), nullable=False, primary_key=True)


if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()

        rt1 = RoomType(name='SINGLE BEDROOM')
        rt2 = RoomType(name='TWIN BEDROOM')
        rt3 = RoomType(name='DOUBLE BEDROOM')
        db.session.add_all([rt1, rt2, rt3])
        db.session.commit()

        r1 = Room(name='A01', room_type_id=2, image='images/p1.png')
        r2 = Room(name='A02', room_type_id=3, image='images/p2.png')
        r3 = Room(name='A03', room_type_id=2, image='images/p3.png')
        r4 = Room(name='A04', room_type_id=1, image='images/p4.png')
        r5 = Room(name='A05', room_type_id=3, image='images/p5.png')
        db.session.add_all([r1, r2, r3, r4, r5])
        db.session.commit()

        ######################################################

        import hashlib

        user1 = User(
            role=UserRole.ADMIN,
            username='locla123',
            password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()),
            avatar='https://cdn.pixabay.com/photo/2020/07/14/13/07/icon-5404125_1280.png',
            email='loc@gmail.com',
            phone='0334454203')
        user2 = User(
            role=UserRole.CUSTOMER,
            username='kiet',
            password=str(hashlib.md5('kiet'.encode('utf-8')).hexdigest()),
            avatar='https://cdn.pixabay.com/photo/2020/07/14/13/07/icon-5404125_1280.png',
            email='2151050219kiet@ou.edu.vn',
            phone='0869311727')
        user3 = User(
            role=UserRole.CUSTOMER,
            username='duy',
            password=str(hashlib.md5('duy'.encode('utf-8')).hexdigest()),
            avatar='https://cdn.pixabay.com/photo/2020/07/14/13/07/icon-5404125_1280.png',
            email='2151050055@ou.edu.vn',
            phone='0123456789')
        user4 = User(
            role=UserRole.CUSTOMER,
            username='lan',
            password=str(hashlib.md5('lan'.encode('utf-8')).hexdigest()),
            avatar='https://cdn.pixabay.com/photo/2020/07/14/13/07/icon-5404125_1280.png',
            email='lan@gmail.com',
            phone='0642138713')
        user5 = User(
            role=UserRole.CUSTOMER,
            username='tuan',
            password=str(hashlib.md5('tuan'.encode('utf-8')).hexdigest()),
            avatar='https://cdn.pixabay.com/photo/2020/07/14/13/07/icon-5404125_1280.png',
            email='tuan@gmail.com',
            phone='0287112946')
        user6 = User(
            role=UserRole.CUSTOMER,
            username='lau',
            password=str(hashlib.md5('lau'.encode('utf-8')).hexdigest()),
            avatar='https://cdn.pixabay.com/photo/2020/07/14/13/07/icon-5404125_1280.png',
            email='lau@gmail.com',
            phone='0198247172')
        user7 = User(username='NhungTran', password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()),
                     role=UserRole.RECEPTIONIST, email='nhung@gmail.com', phone='035588475', gender=False)
        db.session.commit()
        db.session.add_all([user1, user2, user3, user4, user5, user6, user7])
        db.session.commit()

        admin1 = Administrator(id=1, name='La Hồng Lộc')
        db.session.add(admin1)
        db.session.commit()

        r1 = Receptionist(name='Tran Thi Nhung', id=7)
        db.session.add(r1)
        db.session.commit()

        ct1 = CustomerType()
        ct2 = CustomerType(type='FOREIGN')
        db.session.add_all([ct1, ct2])
        db.session.commit()

        cus1 = Customer(id=2, name='Trần Tuấn Kiệt', identification='0194612374612', customer_type_id=1)
        cus2 = Customer(id=3, name='Hoàng Nguyễn Quốc Duy', identification='0123491958123', customer_type_id=1)
        cus3 = Customer(id=4, name='Trần Lê Lân', identification='01235012357', customer_type_id=2)
        cus4 = Customer(id=5, name='Văn Công Tuấn', identification='09832478143', customer_type_id=2)
        cus5 = Customer(id=6, name='Ngô Văn Lâu', identification='01283597235', customer_type_id=1)
        db.session.add_all([cus1, cus2, cus3, cus4, cus5])
        db.session.commit()

        ##################

        ctr1 = CustomerTypeRegulation(admin_id=1, customer_type_id=1)
        ctr2 = CustomerTypeRegulation(admin_id=1, customer_type_id=2, rate=1.5)
        db.session.add_all([ctr1, ctr2])
        db.session.commit()

        rr1 = RoomRegulation(room_type_id=1, admin_id=1, room_quantity=10, capacity=3, price=3000000)
        rr2 = RoomRegulation(room_type_id=2, admin_id=1, room_quantity=15, capacity=3, price=4000000)
        rr3 = RoomRegulation(room_type_id=3, admin_id=1, room_quantity=17, capacity=3, price=5000000)
        db.session.add_all([rr1, rr2, rr3])
        db.session.commit()

        cm1 = Comment(customer_id=2, content='Phòng này quá ok <3', room_id=1, created_date=datetime(2024, 1, 9, 17, 1))
        cm2 = Comment(customer_id=3, content='Cũng tàm tạm, cần nâng cấp dịch vụ phòng!',
                      created_date=datetime(2024, 1, 9, 17, 1), room_id=1)
        cm3 = Comment(customer_id=4, content='Sẽ ghé thăm vào lần sau nếu có dịp',
                      created_date=datetime(2024, 1, 9, 17, 1), room_id=2)
        cm4 = Comment(customer_id=5, content='Một căn phòng đáng trải nghiệm nhất tại khách sạn, 5 sau nhé',
                      created_date=datetime(2024, 1, 9, 17, 1), room_id=2)
        cm5 = Comment(customer_id=6,
                      content='Mình có một người bạn nước ngoài ở chung, sẽ nhân hệ số 1.5 nhưng đây là quy định chung của khách sạn rùi nên cũng không sao, miễn là dịch vụ OK và phòng thì miễn chê',
                      created_date=datetime(2024, 1, 9, 17, 1),
                      room_id=2)
        cm6 = Comment(customer_id=2,
                      content='Có dịp ghé qua đây, đang loay hoay tìm phòng thì có dịch vụ đặt phòng trước, đến nơi chỉ cần đưa thông tin phiếu cho nhân viên lễ tân là nhận phòng ở luôn, 10 điểm',
                      created_date=datetime(2024, 1, 9, 17, 1),
                      room_id=3)
        cm7 = Comment(customer_id=3, content='Phòng này 0 điểm ... không có điểm nào để chê ạ =)))',
                      created_date=datetime(2024, 1, 9, 17, 1), room_id=3)
        cm8 = Comment(customer_id=4, content='Thật là một nơi đáng để tra nghiệm',
                      created_date=datetime(2024, 1, 9, 17, 1), room_id=3)
        cm9 = Comment(customer_id=5, content='Xứng đáng với số tiền bỏ ra', created_date=datetime(2024, 1, 9, 17, 1),
                      room_id=3)
        cm10 = Comment(customer_id=6,
                       content='Mình không biết những nơi khác thế nào, nhưng đối với mình noi đây rất tiện nghi từ dịch vụ cho đến giải quyết sự cố cho khách hàng',
                       created_date=datetime(2024, 1, 9, 17, 1),
                       room_id=3)
        cm11 = Comment(customer_id=2,
                       content='Mình lỡ làm bể kính phòng tắm nên phải bồi thường, nhưng vẫn hài lòng với những gì khách sạn mang đến',
                       created_date=datetime(2024, 1, 9, 17, 1),
                       room_id=4)
        cm12 = Comment(customer_id=3, content='Cần điều chỉnh số lượng người ở trong phòng nhiều hơn',
                       created_date=datetime(2024, 1, 9, 17, 1), room_id=4)
        cm13 = Comment(customer_id=4, content='Nơi này rất thoải mái và tiện nghi, có view đỉnh lắm ạ!',
                       created_date=datetime(2024, 1, 9, 17, 1), room_id=4)
        cm14 = Comment(customer_id=5, content='Những gì khách sạn mang đến rất tốt cho trải nghiệm của tôi',
                       created_date=datetime(2024, 1, 9, 17, 1), room_id=4)
        cm15 = Comment(customer_id=6, content='Nhân viên dễ thương lắm, tư vấn phòng này và trải nghiệm rất tốt',
                       created_date=datetime(2024, 1, 9, 17, 1), room_id=4)
        cm16 = Comment(customer_id=2,
                       content='Quá tuyt vời mặc dù mình ở 3 người nên có thêm phụ phí 25% nha mng ơi, quy định chung của khách sạn rùi',
                       created_date=datetime(2024, 1, 9, 17, 1),
                       room_id=5)
        cm17 = Comment(customer_id=3,
                       content='Cần điều chỉnh hệ số lúc thanh toán thì quá oke vì mình là khách nước ngoài',
                       created_date=datetime(2024, 1, 9, 17, 1),
                       room_id=5)
        cm18 = Comment(customer_id=4,
                       content='9.5 điểm, vì 0.5 điểm còn lại là do mình đi 3 người nên thu 25% và có nhân hệ số 1.5 lúc thanh toán huhuhuhhhhuhu :(',
                       created_date=datetime(2024, 1, 9, 17, 1),
                       room_id=5)
        db.session.add_all([cm1, cm2,
                            cm3, cm4, cm5, cm6,
                            cm7, cm8, cm9,
                            cm10, cm11, cm12, cm13, cm14, cm15,
                            cm16, cm17, cm18])
        db.session.commit()

        reservation_data = [
            {'customer_id': 2, 'receptionist_id': 7, 'room_id': 4, 'checkin_date': datetime(2024, 1, 9, 17, 1),
             'checkout_date': datetime(2024, 1, 19, 17, 1), 'deposit': 900000},
            {'customer_id': 1, 'receptionist_id': 7, 'room_id': 2, 'checkin_date': datetime(2024, 3, 25, 17, 11),
             'checkout_date': datetime(2024, 3, 29, 17, 11), 'deposit': 1500000},
            {'customer_id': 2, 'receptionist_id': 7, 'room_id': 2, 'checkin_date': datetime(2023, 12, 11, 17, 12),
             'checkout_date': datetime(2023, 12, 21, 17, 12), 'deposit': 1500000},
            {'customer_id': 1, 'receptionist_id': 7, 'room_id': 1, 'checkin_date': datetime(2024, 1, 9, 17, 1),
             'checkout_date': datetime(2024, 2, 9, 17, 1), 'deposit': 1200000},
            {'customer_id': 4, 'receptionist_id': 7, 'room_id': 1, 'checkin_date': datetime(2024, 1, 9, 17, 1),
             'checkout_date': datetime(2024, 1, 29, 17, 1), 'deposit': 1200000},
            {'customer_id': 5, 'receptionist_id': 7, 'room_id': 2, 'checkin_date': datetime(2023, 12, 11, 17, 12),
             'checkout_date': datetime(2023, 12, 19, 17, 12), 'deposit': 1500000},
            {'customer_id': 2, 'receptionist_id': 7, 'room_id': 1, 'checkin_date': datetime(2023, 12, 11, 17, 12),
             'checkout_date': datetime(2023, 12, 17, 17, 12), 'deposit': 1200000},
        ]

        for data in reservation_data:
            reservation = Reservation(**data)
            db.session.add(reservation)
        db.session.commit()

        # Tạo đối tượng RoomRental và thêm dữ liệu chi tiết
        room_rental1 = RoomRental(
            receptionist_id=7,
            room_id=4,
            reservation_id=1,
            checkin_date=datetime(2024, 1, 17, 20, 55, 32),
            checkout_date=datetime(2024, 1, 29, 20, 55, 32),
            deposit=None,
            is_paid=True
        )

        room_rental2 = RoomRental(
            receptionist_id=7,
            room_id=2,
            reservation_id=2,
            checkin_date=datetime(2024, 2, 1, 20, 55, 32),
            checkout_date=datetime(2024, 2, 18, 20, 55, 32),
            deposit=None,
            is_paid=True
        )

        room_rental3 = RoomRental(
            receptionist_id=7,
            room_id=3,
            checkin_date=datetime(2024, 2, 3, 20, 55, 32),
            checkout_date=datetime(2024, 2, 26, 20, 55, 32),
            deposit=1500000,
            is_paid=True
        )

        room_rental4 = RoomRental(
            receptionist_id=7,
            room_id=2,
            reservation_id=3,
            checkin_date=datetime(2024, 2, 27, 20, 55, 32),
            checkout_date=datetime(2024, 3, 5, 20, 55, 32),
            deposit=None,
            is_paid=True
        )

        room_rental5 = RoomRental(
            receptionist_id=7,
            room_id=1,
            reservation_id=4,
            checkin_date=datetime(2023, 8, 3, 20, 55, 32),
            checkout_date=datetime(2024, 8, 24, 20, 55, 32),
            deposit=None,
            is_paid=True
        )

        room_rental6 = RoomRental(
            receptionist_id=7,
            room_id=1,
            reservation_id=5,
            checkin_date=datetime(2024, 1, 20, 20, 55, 32),
            checkout_date=datetime(2024, 1, 27, 20, 55, 32),
            deposit=None,
            is_paid=True
        )

        room_rental7 = RoomRental(
            receptionist_id=7,
            room_id=3,
            checkin_date=datetime(2023, 4, 12, 20, 55, 32),
            checkout_date=datetime(2024, 4, 26, 20, 55, 32),
            deposit=1500000,
            is_paid=True
        )

        room_rental8 = RoomRental(
            receptionist_id=7,
            room_id=2,
            reservation_id=6,
            checkin_date=datetime(2024, 6, 18, 20, 55, 32),
            checkout_date=datetime(2024, 7, 2, 20, 55, 32),
            deposit=None,
            is_paid=True
        )

        room_rental9 = RoomRental(
            receptionist_id=7,
            room_id=1,
            reservation_id=7,
            checkin_date=datetime(2024, 3, 3, 20, 55, 32),
            checkout_date=datetime(2024, 4, 5, 20, 55, 32),
            deposit=None,
            is_paid=True
        )

        # Thêm các đối tượng vào cơ sở dữ liệu
        with db.session.begin():
            db.session.add_all(
                [room_rental1, room_rental2, room_rental3, room_rental4, room_rental5, room_rental6, room_rental7,
                 room_rental8, room_rental9])

        # Lưu thay đổi vào cơ sở dữ liệu
        db.session.commit()

        receipt_data = [
            {'receptionist_id': 7, 'rental_room_id': 1, 'total_price': 3000000, 'created_date': datetime(2023, 1, 19, 17, 1)},
            {'receptionist_id': 7, 'rental_room_id': 2, 'total_price': 5000000, 'created_date': datetime(2023, 1, 29, 17, 11)},
            {'receptionist_id': 7, 'rental_room_id': 3, 'total_price': 5000000, 'created_date': datetime(2023, 2, 19, 17, 11)},
            {'receptionist_id': 7, 'rental_room_id': 4, 'total_price': 5000000, 'created_date': datetime(2023, 4, 29, 17, 11)},
            {'receptionist_id': 7, 'rental_room_id': 5, 'total_price': 4000000, 'created_date': datetime(2024, 1, 29, 17, 11)},
            {'receptionist_id': 7, 'rental_room_id': 6, 'total_price': 4000000, 'created_date': datetime(2024, 2, 29, 17, 11)},
            {'receptionist_id': 7, 'rental_room_id': 7, 'total_price': 5000000, 'created_date': datetime(2024, 2, 29, 17, 11)},
            {'receptionist_id': 7, 'rental_room_id': 8, 'total_price': 5000000, 'created_date': datetime(2024, 2, 29, 17, 11)},
            {'receptionist_id': 7, 'rental_room_id': 9, 'total_price': 4000000, 'created_date': datetime(2024, 4, 29, 17, 11)},
        ]

        for data in receipt_data:
            receipt = Receipt(**data)
            db.session.add(receipt)

        db.session.commit()
