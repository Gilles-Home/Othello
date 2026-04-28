from PySide6.QtWidgets import QMessageBox, QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
from PySide6.QtCore import Qt, QRectF, QTimer
from ai import OthelloAI


class BoardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.rows = 8
        self.cols = 8

        self.board_state = [[0]*8 for _ in range(8)]
        self.player_color = 2
        self.ai_color = 1
        self.current_turn = "none"
        self.difficulty = 1

        self.ai = OthelloAI()

        self.reset_board(True, 1)

    # -----------------------------------------------------
    # RESET
    # -----------------------------------------------------
    def reset_board(self, player_starts, difficulty):
        self.board_state = [[0]*8 for _ in range(8)]

        self.board_state[3][3] = 2
        self.board_state[4][4] = 2
        self.board_state[3][4] = 1
        self.board_state[4][3] = 1

        self.difficulty = difficulty

        if player_starts:
            self.player_color = 2
            self.ai_color = 1
            self.current_turn = "player"
        else:
            self.player_color = 1
            self.ai_color = 2
            self.current_turn = "ai"
            QTimer.singleShot(300, self.play_ai_move)

        self.update()
        self.update_score_label()

    # -----------------------------------------------------
    # SCORE
    # -----------------------------------------------------
    def count_pieces(self):
        black = sum(1 for r in range(8) for c in range(8) if self.board_state[r][c] == 1)
        white = sum(1 for r in range(8) for c in range(8) if self.board_state[r][c] == 2)
        return black, white

    def update_score_label(self):
        main = self.window()
        if hasattr(main, "update_score"):
            main.update_score(*self.count_pieces())

    # -----------------------------------------------------
    # RÈGLES
    # -----------------------------------------------------
    def get_flips(self, row, col, color):
        if self.board_state[row][col] != 0:
            return []

        opponent = 1 if color == 2 else 2
        flips = []

        directions = [
            (-1,-1),(-1,0),(-1,1),
            (0,-1),       (0,1),
            (1,-1),(1,0),(1,1)
        ]

        for dr, dc in directions:
            r, c = row+dr, col+dc
            line = []

            while 0 <= r < 8 and 0 <= c < 8 and self.board_state[r][c] == opponent:
                line.append((r,c))
                r += dr
                c += dc

            if 0 <= r < 8 and 0 <= c < 8 and self.board_state[r][c] == color and line:
                flips.extend(line)

        return flips

    def play_move(self, row, col, color):
        flips = self.get_flips(row, col, color)
        if not flips:
            return False

        self.board_state[row][col] = color
        for r, c in flips:
            self.board_state[r][c] = color

        return True

    def has_legal_move(self, color):
        for r in range(8):
            for c in range(8):
                if self.get_flips(r, c, color):
                    return True
        return False

    # -----------------------------------------------------
    # FIN DE PARTIE
    # -----------------------------------------------------
    def check_end_of_game(self):
        full = all(self.board_state[r][c] != 0 for r in range(8) for c in range(8))
        no_moves = (not self.has_legal_move(1)) and (not self.has_legal_move(2))

        if not full and not no_moves:
            return False

        black, white = self.count_pieces()

        if black > white:
            winner = "Noir"
        elif white > black:
            winner = "Blanc"
        else:
            winner = "Égalité"

        QMessageBox.information(
            self, "Fin de partie",
            f"Noirs : {black}\nBlancs : {white}\n\nVainqueur : {winner}"
        )

        self.current_turn = "none"
        return True

    # -----------------------------------------------------
    # CLIC JOUEUR
    # -----------------------------------------------------
    def mousePressEvent(self, event):
        if self.current_turn != "player":
            return

        x = event.position().x()
        y = event.position().y()

        size = min(self.width(), self.height()) * 0.80
        bx = (self.width() - size) / 2
        by = (self.height() - size) / 2
        m1 = size * 0.04
        m2 = size * 0.02

        gx = bx + m1 + m2
        gy = by + m1 + m2
        gsize = size - 2*(m1+m2)

        cw = gsize / 8
        ch = gsize / 8

        if not (gx <= x <= gx+gsize and gy <= y <= gy+gsize):
            return

        col = int((x - gx) / cw)
        row = int((y - gy) / ch)

        if not self.play_move(row, col, self.player_color):
            QMessageBox.warning(self, "Coup invalide", "Ce coup ne retourne aucun pion!")
            return

        self.update()
        self.update_score_label()

        if self.check_end_of_game():
            return

        if not self.has_legal_move(self.ai_color):
            if not self.has_legal_move(self.player_color):
                self.check_end_of_game()
                return
            QMessageBox.information(self, "Tour passé", "L'ordinateur ne peut pas jouer.")
            return

        self.current_turn = "ai"
        QTimer.singleShot(300, self.play_ai_move)

    # -----------------------------------------------------
    # IA MINIMAX
    # -----------------------------------------------------
    def play_ai_move(self):
        if not self.has_legal_move(self.ai_color):
            if not self.has_legal_move(self.player_color):
                self.check_end_of_game()
                return
            QMessageBox.information(self, "Tour passé", "L'ordinateur ne peut pas jouer.")
            self.current_turn = "player"
            return

        depth = {1:1, 2:3, 3:5}[self.difficulty]

        _, move = self.ai.minimax(
            [row[:] for row in self.board_state],
            depth,
            True,
            -999999,
            999999,
            self.ai_color,
            self.ai_color
        )

        if move is None:
            QMessageBox.information(self, "Tour passé", "L'ordinateur ne peut pas jouer.")
            self.current_turn = "player"
            return

        r, c = move
        self.play_move(r, c, self.ai_color)
        self.update()
        self.update_score_label()

        if self.check_end_of_game():
            return

        if not self.has_legal_move(self.player_color):
            QMessageBox.information(self, "Tour passé", "Vous ne pouvez pas jouer.")
            QTimer.singleShot(300, self.play_ai_move)
            return

        self.current_turn = "player"

    # -----------------------------------------------------
    # DESSIN
    # -----------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)

        painter.fillRect(self.rect(), QColor(230,220,200))

        size = min(self.width(), self.height()) * 0.80
        bx = (self.width() - size) / 2
        by = (self.height() - size) / 2

        painter.fillRect(QRectF(bx,by,size,size), QColor(90,50,20))

        m1 = size * 0.04
        inner = QRectF(bx+m1, by+m1, size-2*m1, size-2*m1)
        painter.fillRect(inner, QColor(0,0,0))

        m2 = size * 0.02
        grid = QRectF(inner.x()+m2, inner.y()+m2, inner.width()-2*m2, inner.height()-2*m2)
        painter.fillRect(grid, QColor(0,110,0))

        cw = grid.width()/8
        ch = grid.height()/8

        pen = QPen(Qt.black,2)
        painter.setPen(pen)

        for c in range(9):
            painter.drawLine(grid.x()+c*cw, grid.y(), grid.x()+c*cw, grid.y()+grid.height())
        for r in range(9):
            painter.drawLine(grid.x(), grid.y()+r*ch, grid.x()+grid.width(), grid.y()+r*ch)

        for r in range(8):
            for c in range(8):
                if self.board_state[r][c] == 0:
                    continue

                cx = grid.x() + c*cw + cw/2
                cy = grid.y() + r*ch + ch/2
                radius = min(cw,ch)*0.35

                color = Qt.black if self.board_state[r][c] == 1 else Qt.white
                painter.setBrush(QBrush(color))
                painter.drawEllipse(QRectF(cx-radius, cy-radius, radius*2, radius*2))

