from wrapper_osc import OSCWrapper
from wrapper_iml import IMLWrapper
from wrapper_tolvera import TolveraWrapper
from iipyper import run
import numpy as np
import tolvera as tol
import taichi as ti

def main(x=1920, y=1080, n=64, species=5, fps=120, 
        local_host="127.0.0.1", local_client="127.0.0.1",
        pd_receive_port=7561, pd_send_port=7562
    ):

    # OSC
    osc_local = OSCWrapper(local_host, local_client, pd_receive_port, pd_send_port, "osc_local", verbose=False)

    # Tolvera
    t = TolveraWrapper(x, y, n, species, fps, headless=False)

    # IML
    source_size = 2
    def source_func():
        return np.random.rand(2)
    target_size = 1
    target = 0
    def target_func(mapped_values):
        nonlocal target
        target = mapped_values
        print(target)
    iml = IMLWrapper(source_size, source_func, target_size, target_func, randomise=False)

    for i in range(16):
        s = np.random.rand(2)
        print(s,i)
        iml.iml.add(s, i)

    @ti.func
    def map_inner():
        
        return iml.iml.map([0,0])

    @ti.kernel
    def test_():
        test()

    # test_()

    r = np.zeros((16,16))
    for i,y in enumerate(c):
        for j,x in enumerate(c):
            r[i,j] = iml.map([x,y])
    

    # OSC Map
    '''
    Max → Python
    '''
    io, update_rate = 'receive', 1

    # Attractors
    @osc_local.map.add(x=(x/2,0,x), y=(y/2,0,y), io=io, count=update_rate)
    def attractor_pos(x: float, y: float):
        nonlocal t
        t.attractors.field[0].p.pos[0] = x
        t.attractors.field[0].p.pos[1] = y
    
    @osc_local.map.add(distance=(y,0,y), weight=(2,0,10), io=io, count=update_rate)
    def attractor_dist(distance: float, weight: float):
        nonlocal t
        t.attractors.field[0].p.mass = weight
        t.attractors.field[0].radius = distance

    # Render loop
    def render():
        osc_local.map()
        iml()
        t()

    tol.utils.render(render, t.pixels)

if __name__ == "__main__":
    run(main)
