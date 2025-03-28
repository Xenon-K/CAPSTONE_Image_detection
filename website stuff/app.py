from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

app = Flask(__name__)
CORS(app)

# SQLAlchemy configuration
engine = create_engine('mysql+pymysql://root:5555@localhost/ai_leaderboard', echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Model(Base):
    __tablename__ = 'Models'
    model_id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(255), nullable=False)
    benchmarks = relationship("Benchmark", back_populates="model")
    website_url = Column(String(255))
    article_url = Column(String(255))


class Device(Base):
    __tablename__ = 'Devices'
    device_id = Column(Integer, primary_key=True, autoincrement=True)
    device_name = Column(String(255), nullable=False)
    chipset = Column(String(255), nullable=False)
    operating_system = Column(String(255), nullable=False)
    benchmarks = relationship("Benchmark", back_populates="device")


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
    memory_usage = Column(Float)
    compute_units = Column(Integer)
    model = relationship("Model", back_populates="benchmarks")
    device = relationship("Device", back_populates="benchmarks")



@app.route('/api/devices', methods=['GET'])
def get_devices():
    session = Session()
    devices = session.query(Device).all()
    device_list = [
        {
            "device_id": d.device_id,
            "device_name": d.device_name,
            "chipset": d.chipset,
            "operating_system": d.operating_system
        } for d in devices
    ]
    session.close()
    return jsonify(device_list)



@app.route('/api/modeldata', methods=['GET'])
def get_modeldata():
    device_id = request.args.get('device_id', type=int)
    session = Session()
    results = (
        session.query(Benchmark, Model)
        .join(Model, Benchmark.model_id == Model.model_id)
        .filter(Benchmark.device_id == device_id)
        .all()
    )
    model_data = {}
    for benchmark, model in results:
        model_data[model.model_name] = [
            benchmark.mAP,
            benchmark.inference_time,
            benchmark.memory_usage,
            benchmark.compute_units,
            model.website_url,
            model.article_url,
            benchmark.AP_small,
            benchmark.AP_medium,
            benchmark.AP_large,
        ]
    session.close()
    return jsonify({"data": model_data})



@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    device_id = request.args.get('device_id', type=int)
    metric = request.args.get('metric', type=str)
    sort_order = request.args.get('sort_order', default='default', type=str)

    allowed_metrics = ['inference_time', 'mAP', 'memory_usage', 'compute_units', 'AP_small', 'AP_medium', 'AP_large',
                       'AP_50', 'AP_75', 'AR', 'AR_50', 'AR_75', 'AR_small', 'AR_medium', 'AR_large']  # Add the new metrics
    if metric not in allowed_metrics:
        return jsonify({"error": "Invalid metric"}), 400

    session = Session()
    query = session.query(Benchmark, Model).join(Model, Benchmark.model_id == Model.model_id).filter(
        Benchmark.device_id == device_id)
    if sort_order == 'asc':
        query = query.order_by(getattr(Benchmark, metric).asc())
    elif sort_order == 'desc':
        query = query.order_by(getattr(Benchmark, metric).desc())

    results = query.all()
    labels = []
    values = []
    for benchmark, model in results:
        labels.append(model.model_name)
        values.append(getattr(benchmark, metric))
    session.close()

    return jsonify({"labels": labels, "values": values})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
