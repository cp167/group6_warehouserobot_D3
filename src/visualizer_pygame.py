import pygame
import sys
from .config import *

PAD = 15
LINE_H = 22
SECTION_GAP = 15
HEADER_H = 30


class PygameVisualizer:
    def __init__(self, env, search_result=None):
        pygame.init()
        self.env = env
        self.result = search_result

        grid_px = env.N * CELL_SIZE

        sidebar_h = self._estimate_sidebar_height()

        self.width = grid_px + SIDEBAR_WIDTH
        self.height = max(grid_px, sidebar_h + 40, 600)

        screen_h = pygame.display.Info().current_h - 80
        if self.height > screen_h:
            self.height = screen_h

        self.grid_offset_x = 0
        self.grid_offset_y = 0
        self.sidebar_scroll = 0
        self.sidebar_content_h = sidebar_h

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Warehouse Robot — AI Search Visualization")
        self.clock = pygame.time.Clock()

        self.font_sm = pygame.font.SysFont('Arial', 14)
        self.font_md = pygame.font.SysFont('Arial', 18)
        self.font_lg = pygame.font.SysFont('Arial', 24, bold=True)
        self.font_title = pygame.font.SysFont('Arial', 28, bold=True)

        self.expl_idx = 0
        self.sol_step = 0
        self.playing = False
        self.speed = 50
        self.mode = 'exploration'
        self.explored_pos = set()
        self.frontier_pos = set()
        self.sol_path = []

        if search_result and search_result.get("solution"):
            self.sol_path = [s.p for _, s in search_result["solution"]]
            self.sol_path.insert(0, env.start)

    def _estimate_sidebar_height(self):
        h = 40
        h += 10 * LINE_H
        h += 7 * LINE_H
        h += SECTION_GAP + 10 + HEADER_H
        h += 7 * 20
        h += SECTION_GAP + 10 + HEADER_H
        h += 8 * LINE_H
        h += 40
        return h

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    running = self._handle_key(event.key)
                elif event.type == pygame.MOUSEWHEEL:
                    self._scroll(event.y)
            if self.playing:
                self._advance()
            self._draw()
            self.clock.tick(FPS)
        pygame.quit()

    def _handle_key(self, key):
        if key in (pygame.K_ESCAPE, pygame.K_q):
            return False
        elif key == pygame.K_SPACE:
            self.playing = not self.playing
        elif key == pygame.K_RIGHT:
            self._advance()
        elif key == pygame.K_r:
            self.expl_idx = 0
            self.sol_step = 0
            self.explored_pos.clear()
            self.frontier_pos.clear()
            self.mode = 'exploration'
            self.playing = False
        elif key == pygame.K_s:
            self.mode = 'solution'
            self.sol_step = 0
            self.playing = True
        elif key == pygame.K_UP:
            self.speed = min(self.speed * 2, 5000)
        elif key == pygame.K_DOWN:
            self.speed = max(self.speed // 2, 1)
        elif key == pygame.K_f:
            self._fast_forward()
        return True

    def _scroll(self, direction):
        self.sidebar_scroll += direction * 30
        self.sidebar_scroll = min(self.sidebar_scroll, 0)
        max_scroll = -(self.sidebar_content_h - self.height + 40)
        if max_scroll < 0:
            self.sidebar_scroll = max(self.sidebar_scroll, max_scroll)
        else:
            self.sidebar_scroll = 0

    def _fast_forward(self):
        if not self.result or not self.result.get("exploration_order"):
            return
        expl = self.result["exploration_order"]
        for i in range(self.expl_idx, len(expl)):
            state, stype = expl[i]
            if stype == 'expanded':
                self.explored_pos.add(state.p)
                self.frontier_pos.discard(state.p)
            elif stype == 'frontier' and state.p not in self.explored_pos:
                self.frontier_pos.add(state.p)
        self.expl_idx = len(expl)
        self.mode = 'solution'
        self.sol_step = len(self.sol_path) - 1 if self.sol_path else 0
        self.playing = False

    def _advance(self):
        if not self.result:
            return
        if self.mode == 'exploration':
            expl = self.result.get("exploration_order", [])
            for _ in range(self.speed):
                if self.expl_idx < len(expl):
                    state, stype = expl[self.expl_idx]
                    if stype == 'expanded':
                        self.explored_pos.add(state.p)
                        self.frontier_pos.discard(state.p)
                    elif stype == 'frontier' and state.p not in self.explored_pos:
                        self.frontier_pos.add(state.p)
                    self.expl_idx += 1
                else:
                    self.mode = 'solution'
                    self.sol_step = 0
                    break
        elif self.mode == 'solution':
            if self.sol_path and self.sol_step < len(self.sol_path) - 1:
                self.sol_step += 1
            else:
                self.playing = False

    def _draw(self):
        self.screen.fill(WHITE)
        self._draw_grid()
        self._draw_sidebar()
        pygame.display.flip()

    def _draw_grid(self):
        N = self.env.N
        ox, oy = self.grid_offset_x, self.grid_offset_y

        for r in range(N):
            for c in range(N):
                x, y = ox + c * CELL_SIZE, oy + r * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                if (r, c) in self.explored_pos:
                    pygame.draw.rect(self.screen, EXPLORED_COLOR, rect)
                elif (r, c) in self.frontier_pos:
                    pygame.draw.rect(self.screen, FRONTIER_COLOR, rect)
                pygame.draw.rect(self.screen, GRAY, rect, 1)

        for r, c in self.env.obstacles:
            rect = pygame.Rect(ox + c*CELL_SIZE + 2, oy + r*CELL_SIZE + 2,
                               CELL_SIZE - 4, CELL_SIZE - 4)
            pygame.draw.rect(self.screen, OBSTACLE_COLOR, rect, border_radius=4)

        dr, dc = self.env.depot
        depot_rect = pygame.Rect(ox + dc*CELL_SIZE + 3, oy + dr*CELL_SIZE + 3,
                                 CELL_SIZE - 6, CELL_SIZE - 6)
        pygame.draw.rect(self.screen, DEPOT_COLOR, depot_rect, border_radius=6)
        lbl = self.font_sm.render("D", True, WHITE)
        self.screen.blit(lbl, (ox + dc*CELL_SIZE + CELL_SIZE//2 - lbl.get_width()//2,
                                oy + dr*CELL_SIZE + CELL_SIZE//2 - lbl.get_height()//2))

        for iid, info in self.env.items_info.items():
            ir, ic = info["location"]
            cx = ox + ic*CELL_SIZE + CELL_SIZE//2
            cy = oy + ir*CELL_SIZE + CELL_SIZE//2

            delivered = False
            if self.mode == 'solution' and self.result and self.result.get("solution"):
                step = min(self.sol_step, len(self.result["solution"]))
                if step > 0:
                    cur = self.result["solution"][step - 1][1]
                    delivered = iid in cur.D or iid == cur.c

            color = ITEM_DELIVERED_COLOR if delivered else ITEM_COLOR
            pygame.draw.circle(self.screen, color, (cx, cy), CELL_SIZE//3)
            plbl = self.font_sm.render(f"P{int(info['priority'])}", True, BLACK)
            self.screen.blit(plbl, (cx - plbl.get_width()//2, cy - plbl.get_height()//2))

        if self.mode == 'solution' and self.sol_path:
            for i in range(min(self.sol_step, len(self.sol_path) - 1)):
                r1, c1 = self.sol_path[i]
                r2, c2 = self.sol_path[i + 1]
                if (r1, c1) != (r2, c2):
                    p1 = (ox + c1*CELL_SIZE + CELL_SIZE//2, oy + r1*CELL_SIZE + CELL_SIZE//2)
                    p2 = (ox + c2*CELL_SIZE + CELL_SIZE//2, oy + r2*CELL_SIZE + CELL_SIZE//2)
                    pygame.draw.line(self.screen, BLUE, p1, p2, 3)

        if self.mode == 'solution' and self.result and self.result.get("solution") and self.sol_path:
            step = min(self.sol_step, len(self.sol_path) - 1)
            rr, rc = self.sol_path[step]
            carrying = False
            if step > 0 and step <= len(self.result["solution"]):
                carrying = self.result["solution"][step - 1][1].c != 0
        else:
            rr, rc = self.env.start
            carrying = False

        rx = ox + rc*CELL_SIZE + CELL_SIZE//2
        ry = oy + rr*CELL_SIZE + CELL_SIZE//2
        clr = ROBOT_CARRYING_COLOR if carrying else ROBOT_COLOR
        pygame.draw.circle(self.screen, clr, (rx, ry), CELL_SIZE//3 + 2)
        pygame.draw.circle(self.screen, WHITE, (rx, ry), CELL_SIZE//3 - 2, 2)
        rlbl = self.font_sm.render("R", True, WHITE)
        self.screen.blit(rlbl, (rx - rlbl.get_width()//2, ry - rlbl.get_height()//2))

    def _draw_sidebar(self):
        N = self.env.N
        sx = N * CELL_SIZE

        pygame.draw.rect(self.screen, WHITE, (sx, 0, SIDEBAR_WIDTH, self.height))
        pygame.draw.line(self.screen, GRAY, (sx, 0), (sx, self.height), 2)

        self.screen.set_clip(pygame.Rect(sx, 0, SIDEBAR_WIDTH, self.height))

        x = sx + PAD
        y = PAD + self.sidebar_scroll

        self.screen.blit(self.font_title.render("Warehouse Robot", True, BLACK), (x, y))
        y += 40

        if self.result:
            lines = [
                f"Algorithm: {self.result['algorithm']}",
                f"Found: {'Yes' if self.result.get('solution') else 'No'}",
                f"Path Cost: {self.result['cost']}" if self.result.get('solution') else "Path Cost: N/A",
                f"Nodes Expanded: {self.result['nodes_expanded']}",
                f"Nodes Generated: {self.result['nodes_generated']}",
                f"Max Frontier: {self.result.get('max_frontier_size', 'N/A')}",
                f"Time: {self.result['time']:.4f}s",
                "",
                f"Mode: {self.mode}",
                f"Speed: {self.speed} steps/frame",
            ]
            if self.mode == 'solution' and self.result.get("solution"):
                step = min(self.sol_step, len(self.result["solution"]))
                if step > 0:
                    st = self.result["solution"][step - 1][1]
                    lines += [
                        "",
                        "--- Current State ---",
                        f"Position: {st.p}",
                        f"Carrying: {st.c if st.c != 0 else 'None'}",
                        f"Delivered: {sorted(st.D) if st.D else '{}'}",
                        f"Energy: {st.E}",
                        f"Step: {self.sol_step}/{len(self.sol_path)-1}",
                    ]
        else:
            lines = ["No search result loaded"]

        for line in lines:
            self.screen.blit(self.font_md.render(line, True, BLACK), (x, y))
            y += LINE_H

        y += SECTION_GAP
        pygame.draw.line(self.screen, GRAY, (x, y), (x + SIDEBAR_WIDTH - 2*PAD, y), 1)
        y += 10
        self.screen.blit(self.font_lg.render("Controls", True, BLACK), (x, y))
        y += HEADER_H
        for ctrl in ["SPACE: Play/Pause", "RIGHT: Step forward", "UP/DOWN: Speed +/-",
                      "S: Jump to solution", "F: Fast forward", "R: Reset", "Q/ESC: Quit"]:
            self.screen.blit(self.font_sm.render(ctrl, True, DARK_GRAY), (x, y))
            y += 20

        y += SECTION_GAP
        pygame.draw.line(self.screen, GRAY, (x, y), (x + SIDEBAR_WIDTH - 2*PAD, y), 1)
        y += 10
        self.screen.blit(self.font_lg.render("Legend", True, BLACK), (x, y))
        y += HEADER_H
        for color, label in [
            (EXPLORED_COLOR, "Explored cell"), (FRONTIER_COLOR, "Frontier cell"),
            (OBSTACLE_COLOR, "Obstacle"), (DEPOT_COLOR, "Depot"),
            (ITEM_COLOR, "Item (undelivered)"), (ITEM_DELIVERED_COLOR, "Item (delivered/carried)"),
            (ROBOT_COLOR, "Robot"), (ROBOT_CARRYING_COLOR, "Robot (carrying)"),
        ]:
            pygame.draw.rect(self.screen, color, (x, y, 18, 18))
            pygame.draw.rect(self.screen, BLACK, (x, y, 18, 18), 1)
            self.screen.blit(self.font_sm.render(label, True, BLACK), (x + 24, y + 1))
            y += LINE_H

        self.sidebar_content_h = y - self.sidebar_scroll + PAD

        if self.sidebar_content_h > self.height:
            bar_h = max(20, int(self.height * (self.height / self.sidebar_content_h)))
            scroll_range = self.sidebar_content_h - self.height
            frac = -self.sidebar_scroll / scroll_range if scroll_range > 0 else 0
            bar_y = int(frac * (self.height - bar_h))
            pygame.draw.rect(self.screen, GRAY,
                             (sx + SIDEBAR_WIDTH - 8, bar_y, 5, bar_h), border_radius=2)

        self.screen.set_clip(None)


def visualize_pygame(env, result):
    vis = PygameVisualizer(env, result)
    vis.run()
