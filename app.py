import os
import base64
import hashlib
import hmac
from datetime import date, datetime

import streamlit as st
import pandas as pd
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    and_,
    func,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session
from contextlib import contextmanager

# ============================================================
# KONFIGURASI DATABASE
# ============================================================

# DATABASE_URL disimpan di .streamlit/secrets.toml
# DATABASE_URL = "mysql+pymysql://root:password@127.0.0.1:3306/accounting_db"
DATABASE_URL = st.secrets["DATABASE_URL"]

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))
Base = declarative_base()


# ============================================================
# DEFINISI MODEL SQLALCHEMY (MAPPING KE TABEL DJANGO)
# ============================================================

class User(Base):
    __tablename__ = "auth_user"

    id = Column(Integer, primary_key=True)
    password = Column(String(128), nullable=False)
    last_login = Column(DateTime)
    is_superuser = Column(Boolean, default=False)
    username = Column(String(150), nullable=False)
    first_name = Column(String(150), default="")
    last_name = Column(String(150), default="")
    email = Column(String(254), default="")
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    date_joined = Column(DateTime)


class Company(Base):
    __tablename__ = "accounting_company"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), default="D'Pongs Wisata Keluarga")
    logo = Column(String(100))  # path file, kita tidak gunakan di Streamlit
    currency = Column(String(10), default="IDR")


class Account(Base):
    __tablename__ = "accounting_account"

    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    account_type = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"{self.code} {self.name}"


class JournalEntry(Base):
    __tablename__ = "accounting_journalentry"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("accounting_company.id"), nullable=True)
    date = Column(Date, nullable=False)
    number = Column(String(100), nullable=False)
    description = Column(String, nullable=False)
    is_adjustment = Column(Boolean, default=False)
    created_by_id = Column(Integer, ForeignKey("auth_user.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company")
    created_by = relationship("User")
    lines = relationship("JournalLine", back_populates="entry")


class JournalLine(Base):
    __tablename__ = "accounting_journalline"

    id = Column(Integer, primary_key=True)
    entry_id = Column(Integer, ForeignKey("accounting_journalentry.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounting_account.id"), nullable=False)
    is_debit = Column(Boolean, nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    tax_ppn = Column(Numeric(18, 2))

    entry = relationship("JournalEntry", back_populates="lines")
    account = relationship("Account")

    def __repr__(self):
        side = "D" if self.is_debit else "K"
        return f"{self.entry.number} {self.account} {side} {self.amount}"


class ClosingStatus(Base):
    __tablename__ = "accounting_closingstatus"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, unique=True, nullable=False)
    is_closed = Column(Boolean, default=False)
    closed_at = Column(DateTime, default=datetime.utcnow)


# ============================================================
# HELPER DB
# ============================================================

@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def current_year():
    return date.today().year


# ============================================================
# AUTENTIKASI (COCOK DENGAN HASH PASSWORD DJANGO)
# ============================================================

def verify_django_password(raw_password: str, encoded: str) -> bool:
    """
    Verifikasi hash password Django pbkdf2_sha256.
    Contoh format:
    pbkdf2_sha256$600000$salt$hash
    """
    try:
        algorithm, iterations_str, salt, hash_value = encoded.split("$", 3)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    try:
        iterations = int(iterations_str)
    except ValueError:
        return False

    dk = hashlib.pbkdf2_hmac(
        "sha256",
        raw_password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    computed = base64.b64encode(dk).decode("ascii").strip()
    return hmac.compare_digest(computed, hash_value)


def authenticate_email(email: str, password: str):
    with get_session() as session:
        user = (
            session.query(User)
            .filter(User.email == email, User.is_active == True)  # noqa: E712
            .first()
        )

        if not user:
            return None

        if verify_django_password(password, user.password):
            return user
        return None


# ============================================================
# LOGIKA AKUNTANSI (TRIAL BALANCE, ADJUSTED TB, LAPORAN)
# ============================================================

def is_year_closed(session, year: int) -> bool:
    status = (
        session.query(ClosingStatus)
        .filter(ClosingStatus.year == year, ClosingStatus.is_closed == True)  # noqa: E712
        .first()
    )
    return status is not None


def compute_trial_balance(session, year: int):
    """
    Neraca saldo sebelum penyesuaian, hanya jurnal umum (is_adjustment=False).
    """
    accounts = (
        session.query(Account)
        .filter(Account.is_active == True)  # noqa: E712
        .order_by(Account.code)
        .all()
    )

    rows = []
    total_debit = 0.0
    total_credit = 0.0

    for acc in accounts:
        lines = (
            session.query(JournalLine)
            .join(JournalEntry)
            .filter(
                JournalLine.account_id == acc.id,
                JournalEntry.date >= date(year, 1, 1),
                JournalEntry.date <= date(year, 12, 31),
                JournalEntry.is_adjustment == False,  # noqa: E712
            )
        )

        debit_sum = lines.filter(JournalLine.is_debit == True).with_entities(
            func.coalesce(func.sum(JournalLine.amount), 0)
        ).scalar()  # noqa: E712

        credit_sum = lines.filter(JournalLine.is_debit == False).with_entities(
            func.coalesce(func.sum(JournalLine.amount), 0)
        ).scalar()  # noqa: E712

        debit_sum = float(debit_sum or 0)
        credit_sum = float(credit_sum or 0)

        if debit_sum >= credit_sum:
            debit = debit_sum - credit_sum
            credit = 0.0
        else:
            debit = 0.0
            credit = credit_sum - debit_sum

        total_debit += debit
        total_credit += credit

        rows.append(
            {
                "Kode Akun": acc.code,
                "Nama Akun": acc.name,
                "Debit": debit,
                "Kredit": credit,
            }
        )

    return rows, total_debit, total_credit


def build_adjusted_trial_balance(session, year: int):
    """
    Neraca saldo setelah penyesuaian:
    - Saldo awal dari jurnal umum (is_adjustment=False)
    - Ditambah pengaruh jurnal penyesuaian (is_adjustment=True)
    """
    accounts = (
        session.query(Account)
        .filter(Account.is_active == True)  # noqa: E712
        .order_by(Account.code)
        .all()
    )

    rows = []
    total_debit = 0.0
    total_credit = 0.0

    for acc in accounts:
        general_lines = (
            session.query(JournalLine)
            .join(JournalEntry)
            .filter(
                JournalLine.account_id == acc.id,
                JournalEntry.date >= date(year, 1, 1),
                JournalEntry.date <= date(year, 12, 31),
                JournalEntry.is_adjustment == False,  # noqa: E712
            )
        )

        debit_gen = general_lines.filter(JournalLine.is_debit == True).with_entities(
            func.coalesce(func.sum(JournalLine.amount), 0)
        ).scalar()  # noqa: E712

        credit_gen = general_lines.filter(JournalLine.is_debit == False).with_entities(
            func.coalesce(func.sum(JournalLine.amount), 0)
        ).scalar()  # noqa: E712

        saldo_awal = float(debit_gen or 0) - float(credit_gen or 0)

        adj_lines = (
            session.query(JournalLine)
            .join(JournalEntry)
            .filter(
                JournalLine.account_id == acc.id,
                JournalEntry.date >= date(year, 1, 1),
                JournalEntry.date <= date(year, 12, 31),
                JournalEntry.is_adjustment == True,  # noqa: E712
            )
        )

        debit_adj = adj_lines.filter(JournalLine.is_debit == True).with_entities(
            func.coalesce(func.sum(JournalLine.amount), 0)
        ).scalar()  # noqa: E712

        credit_adj = adj_lines.filter(JournalLine.is_debit == False).with_entities(
            func.coalesce(func.sum(JournalLine.amount), 0)
        ).scalar()  # noqa: E712

        saldo_akhir = saldo_awal + float(debit_adj or 0) - float(credit_adj or 0)

        if saldo_akhir >= 0:
            debit = saldo_akhir
            credit = 0.0
        else:
            debit = 0.0
            credit = abs(saldo_akhir)

        total_debit += debit
        total_credit += credit

        rows.append(
            {
                "Kode Akun": acc.code,
                "Nama Akun": acc.name,
                "Debit": debit,
                "Kredit": credit,
            }
        )

    return rows, total_debit, total_credit


def get_income_statement_data(session, year: int):
    """
    Laporan laba rugi:
    - total pendapatan
    - total beban
    - laba bersih
    """
    revenue_accounts = session.query(Account).filter(Account.account_type == "revenue").all()
    expense_accounts = session.query(Account).filter(Account.account_type == "expense").all()

    def calc_total(accounts):
        total = 0.0
        for acc in accounts:
            lines = (
                session.query(JournalLine)
                .join(JournalEntry)
                .filter(
                    JournalLine.account_id == acc.id,
                    JournalEntry.date >= date(year, 1, 1),
                    JournalEntry.date <= date(year, 12, 31),
                )
            )
            debit = lines.filter(JournalLine.is_debit == True).with_entities(
                func.coalesce(func.sum(JournalLine.amount), 0)
            ).scalar()  # noqa: E712
            credit = lines.filter(JournalLine.is_debit == False).with_entities(
                func.coalesce(func.sum(JournalLine.amount), 0)
            ).scalar()  # noqa: E712
            total += float(credit or 0) - float(debit or 0)
        return total

    total_revenue = calc_total(revenue_accounts)
    total_expense = calc_total(expense_accounts)
    net_income = total_revenue - total_expense
    return total_revenue, total_expense, net_income


def get_balance_sheet_data(session, year: int):
    """
    Ringkasan neraca:
    total aset, liabilitas, dan ekuitas.
    """
    asset_accounts = session.query(Account).filter(Account.account_type == "asset").all()
    liability_accounts = session.query(Account).filter(Account.account_type == "liability").all()
    equity_accounts = session.query(Account).filter(Account.account_type == "equity").all()

    def calc_balance(accounts):
        total = 0.0
        for acc in accounts:
            lines = (
                session.query(JournalLine)
                .join(JournalEntry)
                .filter(
                    JournalLine.account_id == acc.id,
                    JournalEntry.date >= date(year, 1, 1),
                    JournalEntry.date <= date(year, 12, 31),
                )
            )
            debit = lines.filter(JournalLine.is_debit == True).with_entities(
                func.coalesce(func.sum(JournalLine.amount), 0)
            ).scalar()  # noqa: E712
            credit = lines.filter(JournalLine.is_debit == False).with_entities(
                func.coalesce(func.sum(JournalLine.amount), 0)
            ).scalar()  # noqa: E712

            if acc.account_type == "asset":
                total += float(debit or 0) - float(credit or 0)
            else:
                total += float(credit or 0) - float(debit or 0)
        return total

    total_asset = calc_balance(asset_accounts)
    total_liability = calc_balance(liability_accounts)
    total_equity = calc_balance(equity_accounts)
    return total_asset, total_liability, total_equity


# ============================================================
# HALAMAN UI STREAMLIT
# ============================================================

def login_page():
    st.title("Login")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Masuk")

    if submitted:
        if not email or not password:
            st.error("Email dan password wajib diisi")
            return

        user = authenticate_email(email, password)
        if user:
            st.session_state["user"] = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
            st.success("Login berhasil")
            st.rerun()
        else:
            st.error("Email atau password salah")


def page_dashboard():
    st.header("Dashboard")
    year = st.number_input("Tahun", min_value=2000, max_value=2100, value=current_year(), step=1)

    with get_session() as session:
        total_rev, total_exp, net_income = get_income_statement_data(session, year)
        total_asset, total_liab, total_equity = get_balance_sheet_data(session, year)
        closed = is_year_closed(session, year)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pendapatan", f"{total_rev:,.2f}")
    col2.metric("Total Beban", f"{total_exp:,.2f}")
    col3.metric("Laba Bersih", f"{net_income:,.2f}")

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Aset", f"{total_asset:,.2f}")
    c2.metric("Total Liabilitas", f"{total_liab:,.2f}")
    c3.metric("Total Ekuitas", f"{total_equity:,.2f}")

    st.markdown("---")
    st.write(f"Status tahun {year}: {'Proses penyesuaian' if closed else 'Belum proses penyesuaian'}")


def page_journal(is_adjustment: bool = False):
    title = "Jurnal Penyesuaian" if is_adjustment else "Jurnal Umum"
    key_suffix = "adj" if is_adjustment else "gen"

    st.header(title)
    year = st.number_input("Tahun", min_value=2000, max_value=2100, value=current_year(), step=1)

    with get_session() as session:
        closed = is_year_closed(session, year)

        # ambil jurnal
        q = (
            session.query(JournalEntry)
            .filter(
                JournalEntry.date >= date(year, 1, 1),
                JournalEntry.date <= date(year, 12, 31),
                JournalEntry.is_adjustment == is_adjustment,
            )
            .order_by(JournalEntry.date, JournalEntry.number)
        )
        entries = q.all()

        # total debit / kredit
        total_debit = 0.0
        total_credit = 0.0
        table_rows = []

        for e in entries:
            for line in e.lines:
                amt = float(line.amount or 0)
                if line.is_debit:
                    total_debit += amt
                else:
                    total_credit += amt

                table_rows.append(
                    {
                        "ID": e.id,
                        "Tanggal": e.date,
                        "No": e.number,
                        "Keterangan": e.description,
                        "Akun": f"{line.account.code} {line.account.name}",
                        "Debit": amt if line.is_debit else 0.0,
                        "Kredit": amt if not line.is_debit else 0.0,
                    }
                )

        # ===========================
        # TABEL + TOMBOL EDIT/DELETE
        # ===========================
        st.subheader("Daftar Jurnal")

        if table_rows:
            df = pd.DataFrame(table_rows)

            # baris total di tabel
            total_row = {
                "ID": "",
                "Tanggal": "",
                "No": "",
                "Keterangan": "Total",
                "Akun": "",
                "Debit": total_debit,
                "Kredit": total_credit,
            }
            df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

            st.dataframe(df, use_container_width=True)

            # tombol edit/delete per entry
            for e in entries:
                cols = st.columns([6, 1, 1])
                cols[0].write(f"{e.date} | {e.number} | {e.description}")

                if cols[1].button("Edit", key=f"edit_{key_suffix}_{e.id}"):
                    st.session_state[f"edit_entry_id_{key_suffix}"] = e.id
                    st.rerun()

                if cols[2].button("Delete", key=f"delete_{key_suffix}_{e.id}"):
                    st.session_state[f"delete_entry_id_{key_suffix}"] = e.id
                    st.rerun()

        else:
            st.info("Belum ada data jurnal untuk tahun ini.")

        # ambil daftar akun untuk form
        accounts = (
            session.query(Account)
            .filter(Account.is_active == True)
            .order_by(Account.code)
            .all()
        )
        account_options = {f"{a.code} - {a.name}": a.id for a in accounts}
        account_labels = list(account_options.keys())

        # ===========================
        # FORM EDIT JURNAL
        # ===========================
        edit_key = f"edit_entry_id_{key_suffix}"
        if edit_key in st.session_state:
            edit_id = st.session_state[edit_key]

            st.markdown("---")
            st.subheader("Edit Jurnal")

            entry = session.query(JournalEntry).filter(JournalEntry.id == edit_id).first()
            lines = session.query(JournalLine).filter(JournalLine.entry_id == edit_id).all()

            with st.form(f"form_edit_{key_suffix}"):
                col1, col2 = st.columns(2)
                new_date = col1.date_input("Tanggal", value=entry.date)
                new_number = col2.text_input("Nomor", value=entry.number)
                new_desc = st.text_input("Keterangan", value=entry.description)

                st.write("Edit Baris Jurnal:")
                edited_lines = []

                for idx, l in enumerate(lines):
                    c1, c2, c3 = st.columns([3, 1, 2])
                    default_label = f"{l.account.code} - {l.account.name}"

                    acc_label = c1.selectbox(
                        f"Akun {idx + 1}",
                        options=account_labels,
                        index=account_labels.index(default_label),
                        key=f"edit_acc_{key_suffix}_{edit_id}_{idx}",
                    )
                    is_debit_line = c2.checkbox(
                        "Debit",
                        value=l.is_debit,
                        key=f"edit_deb_{key_suffix}_{edit_id}_{idx}",
                    )
                    amount_line = c3.number_input(
                        "Jumlah",
                        value=float(l.amount),
                        step=1000.0,
                        key=f"edit_amt_{key_suffix}_{edit_id}_{idx}",
                    )

                    edited_lines.append((acc_label, is_debit_line, amount_line))

                saved = st.form_submit_button("Simpan Perubahan")

            if saved:
                # update header
                entry.date = new_date
                entry.number = new_number
                entry.description = new_desc

                # hapus line lama
                session.query(JournalLine).filter(JournalLine.entry_id == edit_id).delete()

                # simpan line baru
                for acc_label, is_debit_line, amount_line in edited_lines:
                    acc_id = account_options[acc_label]
                    session.add(
                        JournalLine(
                            entry_id=edit_id,
                            account_id=acc_id,
                            is_debit=is_debit_line,
                            amount=float(amount_line),
                        )
                    )

                session.commit()
                st.success("Jurnal berhasil diperbarui.")
                del st.session_state[edit_key]
                st.rerun()

        # ===========================
        # KONFIRMASI DELETE
        # ===========================
        delete_key = f"delete_entry_id_{key_suffix}"
        if delete_key in st.session_state:
            del_id = st.session_state[delete_key]

            st.markdown("---")
            st.error("Anda yakin ingin menghapus jurnal ini?")

            c1, c2 = st.columns(2)
            if c1.button("Ya, hapus", key=f"confirm_del_{key_suffix}"):
                session.query(JournalLine).filter(JournalLine.entry_id == del_id).delete()
                session.query(JournalEntry).filter(JournalEntry.id == del_id).delete()
                session.commit()

                st.success("Jurnal sudah dihapus.")
                del st.session_state[delete_key]
                st.rerun()

            if c2.button("Batal", key=f"cancel_del_{key_suffix}"):
                del st.session_state[delete_key]
                st.rerun()

        st.markdown("---")

        # ===========================
        # RULE TUTUP BUKU UNTUK INPUT BARU
        # ===========================
        if is_adjustment and not closed:
            st.warning(f"Tahun {year} belum proses penyesuaian, jurnal penyesuaian tidak bisa dibuat.")
            return

        if (not is_adjustment) and closed:
            st.warning(f"Tahun {year} sudah proses penyesuaian, jurnal umum baru tidak bisa dibuat.")
            return

        # ===========================
        # FORM TAMBAH JURNAL BARU
        # ===========================
        st.subheader(f"Tambah {title}")

        with st.form(f"form_{key_suffix}"):
            col_date, col_number = st.columns(2)
            trans_date = col_date.date_input("Tanggal", value=date.today())
            number = col_number.text_input("Nomor", value="")

            description = st.text_input("Keterangan", value="")

            num_lines = st.number_input("Jumlah baris", min_value=1, max_value=10, value=2, step=1)

            line_inputs = []
            for i in range(int(num_lines)):
                st.markdown(f"Baris {i + 1}")
                c1, c2, c3 = st.columns([3, 1, 2])
                acc_label = c1.selectbox(
                    "Akun",
                    options=["(pilih)"] + account_labels,
                    key=f"acc_{key_suffix}_{i}",
                )
                is_debit_line = c2.checkbox(
                    "Debit",
                    value=(i == 0),
                    key=f"debit_{key_suffix}_{i}",
                )
                amount_line = c3.number_input(
                    "Jumlah",
                    min_value=0.0,
                    step=1000.0,
                    key=f"amount_{key_suffix}_{i}",
                )

                line_inputs.append((acc_label, is_debit_line, amount_line))

            submitted = st.form_submit_button("Simpan")

        if submitted:
            if not number:
                st.error("Nomor transaksi wajib diisi.")
                return
            if not description:
                st.error("Keterangan wajib diisi.")
                return

            debit_sum = 0.0
            credit_sum = 0.0
            valid_lines = []

            for acc_label, is_debit_line, amount_line in line_inputs:
                if acc_label == "(pilih)" or amount_line <= 0:
                    continue
                account_id = account_options.get(acc_label)
                if not account_id:
                    continue
                amt = float(amount_line)
                if is_debit_line:
                    debit_sum += amt
                else:
                    credit_sum += amt
                valid_lines.append((account_id, is_debit_line, amt))

            if not valid_lines:
                st.error("Minimal satu baris jurnal harus diisi.")
                return

            if abs(debit_sum - credit_sum) > 0.001:
                st.error("Total debit dan kredit harus seimbang.")
                return

            # Simpan ke DB
            entry = JournalEntry(
                date=trans_date,
                number=number,
                description=description,
                is_adjustment=is_adjustment,
                created_by_id=st.session_state["user"]["id"],
            )
            session.add(entry)
            session.flush()

            for account_id, is_debit_line, amt in valid_lines:
                session.add(
                    JournalLine(
                        entry_id=entry.id,
                        account_id=account_id,
                        is_debit=is_debit_line,
                        amount=amt,
                    )
                )

            session.commit()
            st.success("Jurnal berhasil disimpan.")
            st.rerun()


def page_ledger():
    st.header("Buku Besar")
    year = st.number_input("Tahun", min_value=2000, max_value=2100, value=current_year(), step=1)

    with get_session() as session:
        accounts = (
            session.query(Account)
            .filter(Account.is_active == True)
            .order_by(Account.code)
            .all()
        )

        for acc in accounts:
            st.markdown(f"### {acc.code} - {acc.name}")

            # ambil semua transaksi akun
            lines = (
                session.query(JournalLine)
                .join(JournalEntry)
                .filter(
                    JournalLine.account_id == acc.id,
                    JournalEntry.date >= date(year, 1, 1),
                    JournalEntry.date <= date(year, 12, 31),
                )
                .order_by(JournalEntry.date, JournalEntry.number)
                .all()
            )

            if not lines:
                st.write("Tidak ada transaksi")
                st.markdown("---")
                continue

            rows = []
            saldo = 0.0
            no = 1

            for l in lines:
                debit = float(l.amount) if l.is_debit else 0.0
                credit = float(l.amount) if not l.is_debit else 0.0

                # pergerakan saldo
                saldo += debit - credit

                saldo_debit = saldo if saldo >= 0 else 0.0
                saldo_kredit = abs(saldo) if saldo < 0 else 0.0

                rows.append(
                    {
                        "No": no,
                        "Tanggal": l.entry.date.strftime("%d-%m-%Y"),
                        "Keterangan": l.entry.description,
                        "No Trans": l.entry.number,
                        "Debit": debit,
                        "Kredit": credit,
                        "Saldo Debit": saldo_debit,
                        "Saldo Kredit": saldo_kredit,
                    }
                )
                no += 1

            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)

            st.markdown("---")


def page_trial_balance():
    st.header("Neraca Saldo")
    year = st.number_input("Tahun", min_value=2000, max_value=2100, value=current_year(), step=1)

    with get_session() as session:
        rows, total_debit, total_credit = compute_trial_balance(session, year)

    if rows:
        # tambah row akhir (Total)
        rows.append({
            "Kode Akun": "Total",
            "Nama Akun": "",
            "Debit": total_debit,
            "Kredit": total_credit
        })

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Belum ada data neraca saldo.")


def page_adjusted_trial_balance():
    st.header("Neraca Saldo Setelah Penyesuaian")
    year = st.number_input("Tahun", min_value=2000, max_value=2100, value=current_year(), step=1)

    with get_session() as session:
        rows, total_debit, total_credit = build_adjusted_trial_balance(session, year)

    if rows:
        rows.append({
            "Kode Akun": "Total",
            "Nama Akun": "",
            "Debit": total_debit,
            "Kredit": total_credit
        })

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Belum ada data neraca saldo setelah penyesuaian.")


def page_income_statement():
    st.header("Laporan Keuangan")
    year = st.number_input("Tahun", min_value=2000, max_value=2100, value=current_year(), step=1)

    with get_session() as session:
        accounts = session.query(Account).order_by(Account.code).all()

        # hitung saldo per akun untuk tahun berjalan
        account_balances = {}  # key: account.id, value: saldo sesuai normal balance

        for acc in accounts:
            lines = (
                session.query(JournalLine)
                .join(JournalEntry)
                .filter(
                    JournalLine.account_id == acc.id,
                    JournalEntry.date >= date(year, 1, 1),
                    JournalEntry.date <= date(year, 12, 31),
                )
            )
            debit = lines.filter(JournalLine.is_debit == True).with_entities(
                func.coalesce(func.sum(JournalLine.amount), 0)
            ).scalar()
            credit = lines.filter(JournalLine.is_debit == False).with_entities(
                func.coalesce(func.sum(JournalLine.amount), 0)
            ).scalar()

            debit = float(debit or 0)
            credit = float(credit or 0)

            # normal balance: asset, expense, prive debit; liability, equity, revenue credit
            if acc.account_type in ("asset", "expense", "prive"):
                balance = debit - credit
            else:
                balance = credit - debit

            account_balances[acc.id] = balance

        # =======================
        # LAPORAN LABA RUGI
        # =======================
        revenue_rows = []
        expense_rows = []

        for acc in accounts:
            bal = account_balances.get(acc.id, 0.0)
            if acc.account_type == "revenue":
                revenue_rows.append((acc.name, bal))
            elif acc.account_type == "expense":
                expense_rows.append((acc.name, bal))

        total_revenue = sum(x[1] for x in revenue_rows)
        total_expense = sum(x[1] for x in expense_rows)
        net_income = total_revenue - total_expense

        st.subheader(f"Laporan Laba Rugi")

        lr_rows = []
        lr_rows.append({"Transaksi": "Pendapatan", "Nominal": ""})
        for name, bal in revenue_rows:
            lr_rows.append({"Transaksi": name, "Nominal": f"{bal:,.2f}"})
        lr_rows.append({"Transaksi": "Total Pendapatan", "Nominal": f"{total_revenue:,.2f}"})

        lr_rows.append({"Transaksi": "Beban", "Nominal": ""})
        for name, bal in expense_rows:
            lr_rows.append({"Transaksi": name, "Nominal": f"{bal:,.2f}"})
        lr_rows.append({"Transaksi": "Total Beban", "Nominal": f"{total_expense:,.2f}"})

        lr_rows.append({"Transaksi": "Laba Bersih", "Nominal": f"{net_income:,.2f}"})

        df_lr = pd.DataFrame(lr_rows)
        df_lr_no_index = df_lr.set_index("Transaksi")
        st.table(df_lr_no_index)

        # =======================
        # LAPORAN PERUBAHAN MODAL
        # =======================
        equity_rows = []
        prive_rows = []

        for acc in accounts:
            bal = account_balances.get(acc.id, 0.0)
            if acc.account_type == "equity":
                equity_rows.append((acc.name, bal))
            elif acc.account_type == "prive":
                # prive normal debit, sudah ditangani di atas, biasanya positif kalau ada prive
                prive_rows.append((acc.name, bal))

        total_equity = sum(x[1] for x in equity_rows)
        total_prive = sum(x[1] for x in prive_rows)

        # modal akhir = ekuitas + laba bersih - prive
        modal_akhir = total_equity + net_income - total_prive

        st.markdown("")
        st.subheader(f"Laporan Perubahan Modal")

        lpm_rows = []
        lpm_rows.append({"Transaksi": "Ekuitas", "Nominal": ""})
        for name, bal in equity_rows:
            lpm_rows.append({"Transaksi": name, "Nominal": f"{bal:,.2f}"})
        lpm_rows.append({"Transaksi": "Total Ekuitas", "Nominal": f"{total_equity:,.2f}"})

        lpm_rows.append({"Transaksi": "Prive", "Nominal": ""})
        if prive_rows:
            for name, bal in prive_rows:
                lpm_rows.append({"Transaksi": name, "Nominal": f"{bal:,.2f}"})
        else:
            lpm_rows.append({"Transaksi": "Prive", "Nominal": f"{0:,.2f}"})
        lpm_rows.append({"Transaksi": "Total Prive", "Nominal": f"{total_prive:,.2f}"})

        lpm_rows.append({"Transaksi": "Modal Akhir", "Nominal": f"{modal_akhir:,.2f}"})

        df_lpm = pd.DataFrame(lpm_rows)
        df_lpm_no_index = df_lpm.set_index("Transaksi")
        st.table(df_lpm_no_index)

        # =======================
        # NERACA
        # =======================
        st.markdown("")
        st.subheader(f"Neraca")

        # Kategori Aktiva
        aset_lancar_rows = []
        aset_tetap_rows = []

        for acc in accounts:
            if acc.account_type != "asset":
                continue

            bal = account_balances.get(acc.id, 0.0)

            # kategori manual khusus
            if acc.name in ["Peralatan Outbond", "Akumulasi Penyusutan"]:
                aset_tetap_rows.append((acc.name, bal))
                continue

            # kategori otomatis berdasarkan kode
            try:
                code_int = int(acc.code)
            except ValueError:
                code_int = 0

            if code_int < 1500:
                aset_lancar_rows.append((acc.name, bal))
            else:
                aset_tetap_rows.append((acc.name, bal))

        total_aset_lancar = sum(x[1] for x in aset_lancar_rows)
        total_aset_tetap = sum(x[1] for x in aset_tetap_rows)
        total_aktiva = total_aset_lancar + total_aset_tetap

        # Tabel Aktiva
        st.write("Aktiva")
        aktiva_tabel = []

        aktiva_tabel.append({"Transaksi": "Aset Lancar", "Nominal": ""})
        for name, bal in aset_lancar_rows:
            aktiva_tabel.append({"Transaksi": name, "Nominal": f"{bal:,.2f}"})
        aktiva_tabel.append({"Transaksi": "Jumlah Aset Lancar", "Nominal": f"{total_aset_lancar:,.2f}"})

        aktiva_tabel.append({"Transaksi": "Aset Tetap", "Nominal": ""})
        for name, bal in aset_tetap_rows:
            aktiva_tabel.append({"Transaksi": name, "Nominal": f"{bal:,.2f}"})
        aktiva_tabel.append({"Transaksi": "Jumlah Aset Tetap", "Nominal": f"{total_aset_tetap:,.2f}"})

        aktiva_tabel.append({"Transaksi": "Total Aktiva", "Nominal": f"{total_aktiva:,.2f}"})

        df_aktiva = pd.DataFrame(aktiva_tabel)
        df_aktiva_no_index = df_aktiva.set_index("Transaksi")
        st.table(df_aktiva_no_index)

        # Pasiva: Liabilitas + Modal Akhir
        liab_rows = []
        for acc in accounts:
            if acc.account_type == "liability":
                bal = account_balances.get(acc.id, 0.0)
                liab_rows.append((acc.name, bal))

        total_liab = sum(x[1] for x in liab_rows)
        total_pasiva = total_liab + modal_akhir

        st.write("Pasiva")
        pasiva_tabel = []
        pasiva_tabel.append({"Transaksi": "Liabilitas", "Nominal": ""})
        for name, bal in liab_rows:
            pasiva_tabel.append({"Transaksi": name, "Nominal": f"{bal:,.2f}"})
        pasiva_tabel.append({"Transaksi": "Jumlah Liabilitas", "Nominal": f"{total_liab:,.2f}"})

        pasiva_tabel.append({"Transaksi": "Modal Akhir", "Nominal": ""})
        pasiva_tabel.append({"Transaksi": "Modal Akhir", "Nominal": f"{modal_akhir:,.2f}"})
        pasiva_tabel.append({"Transaksi": "Total Pasiva", "Nominal": f"{total_pasiva:,.2f}"})

        df_pasiva = pd.DataFrame(pasiva_tabel)
        df_pasiva_no_index = df_pasiva.set_index("Transaksi")
        st.table(df_pasiva_no_index)


def page_accounts():
    st.header("Daftar Akun")

    with get_session() as session:
        accounts = (
            session.query(Account)
            .order_by(Account.code)
            .all()
        )

        rows = [
            {
                "ID": a.id,
                "Kode": a.code,
                "Nama": a.name,
                "Tipe": a.account_type,
                "Aktif": a.is_active,
            }
            for a in accounts
        ]

        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Belum ada akun.")

        st.subheader("Aksi Akun")
        for a in accounts:
            c1, c2, c3 = st.columns([6, 1, 1])
            c1.write(f"{a.code} - {a.name} ({a.account_type})")

            if c2.button("Edit", key=f"edit_account_{a.id}"):
                st.session_state["edit_account_id"] = a.id
                st.rerun()

            if c3.button("Delete", key=f"del_account_{a.id}"):
                st.session_state["delete_account_id"] = a.id
                st.rerun()

        # pilihan tipe akun
        type_choices = [
            ("asset", "Aset"),
            ("liability", "Liabilitas"),
            ("equity", "Ekuitas"),
            ("prive", "Prive"),
            ("revenue", "Pendapatan"),
            ("expense", "Beban"),
        ]

        # ===========================
        # FORM EDIT AKUN
        # ===========================
        if "edit_account_id" in st.session_state:
            edit_id = st.session_state["edit_account_id"]
            acc = session.query(Account).filter(Account.id == edit_id).first()

            st.markdown("---")
            st.subheader("Edit Akun")

            with st.form("form_edit_account"):
                code = st.text_input("Kode akun", value=acc.code)
                name = st.text_input("Nama akun", value=acc.name)
                account_type = st.selectbox(
                    "Tipe akun",
                    options=type_choices,
                    index=[t[0] for t in type_choices].index(acc.account_type),
                    format_func=lambda x: x[1],
                )
                is_active = st.checkbox("Aktif", value=acc.is_active)

                submitted_edit = st.form_submit_button("Simpan Perubahan")

            if submitted_edit:
                if not code or not name:
                    st.error("Kode dan nama akun wajib diisi.")
                else:
                    existing = (
                        session.query(Account)
                        .filter(Account.code == code, Account.id != edit_id)
                        .first()
                    )
                    if existing:
                        st.error("Kode akun sudah digunakan oleh akun lain.")
                    else:
                        acc.code = code
                        acc.name = name
                        acc.account_type = account_type[0]
                        acc.is_active = is_active
                        session.commit()
                        st.success("Akun berhasil diperbarui.")
                        del st.session_state["edit_account_id"]
                        st.rerun()

        # ===========================
        # KONFIRMASI DELETE AKUN
        # ===========================
        if "delete_account_id" in st.session_state:
            del_id = st.session_state["delete_account_id"]
            acc = session.query(Account).filter(Account.id == del_id).first()

            st.markdown("---")
            st.error(f"Yakin ingin menghapus akun: {acc.code} - {acc.name}?")

            used = (
                session.query(JournalLine)
                .filter(JournalLine.account_id == del_id)
                .first()
            )

            if used:
                st.warning("Akun ini sudah dipakai di jurnal, tidak bisa dihapus.")
                if st.button("Tutup pesan"):
                    del st.session_state["delete_account_id"]
                    st.rerun()
            else:
                c1, c2 = st.columns(2)
                if c1.button("Ya, hapus akun ini"):
                    session.delete(acc)
                    session.commit()
                    st.success("Akun berhasil dihapus.")
                    del st.session_state["delete_account_id"]
                    st.rerun()
                if c2.button("Batal"):
                    del st.session_state["delete_account_id"]
                    st.rerun()

        st.markdown("---")
        st.subheader("Tambah Akun Baru")

        # FORM TAMBAH AKUN
        with st.form("form_add_account"):
            code = st.text_input("Kode akun")
            name = st.text_input("Nama akun")
            account_type = st.selectbox(
                "Tipe akun",
                options=type_choices,
                format_func=lambda x: x[1],
            )
            is_active = st.checkbox("Aktif", value=True)
            submitted = st.form_submit_button("Simpan")

        if submitted:
            if not code or not name:
                st.error("Kode dan nama akun wajib diisi.")
                return

            existing = (
                session.query(Account)
                .filter(Account.code == code)
                .first()
            )
            if existing:
                st.error("Kode akun sudah ada.")
                return

            acc = Account(
                code=code,
                name=name,
                account_type=account_type[0],
                is_active=is_active,
            )
            session.add(acc)
            session.commit()
            st.success("Akun berhasil ditambahkan.")
            st.rerun()


def page_close_year():
    st.header("Penyesuaian")
    year = st.number_input("Tahun", min_value=2000, max_value=2100, value=current_year(), step=1)

    with get_session() as session:
        closed = is_year_closed(session, year)

        st.write(f"Status tahun {year}: {'Proses penyesuaian' if closed else 'Belum proses penyesuaian'}")

        col1, col2 = st.columns(2)
        if col1.button("Proses penyesesuaian"):
            if closed:
                st.warning("Saat ini sedang dalam proses penyesuaian.")
            else:
                status = (
                    session.query(ClosingStatus)
                    .filter(ClosingStatus.year == year)
                    .first()
                )
                if not status:
                    status = ClosingStatus(year=year, is_closed=True)
                    session.add(status)
                else:
                    status.is_closed = True
                session.commit()
                st.success(f"Tahun {year} proses penyesuian.")
                st.rerun()

        if col2.button("Buka kembali sebelum penyesuaian"):
            status = (
                session.query(ClosingStatus)
                .filter(ClosingStatus.year == year)
                .first()
            )
            if not status:
                st.warning("Belum melakukan proses penyesuaian untuk tahun ini.")
            else:
                status.is_closed = False
                session.commit()
                st.success(f"Tahun {year} sebelum penyesuaian.")
                st.rerun()


# ============================================================
# MAIN APP
# ============================================================

def main():
    st.set_page_config(page_title="D’Pongs Wisata Keluarga", layout="wide")

    if "user" not in st.session_state:
        st.session_state["user"] = None

    if st.session_state["user"] is None:
        login_page()
        return

    # Sidebar Header (center)
    st.sidebar.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)

    st.sidebar.image("logo.png", width=120)

    st.sidebar.markdown("""
    D’Pongs Wisata Keluarga
    """, unsafe_allow_html=True)

    st.sidebar.markdown("</div>", unsafe_allow_html=True)
    st.sidebar.markdown("---")

    # Sidebar
    st.sidebar.title("Menu")
    #st.sidebar.write(f"Login sebagai: {st.session_state['user']['username']}")

    page = st.sidebar.radio(
        "Navigasi",
        [
            "Dashboard",
            "Daftar Akun",
            "Jurnal Umum",
            "Buku Besar",
            "Neraca Saldo",
            "Jurnal Penyesuaian",
            "Neraca Saldo Penyesuaian",
            "Laporan Keuangan",
            "Penyesuaian",
        ],
    )

    if st.sidebar.button("Logout"):
        st.session_state["user"] = None
        st.rerun()

    # Routing halaman
    if page == "Dashboard":
        page_dashboard()
    elif page == "Daftar Akun":
        page_accounts()
    elif page == "Jurnal Umum":
        page_journal(is_adjustment=False)
    elif page == "Buku Besar":
        page_ledger()
    elif page == "Neraca Saldo":
        page_trial_balance()
    elif page == "Jurnal Penyesuaian":
        page_journal(is_adjustment=True)
    elif page == "Neraca Saldo Penyesuaian":
        page_adjusted_trial_balance()
    elif page == "Laporan Keuangan":
        page_income_statement()
    elif page == "Penyesuaian":
        page_close_year()


if __name__ == "__main__":
    main()
