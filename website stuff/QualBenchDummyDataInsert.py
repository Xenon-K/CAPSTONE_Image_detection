from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, declarative_base, sessionmaker

# Define the base for our models
Base = declarative_base()

# Define the Models table as a Python class
class Model(Base):
    __tablename__ = 'Models'
    model_id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(255), nullable=False)
    benchmarks = relationship("Benchmark", back_populates="model")

# Define the Devices table as a Python class (with added chipset and operating_system)
class Device(Base):
    __tablename__ = 'Devices'
    device_id = Column(Integer, primary_key=True, autoincrement=True)
    device_name = Column(String(255), nullable=False)
    chipset = Column(String(255), nullable=False)
    operating_system = Column(String(255), nullable=False)
    benchmarks = relationship("Benchmark", back_populates="device")

# Define the Benchmarks table as a Python class
class Benchmark(Base):
    __tablename__ = 'Benchmarks'
    benchmark_id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(Integer, ForeignKey('Models.model_id'), nullable=False)
    device_id = Column(Integer, ForeignKey('Devices.device_id'), nullable=False)
    mAP = Column(Float, nullable=False)
    inference_time = Column(Float, nullable=False)
    compute_units = Column(Integer)
    memory_usage = Column(Float)

    model = relationship("Model", back_populates="benchmarks")
    device = relationship("Device", back_populates="benchmarks")

# Replace 'root', '5555', and 'ai_leaderboard' with your actual MySQL credentials and database name.
engine = create_engine('mysql+pymysql://root:5555@localhost/ai_leaderboard')
Session = sessionmaker(bind=engine)
session = Session()

# Create the tables in the database
Base.metadata.create_all(engine)

# Helper function to get or create a device
def get_or_create_device(session, device_name, chipset, operating_system):
    device = session.query(Device).filter_by(
        device_name=device_name,
        chipset=chipset,
        operating_system=operating_system
    ).first()
    if not device:
        device = Device(
            device_name=device_name,
            chipset=chipset,
            operating_system=operating_system
        )
        session.add(device)
        session.commit()  # Commit to get the device_id assigned
    return device

# ========================
# Insert Dummy Data Below
# ========================

# ----- AI Model One -----
model1 = Model(model_name="Test Model one(Testing Data)")
session.add(model1)
session.commit()  # Commit to assign model1.model_id

# Device 1 for Model One: SA7255P ADP
device1 = get_or_create_device(
    session,
    device_name="SA7255P ADP",
    chipset="Qualcomm® SA7255P",
    operating_system="Android 14"
)
benchmark1 = Benchmark(
    model_id=model1.model_id,
    device_id=device1.device_id,
    runtime=70.0,
    mAP=0.8,
    inference_time=15.0,
    memory_usage=80.0,
    compute_units=400
)
session.add(benchmark1)

# Device 2 for Model One: SA8255 (Proxy)
device2 = get_or_create_device(
    session,
    device_name="SA8255 (Proxy)",
    chipset="Qualcomm® SA8255P",
    operating_system="Android 13"
)
benchmark2 = Benchmark(
    model_id=model1.model_id,
    device_id=device2.device_id,
    runtime=70.0,
    mAP=0.8,
    inference_time=15.0,
    memory_usage=80.0,
    compute_units=400
)
session.add(benchmark2)
session.commit()

# ----- AI Model Two -----
model2 = Model(model_name="Test Model two(Testing Data)")
session.add(model2)
session.commit()

# For Model Two, reusing Device 1 (SA7255P ADP)
benchmark3 = Benchmark(
    model_id=model2.model_id,
    device_id=device1.device_id,
    runtime=60.0,
    mAP=0.6,
    inference_time=20.0,
    memory_usage=120.0,
    compute_units=600
)
session.add(benchmark3)

# For Model Two, reusing Device 2 (SA8255 (Proxy))
benchmark4 = Benchmark(
    model_id=model2.model_id,
    device_id=device2.device_id,
    runtime=60.0,
    mAP=0.6,
    inference_time=20.0,
    memory_usage=120.0,
    compute_units=600
)
session.add(benchmark4)
session.commit()

# ----- AI Model Three -----
model3 = Model(model_name="Test Model three(Testing Data)")
session.add(model3)
session.commit()

# For Model Three, reuse Device 2 (SA8255 (Proxy))
benchmark5 = Benchmark(
    model_id=model3.model_id,
    device_id=device2.device_id,
    runtime=50.0,
    mAP=0.9,
    inference_time=10.0,
    memory_usage=70.0,
    compute_units=350
)
session.add(benchmark5)

# Device 3 for Model Three: SA8295P ADP
device3 = get_or_create_device(
    session,
    device_name="SA8295P ADP",
    chipset="Qualcomm® SA8295P",
    operating_system="Android 14"
)
benchmark6 = Benchmark(
    model_id=model3.model_id,
    device_id=device3.device_id,
    runtime=55.0,
    mAP=0.95,
    inference_time=12.0,
    memory_usage=75.0,
    compute_units=450
)
session.add(benchmark6)
session.commit()

print("Database and tables created, and dummy data inserted successfully!")
