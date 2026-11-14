import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, 
    QHBoxLayout, QGridLayout, QLabel, QLineEdit, QSpinBox, 
    QPushButton, QTableView, QComboBox, QMessageBox, QHeaderView
)
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtCore import Qt, QDate

class LibrarySystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistem Peminjaman Buku - Modern UI")
        self.setGeometry(300, 200, 950, 650)
        
        # Terapkan Global stylesheet untuk tampilan modern
        self.apply_stylesheet()
        
        self.init_db()
        self.setup_ui()

    def apply_stylesheet(self):
        # Styling menggunakan QSS (Qt Style Sheet)
        stylesheet = """
            QMainWindow {
                background-color: #f4f7f6;
            }
            QTabWidget::pane {
                border: 1px solid #d1d8db;
                background: white;
                border-radius: 6px;
                top: -1px;
            }
            QTabBar::tab {
                background: #e4e7eb;
                color: #4b6584;
                padding: 10px 20px;
                font-weight: bold;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background: #0984e3;
                color: white;
            }
            QLabel {
                color: #2f3542;
                font-size: 13px;
            }
            QLineEdit, QSpinBox, QComboBox {
                padding: 8px;
                border: 1px solid #ced6e0;
                border-radius: 4px;
                background: #ffffff;
                font-size: 13px;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border: 1px solid #0984e3;
            }
            QPushButton {
                background-color: #0984e3;
                color: white;
                border: none;
                padding: 9px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #74b9ff;
            }
            QPushButton#btn_delete {
                background-color: #ff4757;
            }
            QPushButton#btn_delete:hover {
                background-color: #ff6b81;
            }
            QTableView {
                border: 1px solid #ced6e0;
                background: white;
                alternate-background-color: #f1f2f6;
                selection-background-color: #74b9ff;
                selection-color: white;
                border-radius: 4px;
            }
        """
        self.setStyleSheet(stylesheet)

    def init_db(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("library.db")
        if not self.db.open():
            QMessageBox.critical(self, "Error", "Gagal membuka database!")
            return

        self.db.exec("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT,
                stock INTEGER DEFAULT 1
            )
        """)

        self.db.exec("""
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                borrower TEXT,
                loan_date TEXT,
                return_date TEXT,
                status TEXT DEFAULT 'active'
            )
        """)

    def setup_ui(self):
        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        # ================= TAB 1: KELOLA BUKU =================
        books_tab = QWidget()
        books_layout = QVBoxLayout(books_tab)
        books_layout.setContentsMargins(20, 20, 20, 20)
        books_layout.setSpacing(15)

        form_layout = QGridLayout()
        form_layout.setSpacing(10)
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Masukkan judul buku...")
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Masukkan nama penulis...")
        self.stock_input = QSpinBox()
        self.stock_input.setRange(1, 100)

        form_layout.addWidget(QLabel("Judul Buku:"), 0, 0)
        form_layout.addWidget(self.title_input, 0, 1)
        form_layout.addWidget(QLabel("Penulis:"), 1, 0)
        form_layout.addWidget(self.author_input, 1, 1)
        form_layout.addWidget(QLabel("Stok:"), 2, 0)
        form_layout.addWidget(self.stock_input, 2, 1)

        btn_layout = QHBoxLayout()
        self.add_book_btn = QPushButton("➕ Tambah Buku")
        self.update_book_btn = QPushButton("✏️ Update Buku")
        self.delete_book_btn = QPushButton("🗑️ Hapus Buku")
        self.delete_book_btn.setObjectName("btn_delete") # Target QSS styling khusus
        
        btn_layout.addWidget(self.add_book_btn)
        btn_layout.addWidget(self.update_book_btn)
        btn_layout.addWidget(self.delete_book_btn)

        self.book_model = QSqlTableModel()
        self.book_model.setTable("books")
        self.book_model.select()

        self.book_table = QTableView()
        self.book_table.setModel(self.book_model)
        self.book_table.setSelectionBehavior(QTableView.SelectRows)
        self.book_table.setAlternatingRowColors(True)
        self.book_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        books_layout.addLayout(form_layout)
        books_layout.addLayout(btn_layout)
        books_layout.addWidget(self.book_table)
        tabs.addTab(books_tab, "📚 Kelola Buku")

        # ================= TAB 2: PINJAM BUKU =================
        borrow_tab = QWidget()
        borrow_layout = QVBoxLayout(borrow_tab)
        borrow_layout.setContentsMargins(30, 30, 30, 30)
        borrow_layout.setSpacing(15)

        borrow_layout.addWidget(QLabel("<b>Pilih Buku yang Tersedia:</b>"))
        self.book_combo = QComboBox()
        self.load_books_to_combo()
        borrow_layout.addWidget(self.book_combo)

        borrow_layout.addWidget(QLabel("<b>Nama Peminjam:</b>"))
        self.borrower_input = QLineEdit()
        self.borrower_input.setPlaceholderText("Nama lengkap peminjam...")
        borrow_layout.addWidget(self.borrower_input)

        self.borrow_btn = QPushButton("📥 Proses Peminjaman Buku")
        self.borrow_btn.clicked.connect(self.borrow_book)
        borrow_layout.addWidget(self.borrow_btn)
        borrow_layout.addStretch()
        tabs.addTab(borrow_tab, "📖 Pinjam Buku")

        # ================= TAB 3: KEMBALIKAN BUKU =================
        return_tab = QWidget()
        return_layout = QVBoxLayout(return_tab)
        return_layout.setContentsMargins(20, 20, 20, 20)
        return_layout.setSpacing(15)

        self.loan_model = QSqlTableModel()
        self.loan_model.setTable("loans")
        self.loan_model.setFilter("status='active'")
        self.loan_model.select()

        self.loan_table = QTableView()
        self.loan_table.setModel(self.loan_model)
        self.loan_table.setSelectionBehavior(QTableView.SelectRows)
        self.loan_table.setAlternatingRowColors(True)
        self.loan_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.return_btn = QPushButton("📤 Kembalikan Buku Terpilih")
        self.return_btn.clicked.connect(self.return_book)

        return_layout.addWidget(QLabel("<b>Daftar Peminjaman Aktif:</b>"))
        return_layout.addWidget(self.loan_table)
        return_layout.addWidget(self.return_btn)
        tabs.addTab(return_tab, "🔄 Pengembalian")

        # ================= TAB 4: LAPORAN =================
        reports_tab = QWidget()
        reports_layout = QVBoxLayout(reports_tab)
        reports_layout.setContentsMargins(30, 30, 30, 30)
        reports_layout.setSpacing(15)

        self.stats_label = QLabel()
        self.stats_label.setAlignment(Qt.AlignTop)
        self.refresh_btn = QPushButton("🔄 Refresh Laporan")
        self.refresh_btn.clicked.connect(self.refresh_stats)

        reports_layout.addWidget(self.stats_label)
        reports_layout.addWidget(self.refresh_btn)
        reports_layout.addStretch()
        tabs.addTab(reports_tab, "📊 Laporan")

        # Signal connections
        self.add_book_btn.clicked.connect(self.add_book)
        self.update_book_btn.clicked.connect(self.update_book)
        self.delete_book_btn.clicked.connect(self.delete_book)
        self.book_table.clicked.connect(self.on_book_select)
        
        self.refresh_stats()

    def load_books_to_combo(self):
        self.book_combo.clear()
        query = self.db.exec("SELECT id, title FROM books WHERE stock > 0")
        while query.next():
            self.book_combo.addItem(f"{query.value(1)}", query.value(0))

    def add_book(self):
        if self.title_input.text():
            self.db.exec(f"""
                INSERT INTO books (title, author, stock)
                VALUES ('{self.title_input.text()}', '{self.author_input.text()}', {self.stock_input.value()})
            """)
            self.book_model.select()
            self.load_books_to_combo()
            self.clear_book_form()

    def update_book(self):
        current = self.book_table.currentIndex()
        if current.isValid():
            row = current.row()
            book_id = self.book_model.data(self.book_model.index(row, 0))
            self.db.exec(f"""
                UPDATE books
                SET title='{self.title_input.text()}',
                    author='{self.author_input.text()}',
                    stock={self.stock_input.value()}
                WHERE id={book_id}
            """)
            self.book_model.select()
            self.load_books_to_combo()

    def delete_book(self):
        current = self.book_table.currentIndex()
        if current.isValid():
            reply = QMessageBox.question(
                self, "Konfirmasi", "Apakah Anda yakin ingin menghapus buku ini?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                row = current.row()
                book_id = self.book_model.data(self.book_model.index(row, 0))
                self.db.exec(f"DELETE FROM books WHERE id={book_id}")
                self.book_model.select()
                self.load_books_to_combo()

    def on_book_select(self, index):
        row = index.row()
        self.title_input.setText(str(self.book_model.data(self.book_model.index(row, 1))))
        self.author_input.setText(str(self.book_model.data(self.book_model.index(row, 2))))
        self.stock_input.setValue(int(self.book_model.data(self.book_model.index(row, 3))))

    def clear_book_form(self):
        self.title_input.clear()
        self.author_input.clear()
        self.stock_input.setValue(1)

    def borrow_book(self):
        book_id = self.book_combo.currentData()
        borrower = self.borrower_input.text()
        if borrower and book_id:
            today = QDate.currentDate().toString("yyyy-MM-dd")
            self.db.exec(f"""
                INSERT INTO loans (book_id, borrower, loan_date, status)
                VALUES ({book_id}, '{borrower}', '{today}', 'active')
            """)
            self.db.exec(f"UPDATE books SET stock = stock - 1 WHERE id={book_id}")
            self.book_model.select()
            self.loan_model.select()
            self.load_books_to_combo()
            self.borrower_input.clear()
            self.refresh_stats()
            QMessageBox.information(self, "Sukses", f"Buku berhasil dipinjam oleh {borrower}!")

    def return_book(self):
        current = self.loan_table.currentIndex()
        if current.isValid():
            row = current.row()
            loan_id = self.loan_model.data(self.loan_model.index(row, 0))
            book_id = self.loan_model.data(self.loan_model.index(row, 1))
            today = QDate.currentDate().toString("yyyy-MM-dd")
            self.db.exec(f"""
                UPDATE loans
                SET return_date='{today}', status='returned'
                WHERE id={loan_id}
            """)
            self.db.exec(f"UPDATE books SET stock = stock + 1 WHERE id={book_id}")
            self.book_model.select()
            self.loan_model.select()
            self.load_books_to_combo()
            self.refresh_stats()
            QMessageBox.information(self, "Sukses", "Buku telah berhasil dikembalikan!")

    def refresh_stats(self):
        query = self.db.exec("SELECT COUNT(*) FROM books")
        total_books = query.value(0) if query.next() else 0

        query = self.db.exec("SELECT COUNT(*) FROM loans WHERE status='active'")
        active_loans = query.value(0) if query.next() else 0

        self.stats_label.setText(f"""
            <div style='background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #d1d8db;'>
                <h2>📊 Laporan Ringkasan Perpustakaan</h2>
                <hr style='border: 0; border-top: 1px solid #d1d8db;'>
                <p style='font-size: 14px;'><b>Total Jenis Buku:</b> {total_books}</p>
                <p style='font-size: 14px;'><b>Buku Sedang Dipinjam:</b> {active_loans}</p>
                <p style='font-size: 14px;'><b>Total Buku Tersedia:</b> {total_books - active_loans}</p>
            </div>
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LibrarySystem()
    window.show()
    sys.exit(app.exec_())