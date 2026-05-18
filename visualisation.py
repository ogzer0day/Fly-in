import pygame as pg

class Visualizer:
    def __init__(self, map_instance, simulator):
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
        pg.display.set_caption("Drone Flow - SPACE to step, M to auto-play")
        self.font = pg.font.Font(None, 20)
        self.small_font = pg.font.Font(None, 12)
        self.drone_colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), 
                            (255, 255, 100), (255, 100, 255), (100, 255, 255),
                            (255, 150, 50), (150, 255, 50), (50, 150, 255), (255, 50, 150)]

    def run(self):
        running = True
        self.clock = pg.time.Clock()
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
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
            
            # Draw connections
            for conn in self.map.all_connections:
                h1 = self.map.all_hubs[conn.hub1_name]
                h2 = self.map.all_hubs[conn.hub2_name]
                pg.draw.line(self.screen, (100, 200, 100), 
                           (int(h1.X * self.scale + self.padding), int(h1.Y * self.scale + self.padding)),
                           (int(h2.X * self.scale + self.padding), int(h2.Y * self.scale + self.padding)), 4)
            
            # Draw hubs
            for hub in self.map.all_hubs.values():
                x, y = int(hub.X * self.scale + self.padding), int(hub.Y * self.scale + self.padding)
                color = (0, 255, 0) if hub == self.map.start_hub else ((255, 0, 0) if hub == self.map.end_hub else (0, 0, 255))
                pg.draw.circle(self.screen, color, (x, y), 25)
                text = self.small_font.render(hub.name, True, (255, 255, 255))
                self.screen.blit(text, (x - text.get_width() // 2, y - 35))
            
            # Draw drones with colors and numbers
            for drone in self.sim.active_drones:
                if not self.sim.is_end[drone.id]:
                    hub = self.map.all_hubs[drone.current_position]
                    x, y = int(hub.X * self.scale + self.padding), int(hub.Y * self.scale + self.padding)
                    color = self.drone_colors[(drone.id - 1) % len(self.drone_colors)]
                    pg.draw.circle(self.screen, color, (x, y), 12)
                    num_text = self.font.render(str(drone.id), True, (0, 0, 0))
                    self.screen.blit(num_text, (x - 8, y - 8))
            
            # Draw status
            mode = "MANUAL (SPACE=step)" if self.manual_mode else ("AUTO (PAUSED)" if self.paused else "AUTO (RUNNING)")
            text = self.font.render(f"Turn: {self.sim.turns} | {mode} | M=toggle mode", True, (255, 255, 255))
            self.screen.blit(text, (10, 10))
            
            pg.display.flip()
            self.clock.tick(3)
        
        pg.quit()
