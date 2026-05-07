import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# =========================
# Parameters
# =========================

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

FIELD_SIZE = 512
PANELS = 6
THRESHOLD = 0.5
INTERVAL_MS = 150

np.random.seed(42)

# Constant difference field
D = np.random.random((FIELD_SIZE, FIELD_SIZE))


# =========================
# Core Functions
# =========================

def compress_2x2(field: np.ndarray, threshold: float) -> np.ndarray:
    h, w = field.shape

    h_even = h - h % 2
    w_even = w - w % 2

    field = field[:h_even, :w_even]

    blocks = field.reshape(h_even // 2, 2, w_even // 2, 2)
    averages = blocks.mean(axis=(1, 3))

    return (averages > threshold).astype(float)


def build_interpretation_levels(
    D: np.ndarray,
    frame: int,
    levels: int,
    threshold: float
) -> list[np.ndarray]:
    """
    Returns six consecutive levels of interpretation.

    Level 0: direct black/white interpretation of D
    Level 1: 2x2 compression
    Level 2: compression of Level 1
    ...
    """

    offset_x = frame % 2
    offset_y = (frame // 2) % 2

    local_threshold = threshold + 0.04 * np.sin(frame * 0.15)

    base = D[offset_x:, offset_y:]
    current = (base > local_threshold).astype(float)

    result = [current]

    for _ in range(1, levels):
        current = compress_2x2(current, threshold=0.5)
        result.append(current)

    return result


# =========================
# Visualization: 1920x1080
# =========================

dpi = 100
fig_width = SCREEN_WIDTH / dpi
fig_height = SCREEN_HEIGHT / dpi

fig, axes = plt.subplots(
    2,
    3,
    figsize=(fig_width, fig_height),
    dpi=dpi
)

fig.canvas.manager.set_window_title("Invariant Life: 6 levels of interpretation")

axes = axes.flatten()

levels = build_interpretation_levels(
    D=D,
    frame=0,
    levels=PANELS,
    threshold=THRESHOLD
)

images = []

for i, ax in enumerate(axes):
    img = ax.imshow(
        levels[i],
        cmap="gray",
        vmin=0,
        vmax=1,
        interpolation="nearest"
    )

    ax.set_title(f"Level {i}: compression {i}", fontsize=14)
    ax.axis("off")
    images.append(img)

plt.subplots_adjust(
    left=0.01,
    right=0.99,
    top=0.94,
    bottom=0.02,
    wspace=0.03,
    hspace=0.10
)


def animate(frame: int):
    levels = build_interpretation_levels(
        D=D,
        frame=frame,
        levels=PANELS,
        threshold=THRESHOLD
    )

    for i, img in enumerate(images):
        img.set_data(levels[i])
        axes[i].set_title(
            f"Level {i}: {levels[i].shape[1]}×{levels[i].shape[0]} | frame={frame}",
            fontsize=14
        )

    fig.suptitle(
        "Invariant Life: constant Difference Field D, changing interpretation",
        fontsize=18
    )

    return images


animation = FuncAnimation(
    fig,
    animate,
    frames=1000,
    interval=INTERVAL_MS,
    blit=False
)

plt.show()