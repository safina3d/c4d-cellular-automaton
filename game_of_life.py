# Author: Safina3d
# 3D Cellular Automata Visualization using Cinema 4D
# This script simulates a 3D version of the Game of Life using Cinema 4D.
# It visualizes the evolution of cells based on specified rules, and renders them as particles.

# Global variables: birth_min, birth_max, survival_min, survival_max, refresh

import c4d
from c4d import documents, Vector
from itertools import product

# Define global rule variables
global birth_min, birth_max, survival_min, survival_max, refresh

class Cell:
    """ Represents an individual cell in the simulation. """
    def __init__(self, age=1):
        self.age = age  # Age of the cell

class Generation:
    """ Manages the current state of the cellular grid. """
    def __init__(self):
        self.cells = {}  # Stores the cells with their positions as keys

    def is_cell_alive(self, pos):
        """ Checks if a cell at the given position is alive. """
        return pos in self.cells

    def get_neighbours(self, pos):
        """ Returns the positions of neighbours of a cell at the given position. """
        x, y, z = pos
        offsets = [-1, 0, 1]
        # Generating positions of all neighbouring cells
        neighbours = [(x+dx, y+dy, z+dz) for dx, dy, dz in product(offsets, repeat=3) if (dx, dy, dz) != (0, 0, 0)]
        return neighbours

    def count_alive_neighbours(self, pos):
        """ Counts the number of alive neighbours around the given position. """
        return sum(1 for neighbour in self.get_neighbours(pos) if self.is_cell_alive(neighbour))

    def update(self):
        """ Updates the grid to the next generation based on the rules. """
        new_cells = {}
        potential_cells = set(self.cells.keys())

        # Checking each cell and its neighbours to determine if it should survive or a new cell should be born
        for cell in self.cells.keys():
            potential_cells.update(self.get_neighbours(cell))

        for cell in potential_cells:
            alive_neighbours = self.count_alive_neighbours(cell)
            if self.is_cell_alive(cell):
                if survival_min <= alive_neighbours <= survival_max:
                    new_cells[cell] = Cell(self.cells[cell].age + 1)
            else:
                if birth_min <= alive_neighbours <= birth_max:
                    new_cells[cell] = Cell()

        self.cells = new_cells

class C4dRender:
    """ Handles rendering of the cellular automata in Cinema 4D. """
    SCALE_COEF = 10  # Scaling factor for particle positions
    OLDEST_CELL_AGE = 10  # Tracks the age of the oldest cell for color mapping

    def __init__(self):
        self.generation = Generation()  # The generation object managing the cells
        self.doc = documents.GetActiveDocument()  # Active Cinema 4D document
        self.tp = self.doc.GetParticleSystem()  # Particle system of the document
        self.root_group = self.tp.GetRootGroup()  # Root group for particles
        self.init_generation()  # Initialize the first generation

    def init_generation(self):
        """ Initializes the first generation with a custom set of points. """
        # Define the initial points for the first generation
        init_points = [(x, y, z) for x in range(-3, 4) for y in range(-3, 4) for z in range(-3, 4) if (x + y + z) % 2 == 0]

        for p in init_points:
            self.generation.cells[p] = Cell()

    def update(self):
        """ Updates the particle system with the current generation. """
        self.tp.FreeAllParticles()  # Clear all existing particles
        for pos, cell in self.generation.cells.items():
            self.render(cell, pos)  # Render each cell
        c4d.EventAdd()  # Refresh Cinema 4D UI
        self.generation.update()  # Update to the next generation

    def render(self, cell, pos):
        """ Renders a single cell as a particle. """
        C4dRender.OLDEST_CELL_AGE = max(cell.age, C4dRender.OLDEST_CELL_AGE)
        p = self.tp.AllocParticle()
        self.tp.SetGroup(p, self.root_group)
        x, y, z = pos

        # Calculate distance from center and adjust particle size based on age and distance
        distance_from_center = (x**2 + y**2 + z**2)**.5
        size_factor = cell.age**2 * (1 / (1 + distance_from_center * cell.age)) * 200

        # Set particle properties
        self.tp.SetPosition(p, Vector(x, y, z) * C4dRender.SCALE_COEF)
        self.tp.SetSize(p, size_factor)
        self.tp.SetColor(p, Vector(c4d.utils.RangeMap(cell.age, 0, C4dRender.OLDEST_CELL_AGE, 0, 1, True), 0.8, 0.9))

instance = C4dRender()

def main():
    """ Main function to control the update of generations. """
    global frame
    if frame % refresh == 0:
        instance.update()  # Update the instance if the condition is met
