'''
TODO: TolveraIML Class prototype
'''

from iml import IML
from mrp import MRP
from iipyper import OSC, run, Updater, OSCSendUpdater, OSCMap
import tolvera as tol
import torch

class TolveraIML:
    def __init__(self, x=1920, y=1080, n=64, species=5, fps=120, host="127.0.0.1", client="127.0.0.1", receive_port=7561, send_port=7562):
        self.x = x
        self.y = y
        self.n = n
        self.species = species
        self.fps = fps
        self.host = host
        self.client = client
        self.receive_port = receive_port
        self.send_port = send_port
        self.setup()
    
    def setup(self):
        self.setup_osc()
        self.setup_tolvera()
        self.setup_mrp()
        self.setup_iml()
        # self.setup_osc_map()
        
    def setup_tolvera(self):
        tol.init(x=self.x, y=self.y, n=self.n, species=self.species, fps=self.fps)
        self.particles = tol.Particles(self.x, self.y, self.n, self.species, wall_margin=0)
        self.pixels = tol.Pixels(self.x, self.y, evaporate=0.95, fps=self.fps)
        self.boids = tol.vera.Boids(self.x, self.y, self.species)
        self.attractors = tol.vera.Attractors(self.x, self.y, n=1)
        self.attractors.set(0, tol.vera.Attractor(p=tol.Particle(active=1,pos=[self.x/2, self.y/2], mass=2), radius=self.y))

    def setup_iml(self):
        self.iml_source_size = (self.n, 2) # 2D array for ProjectAndSort
        self.iml_target_size = 16
        self.iml_source = torch.zeros(self.iml_source_size)
        self.iml_target = torch.zeros(self.iml_target_size)
        self.iml = IML(self.iml_source_size, embed='ProjectAndSort')
        for m in range(32):
            source = torch.rand(self.iml_source_size)
            target = m #torch.FloatTensor(m)# + torch.randn(iml_target_size)*2
            self.iml.add(source, target)
        
    def iml_map(self):
        self.iml_source = self.particles.osc_get_pos_all_2d()
        self.iml_target[:] = torch.from_numpy(self.iml.map(self.iml_source, k=5))
        # print(list2model("test", iml_target[0], iml_target.tolist()))
    # iml_update = Updater(iml_map, 24)

    def iml_send(self):
        self.iml_map()
        return [0]
    # osc_iml_send = OSCSendUpdater(osc, "/resonators", iml_send, 1)

    # Render loop
    def render(self):
        # self.iml_update()
        # self.osc_iml_send()
        self.osc_map()
        self.attractors(self.particles)
        self.particles.seek(self.attractors.get(0))
        self.pixels.diffuse()
        self.pixels.decay()
        self.boids(self.particles)
        self.particles(self.pixels)

def main(x=1920, y=1080, n=64, species=5, fps=120, host="127.0.0.1", client="127.0.0.1", receive_port=7561, send_port=7562
    ):
    tolIML = TolveraIML(x=x, y=y, n=n, species=species, fps=fps, host=host, client=client, receive_port=receive_port, send_port=send_port)
    tol.utils.render(tolIML.render, tolIML.pixels)

    '''
    Max → Python
    '''
    io, update_rate = 'receive', 5

    # Attractors
    @osc_map.add(x=(x/2,0,x), y=(y/2,0,y), io=io, count=update_rate)
    def attractor_pos(x: float, y: float):
        nonlocal attractors
        self.attractors.field[0].p.pos[0] = x
        self.attractors.field[0].p.pos[1] = y
    
    @osc_map.add(distance=(y,0,y), weight=(2,0,10), io=io, count=update_rate)
    def attractor_dist(distance: float, weight: float):
        attractors.field[0].p.mass = weight
        attractors.field[0].radius = distance

    '''
    Python → Patcher
    '''
    io, update_rate = 'send', 7
    send_mode = 'broadcast' # | 'event'
    send_counter = 0

if __name__=='__main__':
    run(main)
