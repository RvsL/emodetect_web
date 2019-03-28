#!flask/bin/python
from flask import Response, render_template
from app.models import Stock
def generate_stock_table():
    yield render_template('stock_header.html')
    for stock in Stock.query.all():
        yield render_template('stock_row.html', stock=stock)
    yield render_template('stock_footer.html')
@app.route('/stock-table')
def stock_table():
    return Response(generate_stock_table())
