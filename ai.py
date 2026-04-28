class OthelloAI:

    def count_pieces_board(self, board):
        black = sum(1 for r in range(8) for c in range(8) if board[r][c] == 1)
        white = sum(1 for r in range(8) for c in range(8) if board[r][c] == 2)
        return black, white

    def evaluate_board(self, board, ai_color):
        black, white = self.count_pieces_board(board)
        return (black - white) if ai_color == 1 else (white - black)

    def get_flips_sim(self, board, row, col, color):
        if board[row][col] != 0:
            return []

        opponent = 1 if color == 2 else 2
        flips = []

        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),          (0, 1),
            (1, -1),  (1, 0), (1, 1)
        ]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            line = []

            while 0 <= r < 8 and 0 <= c < 8 and board[r][c] == opponent:
                line.append((r, c))
                r += dr
                c += dc

            if 0 <= r < 8 and 0 <= c < 8 and board[r][c] == color and line:
                flips.extend(line)

        return flips

    def simulate_move(self, board, row, col, color):
        new_board = [r[:] for r in board]
        flips = self.get_flips_sim(new_board, row, col, color)
        if not flips:
            return new_board

        new_board[row][col] = color
        for r, c in flips:
            new_board[r][c] = color

        return new_board

    def minimax(self, board, depth, maximizing, alpha, beta, color, ai_color):
        if depth == 0:
            return self.evaluate_board(board, ai_color), None

        legal_moves = [
            (r, c)
            for r in range(8)
            for c in range(8)
            if self.get_flips_sim(board, r, c, color)
        ]

        if not legal_moves:
            return self.evaluate_board(board, ai_color), None

        best_move = None
        next_color = 1 if color == 2 else 2

        if maximizing:
            max_eval = -999999
            for move in legal_moves:
                new_board = self.simulate_move(board, move[0], move[1], color)
                eval_score, _ = self.minimax(
                    new_board, depth - 1, False, alpha, beta, next_color, ai_color
                )
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move

        else:
            min_eval = 999999
            for move in legal_moves:
                new_board = self.simulate_move(board, move[0], move[1], color)
                eval_score, _ = self.minimax(
                    new_board, depth - 1, True, alpha, beta, next_color, ai_color
                )
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move

