import pygame
from typing import Dict, Tuple
import random

WIDTH, HEIGHT = 800, 600
NODE_SIZE = 20


class GraphVisualizer:
    def __init__(self, nodes, edges):
        """
        nodes: dict -> {name: (x, y, type)}
        edges: list of (u, v)
        """
        self.nodes = nodes
        self.edges = edges

        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Drone Simulation")

    def transform(self, x, y):
        # scale coordinates to screen
        return x * 50 + 100, y * 50 + 100

    def draw_nodes(self):
        for name, data in self.nodes.items():
            x, y, t = data
            px, py = self.transform(x, y)

            if t == "start":
                color = (0, 255, 0)
            elif t == "end":
                color = (255, 255, 0)
            elif t == "blocked":
                color = (100, 100, 100)
            elif t == "restricted":
                color = (255, 0, 0)
            elif t == "priority":
                color = (0, 200, 255)
            else:
                color = (200, 200, 200)

            pygame.draw.circle(self.screen, color, (px, py), NODE_SIZE)

    def draw_edges(self):
        for u, v in self.edges:
            x1, y1, _ = self.nodes[u]
            x2, y2, _ = self.nodes[v]

            pygame.draw.line(
                self.screen,
                (150, 150, 150),
                self.transform(x1, y1),
                self.transform(x2, y2),
                2
            )

    def draw_drones(self, drones):
        """
        drones: { "D1": "A", "D2": "B" }
        """
        for d, node in drones.items():
            x, y, _ = self.nodes[node]
            px, py = self.transform(x, y)

            pygame.draw.circle(self.screen, (0, 0, 255), (px, py), 8)

    def render(self, drones):
        self.screen.fill((30, 30, 30))

        self.draw_edges()
        self.draw_nodes()
        self.draw_drones(drones)

        pygame.display.update()

    def run(self, get_state_callback):
        """
        get_state_callback must return:
        nodes, drones per frame
        """

        clock = pygame.time.Clock()
        running = True

        while running:
            clock.tick(2)  # simulation speed

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            nodes, drones = get_state_callback()
            self.nodes = nodes

            self.render(drones)

        pygame.quit()

def get_state_callback():
    # Example nodes (static or can evolve)
    nodes = {
        "A": (1, 1, "start"),
        "B": (3, 1, "normal"),
        "C": (3, 3, "end"),
        "D": (1, 3, "restricted"),
    }

    # Example drones moving randomly
    drones = {
        "D1": random.choice(list(nodes.keys())),
        "D2": random.choice(list(nodes.keys())),
    }

    return nodes, drones


if __name__ == "__main__":
    nodes = {
        "A": (1, 1, "start"),
        "B": (3, 1, "normal"),
        "C": (3, 3, "end"),
        "D": (1, 3, "restricted"),
    }

    edges = [
        ("A", "B"),
        ("B", "C"),
        ("C", "D"),
        ("D", "A"),
    ]

    viz = GraphVisualizer(nodes, edges)
    viz.run(get_state_callback)