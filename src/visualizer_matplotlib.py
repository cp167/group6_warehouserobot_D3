import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation

C_OBSTACLE = "#2c3e50"
C_EMPTY = "#ecf0f1"
C_DEPOT = "#e74c3c"
C_ITEM = "#2ecc71"
C_PATH = "#f39c12"
C_GRIDLINE = "#bdc3c7"


def _draw_grid(ax, env, title="Warehouse Grid"):
    N = env.N
    ax.set_xlim(-0.5, N - 0.5)
    ax.set_ylim(-0.5, N - 0.5)
    ax.set_aspect('equal')
    ax.invert_yaxis()
    ax.set_title(title, fontsize=12, fontweight='bold')

    for r in range(N):
        for c in range(N):
            if (r, c) in env.obstacles: color = C_OBSTACLE
            elif (r, c) == env.depot: color = C_DEPOT
            else: color = C_EMPTY
            rect = patches.Rectangle((c - 0.5, r - 0.5), 1, 1,
                                     linewidth=0.5, edgecolor=C_GRIDLINE, facecolor=color)
            ax.add_patch(rect)

    dr, dc = env.depot
    ax.text(dc, dr, "D", ha='center', va='center', fontsize=8, fontweight='bold', color='white')

    for iid, info in env.items_info.items():
        ir, ic = info["location"]
        ax.add_patch(plt.Circle((ic, ir), 0.3, color=C_ITEM, zorder=5))
        ax.text(ic, ir, str(iid), ha='center', va='center',
                fontsize=7, fontweight='bold', color='white', zorder=6)

    ax.set_xticks(range(N))
    ax.set_yticks(range(N))
    ax.tick_params(labelsize=6)


def visualize_solution(env, result, save_path=None):
    if result["solution"] is None:
        print(f"[{result['algorithm']}] No solution.")
        return

    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    _draw_grid(ax, env, title=f"Solution: {result['algorithm']}")

    positions = [env.start]
    for action, state in result["solution"]:
        positions.append(state.p)

    if len(positions) > 1:
        ax.plot([p[1] for p in positions], [p[0] for p in positions],
                color=C_PATH, linewidth=1.5, alpha=0.7, zorder=3)

    txt = (f"Algorithm: {result['algorithm']}\nCost: {result['cost']}\n"
           f"Expanded: {result['nodes_expanded']}\nTime: {result['time']:.4f}s")
    ax.text(0.02, 0.02, txt, transform=ax.transAxes, fontsize=8,
            verticalalignment='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    else:
        plt.show()
    plt.close()


def compare_algorithms_chart(results_list, save_path=None):
    valid = [r for r in results_list if r["solution"] is not None]
    if not valid:
        print("Nothing to compare.")
        return

    names = [r["algorithm"] for r in valid]
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for ax, data, label, fmt in [
        (axes[0], [r["nodes_expanded"] for r in valid], "Nodes Expanded", "d"),
        (axes[1], [r["time"] for r in valid], "Time (seconds)", ".3f"),
        (axes[2], [r["cost"] for r in valid], "Solution Cost", "d"),
    ]:
        bars = ax.bar(names, data, color=colors[:len(names)])
        ax.set_title(label, fontweight='bold')
        for bar, val in zip(bars, data):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                    f"{val:{fmt}}", ha='center', va='bottom', fontsize=8)
        ax.tick_params(axis='x', rotation=30, labelsize=8)

    plt.suptitle("Algorithm Comparison", fontsize=14, fontweight='bold')
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    else:
        plt.show()
    plt.close()


def animate_solution(env, result, save_path=None, interval=200):
    if result["solution"] is None:
        print(f"[{result['algorithm']}] No solution — nothing to animate.")
        return

    fig, ax = plt.subplots(1, 1, figsize=(8, 8))

    path = result["solution"]
    frames = [(state, action, i) for i, (action, state) in enumerate(path)]

    delivered_so_far = set()
    carrying = [0]
    robot_dot = None
    status_text = None
    energy_text = None

    def init():
        nonlocal robot_dot, status_text, energy_text
        ax.clear()
        _draw_grid(ax, env, title=f"Animation: {result['algorithm']}")

        rx, ry = env.start
        robot_dot = plt.Circle((ry, rx), 0.35, color='#3498db', zorder=10)
        ax.add_patch(robot_dot)

        status_text = ax.text(
            0.02, 0.98, "", transform=ax.transAxes,
            fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))
        energy_text = ax.text(
            0.98, 0.98, "", transform=ax.transAxes,
            fontsize=9, verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.9))
        return robot_dot, status_text, energy_text

    def update(frame_idx):
        nonlocal robot_dot
        if frame_idx >= len(frames):
            return robot_dot, status_text, energy_text

        state, action, step = frames[frame_idx]
        rx, ry = state.p
        robot_dot.center = (ry, rx)

        if action == "Drop":
            delivered_so_far.add(carrying[0])
            carrying[0] = 0
        elif action.startswith("Pick"):
            item_id = int(action.split("(")[1].rstrip(")"))
            carrying[0] = item_id

        robot_dot.set_color('#9b59b6' if carrying[0] else '#3498db')

        for iid in delivered_so_far:
            loc = env.item_locations[iid]
            circle = plt.Circle((loc[1], loc[0]), 0.3, color='#95a5a6', zorder=5)
            ax.add_patch(circle)

        carry_str = f"Item {carrying[0]}" if carrying[0] != 0 else "Nothing"
        status_text.set_text(
            f"Step {step + 1}/{len(frames)}\n"
            f"Action: {action}\n"
            f"Carrying: {carry_str}\n"
            f"Delivered: {len(delivered_so_far)}/{len(env.items_info)}")
        energy_text.set_text(f"Energy: {state.E}/{env.energy}")

        return robot_dot, status_text, energy_text

    anim = animation.FuncAnimation(
        fig, update, init_func=init,
        frames=len(frames), interval=interval,
        blit=False, repeat=False)

    if save_path:
        if save_path.endswith('.mp4'):
            writer = animation.FFMpegWriter(fps=1000 // interval)
            anim.save(save_path, writer=writer, dpi=150)
        elif save_path.endswith('.gif'):
            anim.save(save_path, writer='pillow', dpi=100)
        print(f"Animation saved: {save_path}")
    else:
        plt.show()
    plt.close()
