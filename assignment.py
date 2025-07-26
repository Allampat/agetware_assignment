from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import math

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -------------------- Models --------------------

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    principal = db.Column(db.Float, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    period = db.Column(db.Float, nullable=False)  # in years
    interest = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    emi_amount = db.Column(db.Float, nullable=False)
    remaining_amount = db.Column(db.Float, nullable=False)
    remaining_emis = db.Column(db.Integer, nullable=False)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'), nullable=False)
    payment_type = db.Column(db.String(20), nullable=False)  # 'EMI' or 'LUMP_SUM'
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# -------------------- Routes --------------------

@app.route('/customer', methods=['POST'])
def create_customer():
    data = request.json
    customer = Customer(name=data['name'])
    db.session.add(customer)
    db.session.commit()
    return jsonify({"message": "Customer created", "customer_id": customer.id})

@app.route('/lend', methods=['POST'])
def lend():
    data = request.json
    P = data['principal']
    N = data['period']
    R = data['rate']
    I = (P * N * R) / 100
    A = P + I
    emi = round(A / (N * 12), 2)

    loan = Loan(
        customer_id=data['customer_id'],
        principal=P,
        rate=R,
        period=N,
        interest=I,
        total_amount=A,
        emi_amount=emi,
        remaining_amount=A,
        remaining_emis=int(N * 12)
    )
    db.session.add(loan)
    db.session.commit()

    # Initial transaction (Loan disbursal)
    db.session.add(Payment(
        loan_id=loan.id,
        payment_type='LEND',
        amount=A
    ))
    db.session.commit()

    return jsonify({
        "message": "Loan created successfully",
        "loan_id": loan.id,
        "total_amount": round(A, 2),
        "emi_amount": round(emi, 2)
    })

@app.route('/payment', methods=['POST'])
def payment():
    data = request.json
    loan = Loan.query.get(data['loan_id'])
    if not loan:
        return jsonify({"error": "Loan not found"}), 404

    amount = data['amount']
    payment_type = data['payment_type']

    # Update loan balance
    loan.remaining_amount = max(0, loan.remaining_amount - amount)
    loan.remaining_emis = math.ceil(loan.remaining_amount / loan.emi_amount)

    # Record transaction
    payment = Payment(
        loan_id=loan.id,
        payment_type=payment_type,
        amount=amount
    )
    db.session.add(payment)
    db.session.commit()

    return jsonify({
        "message": "Payment recorded successfully",
        "remaining_amount": round(loan.remaining_amount, 2),
        "remaining_emis": loan.remaining_emis
    })

@app.route('/ledger/<int:loan_id>', methods=['GET'])
def ledger(loan_id):
    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({"error": "Loan not found"}), 404

    payments = Payment.query.filter_by(loan_id=loan_id).order_by(Payment.timestamp).all()
    transactions = [{
        "type": p.payment_type,
        "amount": p.amount,
        "timestamp": p.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for p in payments]

    return jsonify({
        "loan_id": loan.id,
        "emi_amount": round(loan.emi_amount, 2),
        "remaining_amount": round(loan.remaining_amount, 2),
        "remaining_emis": loan.remaining_emis,
        "transactions": transactions
    })

@app.route('/overview/<int:customer_id>', methods=['GET'])
def overview(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    loans = Loan.query.filter_by(customer_id=customer_id).all()
    overview = []

    for loan in loans:
        paid = loan.total_amount - loan.remaining_amount
        overview.append({
            "loan_id": loan.id,
            "principal": round(loan.principal, 2),
            "interest": round(loan.interest, 2),
            "total_amount": round(loan.total_amount, 2),
            "emi_amount": round(loan.emi_amount, 2),
            "paid_amount": round(paid, 2),
            "remaining_amount": round(loan.remaining_amount, 2),
            "remaining_emis": loan.remaining_emis
        })

    return jsonify({
        "customer_id": customer_id,
        "customer_name": customer.name,
        "loans": overview
    })

# -------------------- Run the App --------------------

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
