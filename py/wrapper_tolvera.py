import tolvera as tol

class TolveraWrapper:
    def __init__(self, x, y, n, species, fps, headless):
        self.x = x
        self.y = y
        self.n = n
        self.species = species
        self.fps = fps
        self.headless = headless
        tol.init(x=x, y=y, n=n, species=species, fps=fps, headless=headless)
        self.particles = tol.Particles(x, y, n, species, wall_margin=0)
        self.pixels = tol.Pixels(x, y, evaporate=0.95, fps=fps)
        self.boids = tol.vera.Boids(x, y, species)
        self.attractors = tol.vera.Attractors(x, y, n=1)
        self.attractors.set(0, tol.vera.Attractor(p=tol.Particle(active=1,pos=[x/2, y/2], mass=2), radius=y))
    def render(self):
        self.attractors(self.particles)
        self.particles.seek(self.attractors.get(0))
        self.pixels.diffuse()
        self.pixels.decay()
        self.boids(self.particles)
        self.particles(self.pixels)
    def __call__(self):
        self.render()
