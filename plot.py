from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import os


# Sample data (replace this with your actual data)
def plot(data, filename):
    classnames = [
        "BP",
        "coop",
        "objective-text",
        "pen",
        "quests",
        "skill-icons",
        "skill-icons-controller",
        "skill-icons-mobile",
        "spiral-abyss",
        "tutorial",
        "wish",
    ]

    # Filter out elements other than "plot me" and store their positions
    BPindices = [i for i, val in enumerate(data) if "BP-screen" in val]
    COOPindices = [i for i, val in enumerate(data) if "coop-screen" in val]
    OBJECTIVE_TEXTindices = [i for i, val in enumerate(data) if "objective-text" in val]
    PENindices = [i for i, val in enumerate(data) if "book-screen" in val]
    QUESTSindices = [i for i, val in enumerate(data) if "mission-screen" in val]
    SKILL_ICONSindices = [i for i, val in enumerate(data) if "skill-icons" in val]
    SKILL_ICONS_CONTROLLERindices = [
        i for i, val in enumerate(data) if "skill-icons-controller" in val
    ]
    SKILL_ICONS_MOBILEindices = [
        i for i, val in enumerate(data) if "skill-icons-mobile" in val
    ]
    SPIRAL_ABYSSindices = [i for i, val in enumerate(data) if "spiral-abyss" in val]
    TUTORIALindices = [i for i, val in enumerate(data) if "tutorial-screen" in val]
    WISHindices = [i for i, val in enumerate(data) if "wish-screen" in val]
    DIRTY_FRAMEindices = [i for i, val in enumerate(data) if "Dirty Frame" in val]
    TRANSITIONindices = [i for i, val in enumerate(data) if "transition-screen" in val]
    TRANSITION2indices = [
        i for i, val in enumerate(data) if "transition-screen-2" in val
    ]

    ax: Axes
    fig, ax = plt.subplots(figsize=(30, 6))
    fig.patch.set_facecolor("black")  # Set figure background color to black
    ax.set_facecolor("black")

    threshold = 0
    if len(SKILL_ICONSindices) > 0:
        ax.text(
            -5,
            (0.1 + 0.2) / 2,
            "SKILL ICONS",
            horizontalalignment="right",
            verticalalignment="center",
            rotation="horizontal",
            color="white",
        )
        for i, idx in enumerate(SKILL_ICONSindices):
            ax.axvspan(idx, idx + 1, color="#00ffce", alpha=0.5, ymin=0.1, ymax=0.2)
    elif len(SKILL_ICONS_CONTROLLERindices) > 0:
        ax.text(
            -5,
            (0.1 + 0.2) / 2,
            "SKILL ICONS CONTROLLER",
            horizontalalignment="right",
            verticalalignment="center",
            rotation="horizontal",
            color="white",
        )
        for i, idx in enumerate(SKILL_ICONS_CONTROLLERindices):
            ax.axvspan(idx, idx + 1, color="#00b7eb", alpha=0.5, ymin=0.1, ymax=0.2)
    elif len(SKILL_ICONS_MOBILEindices) > 0:
        ax.text(
            -5,
            (0.1 + 0.2) / 2,
            "SKILL ICONS MOBILE",
            horizontalalignment="right",
            verticalalignment="center",
            rotation="horizontal",
            color="white",
        )
        for i, idx in enumerate(SKILL_ICONS_MOBILEindices):
            ax.axvspan(idx, idx + 1, color="#ff8000", alpha=0.5, ymin=0.1, ymax=0.2)

    ax.text(
        -5,
        (0.2 + 0.3) / 2,
        "OBJECTIVE TEXT",
        horizontalalignment="right",
        verticalalignment="center",
        rotation="horizontal",
        color="white",
    )
    for i, idx in enumerate(OBJECTIVE_TEXTindices):
        ax.axvspan(idx, idx + 1, color="#ffff00", alpha=0.5, ymin=0.2, ymax=0.3)

    for i, idx in enumerate(BPindices):
        ax.axvspan(idx, idx + 1, color="#ffabab", alpha=1, ymin=0.3, ymax=0.4)
    for i, idx in enumerate(COOPindices):
        ax.axvspan(idx, idx + 1, color="#CC6B1C", alpha=1, ymin=0.3, ymax=0.4)
    for i, idx in enumerate(PENindices):
        ax.axvspan(idx, idx + 1, color="#8622ff", alpha=1, ymin=0.3, ymax=0.4)
    for i, idx in enumerate(QUESTSindices):
        ax.axvspan(idx, idx + 1, color="#0e7afe", alpha=1, ymin=0.3, ymax=0.4)
    for i, idx in enumerate(SPIRAL_ABYSSindices):
        ax.axvspan(idx, idx + 1, color="#fe0056", alpha=1, ymin=0.3, ymax=0.4)
    for i, idx in enumerate(TUTORIALindices):
        ax.axvspan(idx, idx + 1, color="#0000ff", alpha=1, ymin=0.3, ymax=0.4)
    for i, idx in enumerate(WISHindices):
        ax.axvspan(idx, idx + 1, color="#ff00ff", alpha=1, ymin=0.3, ymax=0.4)

    for i, idx in enumerate(TRANSITIONindices):
        ax.axvspan(idx, idx + 1, color="#FFFFFF", alpha=1, ymin=0.1, ymax=0.3)
    for i, idx in enumerate(TRANSITION2indices):
        ax.axvspan(idx, idx + 1, color="#8D8C8C", alpha=1, ymin=0.1, ymax=0.3)
    ax.text(
        -5,
        (0.4 + 0.3) / 2,
        "PAUSES",
        horizontalalignment="right",
        verticalalignment="center",
        rotation="horizontal",
        color="white",
    )

    for i, idx in enumerate(DIRTY_FRAMEindices):
        ax.axvspan(idx, idx + 1, color="#287E05", alpha=1, ymin=0.4, ymax=0.5)
    ax.text(
        -5,
        (0.4 + 0.5) / 2,
        "DIRTY FRAME",
        horizontalalignment="right",
        verticalalignment="center",
        rotation="horizontal",
        color="white",
    )

    # Set limits and labels
    ax.set_xlim(0, len(data))
    ax.set_ylim(0, 1)
    ax.set_xlabel("Timeline (frame)", color="white")
    ax.set_title("Object Occurrences", color="white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.tick_params(axis="x", colors="white")
    ax.tick_params(axis="y", colors="white")
    ax.spines["bottom"].set_color("white")
    ax.spines["top"].set_color("white")
    ax.spines["right"].set_color("white")
    ax.spines["left"].set_color("white")
    legend_handles = [
        plt.Rectangle((0, 0), 1, 1, color="#ffabab", alpha=1),
        plt.Rectangle((0, 0), 1, 1, color="#CC6B1C", alpha=1),
        plt.Rectangle((0, 0), 1, 1, color="#8622ff", alpha=1),
        plt.Rectangle((0, 0), 1, 1, color="#0e7afe", alpha=1),
        plt.Rectangle((0, 0), 1, 1, color="#fe0056", alpha=1),
        plt.Rectangle((0, 0), 1, 1, color="#0000ff", alpha=1),
        plt.Rectangle((0, 0), 1, 1, color="#ff00ff", alpha=1),
        plt.Rectangle((0, 0), 1, 1, color="#287E05", alpha=1),
    ]
    legend_labels = [
        "BP",
        "COOP",
        "BOOK",
        "QUESTS",
        "SPIRAL ABYSS",
        "TUTORIAL",
        "WISH",
        "DIRTY FRAME",
    ]
    ax.legend(legend_handles, legend_labels, title="Pauses screens", loc="upper right")

    plt.grid(False)
    plt.yticks([])  # Hide y-axis ticks
    if not os.path.exists("plots"):
        os.makedirs("plots")
    plt.savefig(f"plots/{filename}.png")
