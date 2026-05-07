import sys
import numpy as np

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication, QLabel, QWidget, QPushButton,
    QGridLayout, QVBoxLayout, QHBoxLayout
)

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

LEVELS = 4
THRESHOLD = 0.5

# 2x2 panels
PANEL_COLUMNS = 2
PANEL_ROWS = 2

# approximate visible panel size
PANEL_WIDTH = SCREEN_WIDTH // PANEL_COLUMNS
PANEL_HEIGHT = (SCREEN_HEIGHT - 80) // PANEL_ROWS

# D must be large enough so after compressions levels still match panels
# Level 0: 960x500
# Level 1: 480x250
# Level 2: 240x125
# Level 3: 120x62
BASE_WIDTH = PANEL_WIDTH * (2 ** (LEVELS - 1))
BASE_HEIGHT = PANEL_HEIGHT * (2 ** (LEVELS - 1))

np.random.seed(42)


def compress_2x2(field: np.ndarray, threshold: float = 0.5) -> np.ndarray:
    h, w = field.shape
    h_even = h - h % 2
    w_even = w - w % 2

    field = field[:h_even, :w_even]

    blocks = field.reshape(h_even // 2, 2, w_even // 2, 2)
    averages = blocks.mean(axis=(1, 3))

    return (averages > threshold).astype(np.uint8)


def count_neighbors(grid: np.ndarray) -> np.ndarray:
    return (
        np.roll(np.roll(grid, 1, 0), 1, 1)
        + np.roll(grid, 1, 0)
        + np.roll(np.roll(grid, 1, 0), -1, 1)
        + np.roll(grid, 1, 1)
        + np.roll(grid, -1, 1)
        + np.roll(np.roll(grid, -1, 0), 1, 1)
        + np.roll(grid, -1, 0)
        + np.roll(np.roll(grid, -1, 0), -1, 1)
    )


def interpretation_rule(grid: np.ndarray) -> np.ndarray:
    neighbors = count_neighbors(grid)

    born = (grid == 0) & (neighbors == 3)
    survives = (grid == 1) & ((neighbors == 2) | (neighbors == 3))

    return (born | survives).astype(np.uint8)


def field_to_pixmap(field: np.ndarray, width: int, height: int) -> QPixmap:
    image_data = (field * 255).astype(np.uint8)
    h, w = image_data.shape

    qimage = QImage(
        image_data.data,
        w,
        h,
        w,
        QImage.Format_Grayscale8,
    )

    pixmap = QPixmap.fromImage(qimage.copy())

    return pixmap.scaled(
        width,
        height,
        Qt.KeepAspectRatio,
        Qt.FastTransformation,
    )


class InterpretationPanel(QWidget):
    def __init__(self, level_index: int):
        super().__init__()

        self.level_index = level_index

        self.title = QLabel()
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFixedHeight(24)

        self.image = QLabel()
        self.image.setAlignment(Qt.AlignCenter)
        self.image.setMinimumSize(900, 480)
        self.image.setStyleSheet("background-color: black;")

        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        layout.addWidget(self.title)
        layout.addWidget(self.image, stretch=1)

        self.setLayout(layout)

    def update_view(self, field: np.ndarray, iteration: int):
        self.title.setText(
            f"Level {self.level_index} | "
            f"{field.shape[1]}×{field.shape[0]} | "
            f"iteration {iteration}"
        )

        pixmap = field_to_pixmap(
            field,
            self.image.width(),
            self.image.height(),
        )

        self.image.setPixmap(pixmap)


class InvariantLifeWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Invariant Life — 4 large interpretation fields")
        self.resize(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Constant difference field.
        # Its size is derived from visible panel size.
        self.D = np.random.random((BASE_HEIGHT, BASE_WIDTH))

        self.iteration = 0
        self.levels = self.build_initial_levels()

        self.panels = [InterpretationPanel(i) for i in range(LEVELS)]

        grid = QGridLayout()
        grid.setContentsMargins(2, 2, 2, 2)
        grid.setSpacing(2)

        for i, panel in enumerate(self.panels):
            row = i // 2
            col = i % 2
            grid.addWidget(panel, row, col)

        self.iterate_button = QPushButton("Iterate interpretations")
        self.iterate_button.clicked.connect(self.iterate)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset)

        buttons = QHBoxLayout()
        buttons.setContentsMargins(2, 2, 2, 2)
        buttons.addWidget(self.iterate_button)
        buttons.addWidget(self.reset_button)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        main_layout.addLayout(grid, stretch=1)
        main_layout.addLayout(buttons)

        self.setLayout(main_layout)

        self.refresh_all()

    def build_initial_levels(self) -> list[np.ndarray]:
        current = (self.D > THRESHOLD).astype(np.uint8)

        levels = [current]

        for _ in range(1, LEVELS):
            current = compress_2x2(current, threshold=0.5)
            levels.append(current)

        return levels

    def iterate(self):
        self.levels = [
            interpretation_rule(level)
            for level in self.levels
        ]

        self.iteration += 1
        self.refresh_all()

    def reset(self):
        self.iteration = 0
        self.levels = self.build_initial_levels()
        self.refresh_all()

    def refresh_all(self):
        for panel, field in zip(self.panels, self.levels):
            panel.update_view(field, self.iteration)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.refresh_all()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = InvariantLifeWindow()
    window.showMaximized()

    sys.exit(app.exec())