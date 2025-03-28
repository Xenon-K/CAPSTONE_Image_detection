from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
import pandas as pd

# Define the base for our models
Base = declarative_base()

# Define the Models table
class Model(Base):
    __tablename__ = 'Models'
    model_id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(255), nullable=False)
    benchmarks = relationship("Benchmark", back_populates="model")

# Define the Devices table
class Device(Base):
    __tablename__ = 'Devices'
    device_id = Column(Integer, primary_key=True, autoincrement=True)
    device_name = Column(String(255), nullable=False)
    chipset = Column(String(255), nullable=False)
    operating_system = Column(String(255), nullable=False)
    benchmarks = relationship("Benchmark", back_populates="device")

# Define the Benchmarks table
class Benchmark(Base):
    __tablename__ = 'Benchmarks'
    benchmark_id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(Integer, ForeignKey('Models.model_id'), nullable=False)
    device_id = Column(Integer, ForeignKey('Devices.device_id'), nullable=False)
    mAP = Column(Float, nullable=False)
    AP_50 = Column(Float)
    AP_75 = Column(Float)
    AP_small = Column(Float)
    AP_medium = Column(Float)
    AP_large = Column(Float)
    AR = Column(Float, nullable=False)
    AR_50 = Column(Float)
    AR_75 = Column(Float)
    AR_small = Column(Float)
    AR_medium = Column(Float)
    AR_large = Column(Float)
    inference_time = Column(Float, nullable=False)
    memory_usage = Column(Float, nullable=False)
    compute_units = Column(Integer)

    model = relationship("Model", back_populates="benchmarks")
    device = relationship("Device", back_populates="benchmarks")

# Connect to MySQL Database (Update credentials as needed)
engine = create_engine('mysql+pymysql://root:5555@localhost/ai_leaderboard')
Session = sessionmaker(bind=engine)
session = Session()

# Create tables
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
        session.commit()
    return device

# ========================
# Step 1: Drop Dummy Data
# ========================
session.query(Benchmark).delete()
session.query(Model).delete()
session.query(Device).delete()
session.commit()
print("Dummy data deleted successfully.")

# ========================
# Step 2: Read CSV and Insert Data
# ========================
csv_file_path = "allResults.csv"  # Update this path
df = pd.read_csv(csv_file_path)


# Transpose the dataframe so that each column corresponds to a model
df = df.set_index("Metric").transpose()

for _, row in df.iterrows():
    device_name = row["Device"]
    operating_system = row["OS"]
    model_name = row["Model"]
    inference_time = float(row["Inference Time"])
    peak_memory = float(row["Peak Memory"])
    compute_units = int(row["Compute Units"])

    mAP = float(row["AP"])
    AP_50 = float(row["AP@.5"])
    AP_75 = float(row["AP@.75"])
    AP_small = float(row["AP small"])
    AP_medium = float(row["AP medium"])
    AP_large = float(row["AP large"])

    AR = float(row["AR"])
    AR_50 = float(row["AR@.5"])
    AR_75 = float(row["AR@.75"])
    AR_small = float(row["AR small"])
    AR_medium = float(row["AR medium"])
    AR_large = float(row["AR large"])

    # Get or create device
    device = get_or_create_device(session, device_name, "Unknown", operating_system)

    # Get or create model
    model = session.query(Model).filter_by(model_name=model_name).first()
    if not model:
        model = Model(model_name=model_name)
        session.add(model)
        session.commit()

    # Insert new benchmark
    benchmark = Benchmark(
        model_id=model.model_id,
        device_id=device.device_id,
        mAP=mAP,
        AP_50=AP_50,
        AP_75=AP_75,
        AP_small=AP_small,
        AP_medium=AP_medium,
        AP_large=AP_large,
        AR=AR,
        AR_50=AR_50,
        AR_75=AR_75,
        AR_small=AR_small,
        AR_medium=AR_medium,
        AR_large=AR_large,
        inference_time=inference_time,
        memory_usage=peak_memory,
        compute_units=compute_units
    )
    session.add(benchmark)
    session.commit()

print("Actual data inserted successfully.")
