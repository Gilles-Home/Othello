from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QLabel, QInputDialog, QMessageBox
)
from board import BoardWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Othello")

        central = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)

        self.start_button = QPushButton("Nouvelle partie")
        self.start_button.setStyleSheet("font-size: 24px; padding: 15px;")
        self.start_button.clicked.connect(self.start_game)
        layout.addWidget(self.start_button)

        self.board = BoardWidget()
        self.board.setVisible(False)
        layout.addWidget(self.board)

        self.score_label = QLabel("Noirs : 2    Blancs : 2")
        self.score_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.score_label)

        central.setLayout(layout)
        self.setCentralWidget(central)

        # Menu
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        new_game_action = file_menu.addAction("Nouvelle partie")
        new_game_action.triggered.connect(self.start_game)

        quit_action = file_menu.addAction("Quit")
        quit_action.triggered.connect(self.close)

        help_menu = menu_bar.addMenu("Aide")
        about_action = help_menu.addAction("À propos")
        about_action.triggered.connect(self.show_about)

    def start_game(self):
        starter, ok = QInputDialog.getItem(
            self, "Qui commence ?", "Choisissez :", ["Joueur", "Ordinateur"], 0, False
        )
        if not ok:
            return

        difficulty, ok = QInputDialog.getInt(
            self, "Difficulté", "Choisissez (1 à 3) :", 1, 1, 3
        )
        if not ok:
            return

        player_starts = (starter == "Joueur")
        self.board.reset_board(player_starts, difficulty)

        self.start_button.setVisible(False)
        self.board.setVisible(True)

        QMessageBox.information(
            self, "Nouvelle partie",
            f"Premier joueur : {starter}\nDifficulté : {difficulty}"
        )

    def update_score(self, black, white):
        self.score_label.setText(f"Noirs : {black}    Blancs : {white}")

    def show_about(self):
        QMessageBox.information(self, "À propos", "Othello\nProjet Nostalgie 1989")

