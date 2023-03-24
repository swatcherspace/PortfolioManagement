
def row2dict(row):
    data = {}
    for column in row.__table__.columns:
        data[column.name] = getattr(row, column.name)
    return data