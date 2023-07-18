from datetime import date

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from src.models import Credit, Payment
from src.models import read_credits, write_credits

load_dotenv()
app = FastAPI()
credit_list = read_credits()


class InputStatement(BaseModel):
    month: int
    year: int
    closing_sate: date
    due_date: date
    required_min_payment1: int
    required_min_payment2: int
    required_full_payment: int


class InputPayment(BaseModel):
    payment_date: date
    amount: int
    proof_of_payment: str


@app.get("/hello")
def hello():
    return "OK"

@app.get("/")
def read_all():
    return credit_list


@app.get("/credit/{item_id}")
def credit_read(item_id: int):
    return credit_list[item_id]


@app.get("/statements/create/next")
def statements_create_next():
    for credit in credit_list:
        credit.create_empty_statement()
    write_credits(credit_list)


@app.get("/statement/{credit_id}/{statement_id}")
def statement_read(credit_id: int, statement_id: int):
    credit: Credit = credit_list[credit_id]
    statement = credit.statements[statement_id]
    return statement


@app.put("/statements/update/{credit_id}/{statement_id}")
def statement_update(credit_id: int, statement_id: int, obj: InputStatement):
    stm = credit_list[credit_id].statements[statement_id]
    stm.month = obj.month
    stm.year = obj.year
    stm.closing_date = obj.closing_sate
    stm.due_date = obj.due_date
    stm.required_min_payment1 = obj.required_min_payment1
    stm.required_min_payment2 = obj.required_min_payment2
    stm.required_full_payment = obj.required_full_payment

    write_credits(credit_list)


@app.put("/payment/update/{credit_id}/{statement_id}/{payment_id}")
def payment_update(credit_id: int, statement_id: int, payment_id: int, payment: InputPayment):
    pay = credit_list[credit_id].statements[statement_id].payments[payment_id]
    pay.payment_date = payment.payment_date
    pay.amount = payment.amount
    pay.proof_of_payment = payment.proof_of_payment

    write_credits(credit_list)


@app.post("/payment/new/{credit_id}/{statement_id}")
def payment_new(credit_id: int, statement_id: int):
    payment = Payment(payment_date=date.today(), amount=0, proof_of_payment="PATH")
    credit_list[credit_id].statements[statement_id].payments.append(payment)
