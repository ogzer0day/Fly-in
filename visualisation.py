import pygame as pg
from typing import Any


class Visualizer:
    """Pygame-based visualization for drone flow simulation."""

    def __init__(self, map_instance: Any, simulator: Any) -> None:
        """Initialize visualizer with map and simulation instances."""
        self.map = map_instance
        self.sim = simulator
        self.paused = True
        self.manual_mode = True
        self.scale = 60
        self.padding = 200

        width = 1500
        height = 700

        pg.init()
        self.screen = pg.display.set_mode((width, height))
        pg.display.set_caption(
            "Drone Flow - SPACE to step, M to auto-play"
        )
        self.font = pg.font.Font(None, 20)
        self.small_font = pg.font.Font(None, 12)
        self.drone_colors = [
            (255, 100, 100), (100, 255, 100), (100, 100, 255),
            (255, 255, 100), (255, 100, 255), (100, 255, 255),
            (255, 150, 50), (150, 255, 50), (50, 150, 255),
            (255, 50, 150)
        ]

    def run(self) -> None:
        """Main loop - handle events, update simulation, and render."""
        running = True
        self.clock = pg.time.Clock()
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if (event.type == pg.KEYDOWN and
                        event.key == pg.K_SPACE):
                    if self.manual_mode:
                        self.sim.manual_step()
                    else:
                        self.paused = not self.paused
                if event.type == pg.KEYDOWN and event.key == pg.K_m:
                    self.manual_mode = not self.manual_mode
                    self.paused = True

            if not self.paused and not self.manual_mode:
                self.sim.step()

            self.screen.fill((0, 0, 0))

            for conn in self.map.all_connections:
                h1 = self.map.all_hubs[conn.hub1_name]
                h2 = self.map.all_hubs[conn.hub2_name]
                x1 = int(h1.X * self.scale + self.padding)
                y1 = int(h1.Y * self.scale + self.padding)
                x2 = int(h2.X * self.scale + self.padding)
                y2 = int(h2.Y * self.scale + self.padding)
                pg.draw.line(
                    self.screen, (100, 200, 100),
                    (x1, y1), (x2, y2), 4
                )

            for hub in self.map.all_hubs.values():
                x = int(hub.X * self.scale + self.padding)
                y = int(hub.Y * self.scale + self.padding)
                if hub == self.map.start_hub:
                    color = (0, 255, 0)
                elif hub == self.map.end_hub:
                    color = (255, 0, 0)
                else:
                    color = (0, 0, 255)
                pg.draw.circle(self.screen, color, (x, y), 25)
                text = self.small_font.render(
                    hub.name, True, (255, 255, 255)
                )
                self.screen.blit(
                    text, (x - text.get_width() // 2, y - 35)
                )

            for drone in self.sim.active_drones:
                if not self.sim.is_end[drone.id]:
                    hub = self.map.all_hubs[drone.current_position]
                    x = int(hub.X * self.scale + self.padding)
                    y = int(hub.Y * self.scale + self.padding)
                    color_idx = (drone.id - 1) % len(
                        self.drone_colors
                    )
                    color = self.drone_colors[color_idx]
                    pg.draw.circle(self.screen, color, (x, y), 12)
                    num_text = self.font.render(
                        str(drone.id), True, (0, 0, 0)
                    )
                    self.screen.blit(num_text, (x - 8, y - 8))

            if self.manual_mode:
                mode = "MANUAL (SPACE=step)"
            elif self.paused:
                mode = "AUTO (PAUSED)"
            else:
                mode = "AUTO (RUNNING)"
            text = self.font.render(
                f"Turn: {self.sim.turns} | {mode} | M=toggle mode",
                True, (255, 255, 255)
            )
            self.screen.blit(text, (10, 10))

            pg.display.flip()
            self.clock.tick(3)

        pg.quit()
