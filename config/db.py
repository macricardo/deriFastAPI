from sqlalchemy import create_engine, MetaData

engine = create_engine("postgresql://deridb:Abcd1234%@localhost:5432/deridb")

meta = MetaData()

conn = engine.connect()
