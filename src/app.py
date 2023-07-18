import datetime
import json
import os
import tkinter as tk
import boto3

import dateutil.parser
import jsons
from dotenv import load_dotenv

from models import read_credits, Payment, write_credits


class MyCreditWindow:
    TITLE = "Credit Card :: Statements"

    def __init__(self):
        self.credits = read_credits()
        self.n_credits = len(self.credits)
        self.credit_id = 0
        self.statements_ids = [int(os.getenv("CREDIT_STATEMENT_ID")) for _ in self.credits]

        # main window
        self.window = tk.Tk()
        self.window.title(self.TITLE)

        # top frame
        self.frm_credit = tk.Frame(master=self.window)
        self.btn_move_left = tk.Button(master=self.frm_credit,
                                       text="<-",
                                       command=lambda: self.credit_move(-1))
        self.lbl_credit_id = tk.Label(master=self.frm_credit,
                                      text="--/--", font=("Courier",))
        self.btn_move_right = tk.Button(master=self.frm_credit,
                                        text="->",
                                        command=lambda: self.credit_move(1))

        self.frm_credit.pack()
        self.btn_move_left.pack(expand=True, fill="both", side="left")
        self.lbl_credit_id.pack(expand=True, fill="both", side="left")
        self.btn_move_right.pack(expand=True, fill="both", side="left")

        # middle frame
        self.frm_credit = tk.Frame(master=self.window)
        self.lbl_credit_name = tk.Label(master=self.frm_credit, font=("Arial", 25), text="")
        self.lbl_credit_bank = tk.Label(master=self.frm_credit, font=("Arial", 25), text="")
        self.frm_credit.pack()
        self.lbl_credit_name.pack()
        self.lbl_credit_bank.pack()

        # statement frame
        self.month = tk.StringVar()
        self.year = tk.StringVar()
        self.closing_date = tk.StringVar()
        self.due_date = tk.StringVar()
        self.required_min_payment1 = tk.StringVar()
        self.required_min_payment2 = tk.StringVar()
        self.required_full_payment = tk.StringVar()
        self.payed = tk.StringVar()

        self.frm_statement = tk.Frame(master=self.window)
        self.lbl_stm_month = tk.Label(master=self.frm_statement, text="Month/Year")
        self.txt_stm_month = tk.Entry(master=self.frm_statement, textvariable=self.month, width=4)
        self.txt_stm_year = tk.Entry(master=self.frm_statement, textvariable=self.year, width=6)
        self.lbl_closing_date = tk.Label(master=self.frm_statement, text="Closing Date")
        self.txt_closing_date = tk.Entry(master=self.frm_statement, textvariable=self.closing_date, width=12)
        self.lbl_due_date = tk.Label(master=self.frm_statement, text="Due Date")
        self.txt_due_date = tk.Entry(master=self.frm_statement, textvariable=self.due_date, width=12)
        self.lbl_required_min_payment1 = tk.Label(master=self.frm_statement, text="Min Payment#1")
        self.txt_required_min_payment1 = tk.Entry(master=self.frm_statement, textvariable=self.required_min_payment1,
                                                  width=12, font=("Courier",), justify="right")
        self.lbl_pending_for_min_payment1 = tk.Label(master=self.frm_statement, text="", foreground="red")
        self.lbl_required_min_payment2 = tk.Label(master=self.frm_statement, text="Min Payment#2")
        self.txt_required_min_payment2 = tk.Entry(master=self.frm_statement, textvariable=self.required_min_payment2,
                                                  width=12, font=("Courier",), justify="right")
        self.lbl_pending_for_min_payment2 = tk.Label(master=self.frm_statement, text="", foreground="red")
        self.lbl_required_full_payment = tk.Label(master=self.frm_statement, text="Full Payment")
        self.txt_required_full_payment = tk.Entry(master=self.frm_statement, textvariable=self.required_full_payment,
                                                  width=12, font=("Courier",), justify="right")
        self.lbl_pending_for_full_payment = tk.Label(master=self.frm_statement, text="", foreground="red")

        self.lbl_payed = tk.Label(master=self.frm_statement, text="Payed")
        self.txt_payed = tk.Entry(master=self.frm_statement, textvariable=self.payed,
                                  width=12, font=("Courier",), justify="right", state=tk.DISABLED)

        self.frm_statement.pack()
        self.lbl_stm_month.grid(row=0, column=0)
        self.txt_stm_month.grid(row=0, column=1)
        self.txt_stm_year.grid(row=0, column=2)
        self.lbl_closing_date.grid(row=1, column=0)
        self.txt_closing_date.grid(row=1, column=1, columnspan=2)
        self.lbl_due_date.grid(row=2, column=0)
        self.txt_due_date.grid(row=2, column=1, columnspan=2)

        self.lbl_required_min_payment1.grid(row=3, column=0)
        self.txt_required_min_payment1.grid(row=3, column=1, columnspan=2)
        self.lbl_pending_for_min_payment1.grid(row=3, column=3)

        self.lbl_required_min_payment2.grid(row=4, column=0)
        self.txt_required_min_payment2.grid(row=4, column=1, columnspan=2)
        self.lbl_pending_for_min_payment2.grid(row=4, column=3)

        self.lbl_required_full_payment.grid(row=5, column=0)
        self.txt_required_full_payment.grid(row=5, column=1, columnspan=2)
        self.lbl_pending_for_full_payment.grid(row=5, column=3)

        self.lbl_payed.grid(row=6, column=0)
        self.txt_payed.grid(row=6, column=1, columnspan=2)

        # payments
        self.frm_payments = tk.Frame(master=self.window)
        self.frm_payments.pack()
        self.lbl_deposits = tk.Label(master=self.frm_payments, text="Payments")
        self.txt_payments = tk.Text(master=self.frm_payments, width=64, height=18)
        self.btn_add_payment = tk.Button(master=self.frm_payments, text="Add Payment", command=self.add_payment)
        self.btn_update_payments = tk.Button(master=self.frm_payments, text="After Edit -> Update!",
                                             command=self.update_payments)
        self.lbl_deposits.grid(row=0, column=0)
        self.txt_payments.grid(row=0, column=1)
        self.btn_add_payment.grid(row=0, column=2)
        self.btn_update_payments.grid(row=1, column=2)

        self.update_credit_move_label()

        # actions frame
        self.frm_actions = tk.Frame(master=self.window)
        self.btn_next = tk.Button(master=self.frm_actions, text="Create next Statement",
                                  command=self.create_next_statement)
        self.btn_save = tk.Button(master=self.frm_actions, text="Save!", command=self.save)
        self.frm_actions.pack()
        self.btn_next.grid(row=0, column=0)
        self.btn_save.grid(row=0, column=1)

    def update_credit_move_label(self):
        text = f"{self.credit_id + 1}/{self.n_credits}"
        self.lbl_credit_id.config(text=text)
        self.lbl_credit_name.config(text=self.credits[self.credit_id].name)
        self.lbl_credit_bank.config(text=self.credits[self.credit_id].bank.value)

        m = self.credits[self.credit_id].statements[self.statements_ids[self.credit_id]].month
        y = self.credits[self.credit_id].statements[self.statements_ids[self.credit_id]].year
        cd = self.credits[self.credit_id].statements[self.statements_ids[self.credit_id]].closing_date
        dd = self.credits[self.credit_id].statements[self.statements_ids[self.credit_id]].due_date
        p1 = self.credits[self.credit_id].statements[self.statements_ids[self.credit_id]].required_min_payment1
        p2 = self.credits[self.credit_id].statements[self.statements_ids[self.credit_id]].required_min_payment2
        pf = self.credits[self.credit_id].statements[self.statements_ids[self.credit_id]].required_full_payment

        pp1 = self.credits[self.credit_id].statements[self.statements_ids[self.credit_id]].pending_for_min_payment1
        pp2 = self.credits[self.credit_id].statements[self.statements_ids[self.credit_id]].pending_for_min_payment2
        ppf = self.credits[self.credit_id].statements[self.statements_ids[self.credit_id]].pending_for_full_payment
        p = self.credits[self.credit_id].statements[self.statements_ids[self.credit_id]].payed

        fp_text = "Exceeded ✅" if p > pf else ("Covered ✅" if ppf == 0 else f"Pending {ppf / 100:,.2f}")

        self.month.set(str(m))
        self.year.set(str(y))
        self.closing_date.set(str(cd))
        self.due_date.set(str(dd))
        self.required_min_payment1.set(f"{p1 / 100:,.2f}")
        self.required_min_payment2.set(f"{p2 / 100:,.2f}")
        self.required_full_payment.set(f"{pf / 100:,.2f}")
        self.payed.set(f"{p / 100:,.2f}")
        self.lbl_pending_for_min_payment1.config(text="Covered ✅" if pp1 == 0 else f"Pending {pp1 / 100:,.2f}")
        self.lbl_pending_for_min_payment2.config(text="Covered ✅" if pp2 == 0 else f"Pending {pp2 / 100:,.2f}")
        self.lbl_pending_for_full_payment.config(text=fp_text)

        payments = self.credits[self.credit_id].statements[self.statements_ids[self.credit_id]].payments
        payments_dict = [json.loads(jsons.dumps(p)) for p in payments]
        payments_text = json.dumps(payments_dict, indent=3)
        self.txt_payments.delete("1.0", tk.END)
        self.txt_payments.insert(tk.END, payments_text)

    def credit_move(self, k: int):
        self.credit_id = (self.n_credits + self.credit_id + k) % self.n_credits
        self.update_credit_move_label()

    def add_payment(self):
        new_payment = Payment(payment_date=datetime.date.today(), amount=0, proof_of_payment="PATH")
        self.credits[self.credit_id].statements[self.statements_ids[self.credit_id]].payments.append(new_payment)
        self.update_credit_move_label()

    def update_payments(self):
        month = int(self.month.get())
        year = int(self.year.get())
        closing_date = dateutil.parser.parse(self.closing_date.get()).date()
        due_date = dateutil.parser.parse(self.due_date.get()).date()
        min_payment1 = round(float(self.required_min_payment1.get().replace(",", "")) * 100)
        min_payment2 = round(float(self.required_min_payment2.get().replace(",", "")) * 100)
        full_payment = round(float(self.required_full_payment.get().replace(",", "")) * 100)

        current_statement = self.credits[self.credit_id].statements[self.statements_ids[self.credit_id]]
        current_statement.month = month
        current_statement.year = year
        current_statement.closing_date = closing_date
        current_statement.due_date = due_date
        current_statement.required_min_payment1 = min_payment1
        current_statement.required_min_payment2 = min_payment2
        current_statement.required_full_payment = full_payment

        content = self.txt_payments.get("1.0", tk.END)
        new_payments = json.loads(content)
        new_payments = [jsons.loads(json.dumps(x), cls=Payment) for x in new_payments]

        current_statement.payments = new_payments
        current_statement.update()

        self.update_credit_move_label()

    def create_next_statement(self):
        for credit in self.credits:
            credit.create_empty_statement()
        self.update_credit_move_label()

    def save(self):
        write_credits(self.credits)

    def mainloop(self):
        self.window.geometry("800x600")
        self.window.mainloop()


if __name__ == '__main__':
    load_dotenv()
    boto3.setup_default_session(profile_name='mayorga@cimat.mx')

    w = MyCreditWindow()
    w.mainloop()
