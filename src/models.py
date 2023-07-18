import json
import os
from dataclasses import dataclass, field, asdict
from datetime import date, timedelta
from enum import Enum
from typing import Optional

import jsons
import smart_open


class Currency(Enum):
    MXN = "MXN"
    USD = "USD"


class Bank(Enum):
    BBVA = "BBVA"
    BANAMEX = "Banamex"
    HSBC = "HSBC"
    LIVERPOOL = "Liverpool"
    VW_LEASING = "VW Leasing"


@dataclass
class Payment:
    payment_date: date
    amount: int
    proof_of_payment: str

    def asdict(self):
        return asdict(self)


@dataclass
class Statement:
    month: int
    year: int
    closing_date: date
    due_date: date
    required_min_payment1: int
    required_min_payment2: int
    required_full_payment: int
    payed: Optional[int] = None
    pending_for_min_payment1: Optional[int] = None
    pending_for_min_payment2: Optional[int] = None
    pending_for_full_payment: Optional[int] = None
    last_date_payed: Optional[date] = None
    number_of_payments: Optional[int] = None
    payments: list[Payment] = field(default_factory=list)

    def asdict(self):
        return asdict(self)

    def __str__(self):
        data_str = jsons.dumps(self)
        data = json.loads(data_str)
        data_str2 = json.dumps(data, indent=3)
        return data_str2

    @classmethod
    def pending(cls, a: int, x: int) -> int:
        d = a - x
        d = max(0, d)
        return d

    def update(self):
        payed = sum([p.amount for p in self.payments])
        pending_for_min_payment1 = self.pending(self.required_min_payment1, payed)
        pending_for_min_payment2 = self.pending(self.required_min_payment2, payed)
        pending_for_full_payment = self.pending(self.required_full_payment, payed)
        number_of_payments = len(self.payments)
        last_date_payed = None if number_of_payments == 0 else self.payments[-1].payment_date

        self.payed = payed
        self.pending_for_min_payment1 = pending_for_min_payment1
        self.pending_for_min_payment2 = pending_for_min_payment2
        self.pending_for_full_payment = pending_for_full_payment
        self.last_date_payed = last_date_payed
        self.number_of_payments = number_of_payments
        return self


@dataclass
class Credit:
    name: str
    bank: Bank
    closing_day: int
    due_days: int
    currency: Currency
    statements: list[Statement]

    def asdict(self):
        return asdict(self)

    @classmethod
    def ensure_weekday(cls, d: date):
        if d.weekday() == 5:
            d = d + timedelta(days=2)
        elif d.weekday() == 6:
            d = d + timedelta(days=1)
        return d

    def next_closing_and_due_date(self):
        today = date.today()
        year = today.year if not self.statements else self.statements[-1].closing_date.year
        month = today.month if not self.statements else self.statements[-1].closing_date.month + 1

        if month > 12:
            year += month // 12
            month = month % 12

        closing_date = date(year, month, self.closing_day)
        due_date = closing_date + timedelta(days=self.due_days)
        due_date_ok = self.ensure_weekday(due_date)
        return closing_date, due_date_ok

    def create_empty_statement(self):
        closing_date, due_date = self.next_closing_and_due_date()
        month = closing_date.month
        year = closing_date.year
        stm = Statement(
            month=month,
            year=year,
            closing_date=closing_date,
            due_date=due_date,
            required_min_payment1=0,
            required_min_payment2=0,
            required_full_payment=0
        )
        stm.update()
        self.statements.append(stm)

    @classmethod
    def load_credit_file(cls, path: str) -> list['Credit'] or list:
        with smart_open.open(path) as fp:
            credit_list = []
            for line in fp:
                credit = jsons.loads(line, cls=Credit)
                credit_list.append(credit)
        return credit_list

    @classmethod
    def dumps_credit_file(cls, path: str, data: list['Credit']):
        with smart_open.open(path, "w") as fp:
            nl = ""
            for el in data:
                content = jsons.dumps(el)
                fp.write(nl + content)
                nl = "\n"


def read_credits() -> list[Credit]:
    x = Credit.load_credit_file(os.getenv("CREDIT_JSON_PATH"))
    return x


def write_credits(credit_list: list[Credit]):
    Credit.dumps_credit_file(os.getenv("CREDIT_JSON_PATH"), credit_list)


def example_write():
    CREDIT_JSON_PATH = os.getenv("CREDIT_JSON_PATH")

    mxn = Currency.MXN
    credits = [
        Credit(name="BBVA Azul",
               bank=Bank.BBVA,
               closing_day=23,
               due_days=20,
               currency=Currency.MXN,
               statements=[
                   Statement(month=5,
                             year=2023,
                             closing_date=date(2023, 5, 22),
                             due_date=date(2023, 6, 12),
                             required_min_payment1=719251,
                             required_min_payment2=2571942,
                             required_full_payment=11065415,
                             payments=[
                                 Payment(payment_date=date(2023, 5, 31),
                                         amount=2571942,
                                         proof_of_payment="BBVA m05 PP 1 de 2 2023-05-31.jpg"),
                                 Payment(payment_date=date(2023, 6, 10),
                                         amount=8493473,
                                         proof_of_payment="BBVA m05 PP 2 de 2 2023-06-10.pdf"),
                             ]).update(),
                   Statement(month=6,
                             year=2023,
                             closing_date=date(2023, 6, 22),
                             due_date=date(2023, 7, 12),
                             required_min_payment1=528000,
                             required_min_payment2=697800,
                             required_full_payment=1742565,
                             payments=[
                                 Payment(payment_date=date(2023, 6, 27),
                                         amount=1742565,
                                         proof_of_payment="BBVA m06 PPNGI 2023-06-27.pdf"),
                             ]).update(),
               ]),
        Credit(name="Banamex Costco",
               bank=Bank.BANAMEX,
               closing_day=13,
               due_days=20,
               currency=Currency.MXN,
               statements=[
                   Statement(month=5,
                             year=2023,
                             closing_date=date(2023, 5, 13),
                             due_date=date(2023, 6, 2),
                             required_min_payment1=250000,
                             required_min_payment2=1968855,
                             required_full_payment=11167676,
                             payments=[
                                 Payment(payment_date=date(2023, 5, 31),
                                         amount=1968855,
                                         proof_of_payment="Banamex m05 PP 1 de 3 2023-05-31.pdf"),
                                 Payment(payment_date=date(2023, 6, 10),
                                         amount=3500000,
                                         proof_of_payment="Banamex m05 PP 2 de 3 2023-06-10.pdf"),
                             ]).update(),
                   Statement(month=6,
                             year=2023,
                             closing_date=date(2023, 6, 13),
                             due_date=date(2023, 7, 3),
                             required_min_payment1=789000,
                             required_min_payment2=1622009,
                             required_full_payment=7315362,
                             payments=[
                                 Payment(payment_date=date(2023, 7, 3),
                                         amount=5800000,
                                         proof_of_payment="Banamex m06 PP 1 de 2 2023-07-03.pdf"),
                                 Payment(payment_date=date(2023, 7, 6),
                                         amount=1515362,
                                         proof_of_payment="Banamex m06 PP 2 de 2 2023-07-06.pdf"),
                             ]).update()

               ]),
        Credit(name="HSBC Viva",
               bank=Bank.HSBC,
               closing_day=19,
               due_days=20,
               currency=Currency.MXN,
               statements=[
                   Statement(month=5,
                             year=2023,
                             closing_date=date(2023, 5, 19),
                             due_date=date(2023, 6, 10),
                             required_min_payment1=93750,
                             required_min_payment2=492690,
                             required_full_payment=2546076,
                             payments=[
                                 Payment(payment_date=date(2023, 6, 1),
                                         amount=2546076,
                                         proof_of_payment="HSBC m05 PPNGI 2023-06-01.jpeg"),
                             ]).update(),
                   Statement(month=6,
                             year=2023,
                             closing_date=date(2023, 6, 19),
                             due_date=date(2023, 7, 9),
                             required_min_payment1=93750,
                             required_min_payment2=537033,
                             required_full_payment=2176203,
                             payments=[
                                 Payment(payment_date=date(2023, 6, 27),
                                         amount=2176203,
                                         proof_of_payment="HSBC m06 PPNGI 2023-06-27.pdf"),
                             ]).update(),
               ]),
        Credit(name="Liverpool PP",
               bank=Bank.LIVERPOOL,
               closing_day=20,
               due_days=30,
               currency=Currency.MXN,
               statements=[
                   Statement(month=5,
                             year=2023,
                             closing_date=date(2023, 5, 11),
                             due_date=date(2023, 6, 11),
                             required_min_payment1=2,
                             required_min_payment2=2,
                             required_full_payment=2,
                             payments=[
                                 Payment(payment_date=date(2023, 5, 31),
                                         amount=2,
                                         proof_of_payment="Liverpool m05 PPNGI 2023-05-31.pdf"),
                             ]).update(),
                   Statement(month=6,
                             year=2023,
                             closing_date=date(2023, 6, 11),
                             due_date=date(2023, 7, 11),
                             required_min_payment1=0,
                             required_min_payment2=0,
                             required_full_payment=0,
                             payments=[]).update(),
               ]),
        Credit(name="VW Tiguan 2023",
               bank=Bank.VW_LEASING,
               closing_day=1,
               due_days=15,
               currency=Currency.MXN,
               statements=[
                   Statement(month=6,
                             year=2023,
                             closing_date=date(2023, 6, 1),
                             due_date=date(2023, 6, 16),
                             required_min_payment1=1154846,
                             required_min_payment2=1154846,
                             required_full_payment=1154846,
                             payments=[
                                 Payment(payment_date=date(2023, 6, 16),
                                         amount=1154846,
                                         proof_of_payment="JESSICA Statement"),
                             ]).update(),
               ]),
    ]
    Credit.dumps_credit_file(CREDIT_JSON_PATH, credits)


def example_read():
    path = os.getenv("CREDIT_JSON_PATH")
    credits = Credit.load_credit_file(path)
    print(credits)


if __name__ == '__main__':
    from dotenv import load_dotenv

    load_dotenv()
    # example_read()
    example_write()
    credit_list = read_credits()
    for credit in credit_list:
        credit.create_empty_statement()
    # write_credits(credit_list)
    print(credit_list)
