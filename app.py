from flask import Flask, request, render_template, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import math
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# ================== CONFIG ==================
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///' + os.path.join(basedir , 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.secret_key = os.environ.get("SECRET_KEY", "fallback_key")

db = SQLAlchemy(app)




# ================== ROUTES ==================

@app.route('/')
def home():
    return render_template('home.html')






# ======================= TAX CALCULATOR ==========================
@app.route("/tax_calculator", methods=["GET", "POST"])
def tax_calculator():
    

    tax_amount = None
    taxable_income = None
    regime_selected = None
    other_ded = 0

    if request.method == "POST":
        income = float(request.form.get("income"))
        regime_selected = request.form.get("regime")

        if regime_selected == "old":
            other_ded = float(request.form.get("other_ded") or 0)

        age = "Below 60"

        # New Regime
        if regime_selected == "new":
            std_deduction = 75000
            taxable_income = max(0, income - std_deduction)

            if taxable_income <= 1200000:
                tax_amount = 0
            else:
                if taxable_income <= 400000:
                    tax_amount = 0
                elif taxable_income <= 800000:
                    tax_amount = (taxable_income - 400000) * 0.05
                elif taxable_income <= 1200000:
                    tax_amount = 20000 + (taxable_income - 800000) * 0.10
                elif taxable_income <= 1600000:
                    tax_amount = 60000 + (taxable_income - 1200000) * 0.15
                elif taxable_income <= 2000000:
                    tax_amount = 120000 + (taxable_income - 1600000) * 0.20
                elif taxable_income <= 2400000:
                    tax_amount = 200000 + (taxable_income - 2000000) * 0.25
                else:
                    tax_amount = 300000 + (taxable_income - 2400000) * 0.30

            tax_amount *= 1.04  # CESS

        # Old Regime
        elif regime_selected == "old":
            taxable_income = max(0, income - other_ded)

            if taxable_income <= 250000:
                tax_amount = 0
            elif taxable_income <= 500000:
                tax_amount = (taxable_income - 250000) * 0.05
            elif taxable_income <= 1000000:
                tax_amount = 12500 + (taxable_income - 500000) * 0.20
            else:
                tax_amount = 112500 + (taxable_income - 1000000) * 0.30

            if taxable_income <= 500000:
                tax_amount = 0

            tax_amount *= 1.04

    return render_template(
    "tax_calculator.html",
    tax=round(tax_amount, 2) if tax_amount is not None else None,
    taxable_income=round(taxable_income, 2) if taxable_income is not None else None,
    regime=regime_selected
)
 


# ======================= EMI CALCULATOR ==========================
@app.route("/EMI", methods=["GET", "POST"])
def emi_calculator_new():

    emi = None
    total_payment = None
    total_interest = None
    principal = None

    if request.method == "POST":
        principal = float(request.form.get("principal"))
        rate = float(request.form.get("rate"))
        years = float(request.form.get("years"))

        monthly_rate = rate / (12 * 100)
        months = years * 12

        emi = (principal * monthly_rate * (math.pow(1 + monthly_rate, months))) / \
              (math.pow(1 + monthly_rate, months) - 1)

        total_payment = emi * months
        total_interest = total_payment - principal

    return render_template("EMI.html",
                           emi=emi,
                           total_payment=total_payment,
                           total_interest=total_interest,
                           principal=principal)


# ================== 404 PAGE ==================
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


# ================== RUN APP ==================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
