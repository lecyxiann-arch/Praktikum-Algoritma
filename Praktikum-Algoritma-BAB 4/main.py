
import sys
from pathlib import Path

from PyQt5 import QtWidgets, uic
import db_helper
from kelola_buku import KelolaBukuWindow
from pinjam_buku import PinjamBukuWindow


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        base_dir = Path(__file__).resolve().parent

        # Memuat tampilan dari Qt Designer
        uic.loadUi(str(base_dir / "main.ui"), self)

        # Inisialisasi database
        db_helper.init_db()

        self.kelola_buku_win = None
        self.pinjam_buku_win = None

        # Menghubungkan tombol
        self.btnKelolaBuku.clicked.connect(self.open_kelola_buku)
        self.btnPinjamBuku.clicked.connect(self.open_pinjam_buku)
        self.btnPengembalian.clicked.connect(
            self.show_pengembalian_notice
        )
        self.btnLaporan.clicked.connect(self.show_laporan_notice)
        self.btnKeluar.clicked.connect(self.close)

    def open_kelola_buku(self):
        if self.kelola_buku_win is None:
            self.kelola_buku_win = KelolaBukuWindow()

        self.kelola_buku_win.load_books()
        self.kelola_buku_win.show()
        self.kelola_buku_win.raise_()
        self.kelola_buku_win.activateWindow()

    def open_pinjam_buku(self):
        if self.pinjam_buku_win is None:
            self.pinjam_buku_win = PinjamBukuWindow()

        self.pinjam_buku_win.load_books_combo()
        self.pinjam_buku_win.load_active_loans()
        self.pinjam_buku_win.show()
        self.pinjam_buku_win.raise_()
        self.pinjam_buku_win.activateWindow()

    def show_pengembalian_notice(self):
        QtWidgets.QMessageBox.information(
            self,
            "Pengembalian Buku",
            "Fungsi pengembalian belum memiliki file tampilan."
        )

    def show_laporan_notice(self):
        QtWidgets.QMessageBox.information(
            self,
            "Laporan Statistik",
            "Form laporan belum disertakan."
        )


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
