"""
Author: Abhi
Date: 4th Feb, 2023
Purpose: Manages support functions, used multiple times
"""
def row2dict(row):
    data = {}
    for column in row.__table__.columns:
        data[column.name] = getattr(row, column.name)
    return data