'''
TODO: MRP Updater funcs - does `@cleanup` work? add to tolvera?
TODO: IML1 Particles->Harmonics
    random mappings don't work very well...
    harmonics.py -> numpy to torch...?
    species -> notes etc
TODO: Lag harmonics and flucoma data
TODO: Tolvera data synthesis...? Headless?
TODO: IML2 Bela->Boids test
TODO: IML add/remove pairs funcs
TODO: IML port plotting funcs from Victor's notebook
TODO: Tolvera IML1 & IML2 tryptych(s)
TODO: MRP SC simulator iipyper MIDI output
TODO: MRP Pd simulator
'''

from iipyper import run, cleanup
import tolvera as tol

from wrapper_osc import OSCWrapper
from wrapper_tolvera import TolveraWrapper
from wrapper_iml import IMLWrapper
from wrapper_bela import BelaWrapper
from wrapper_mrp import MRPWrapper    

def main(x=1920, y=1080, n=64, species=5, fps=120, 
        local_host="127.0.0.1", local_client="127.0.0.1",
        bela_host ="192.168.7.1", bela_client ="192.168.7.2", 
        pd_receive_port=7561, pd_send_port=7562, mrp_send_port=7770,
        headless=False
    ):

    # OSC
    osc_local = OSCWrapper(local_host, local_client, pd_receive_port, pd_send_port, "osc_local", verbose=False)
    osc_local.host.create_client("mrp", local_client, mrp_send_port)
    osc_bela = OSCWrapper(bela_host, bela_client, pd_receive_port, pd_send_port, "osc_bela")

    # Tolvera
    t = TolveraWrapper(x, y, n, species, fps, headless)

    # MRP
    mrp = MRPWrapper(osc_local, [
        24, 29, 31, 
        36, 41, 43, 
        48, 53, 55, 
        60, 65, 67, 
        72, 77, 79, 
        84])
    mrp.test_note_on()

    # Bela Flucoma
    # bela = BelaWrapper()
    # print(bela()) # TODO: test this, should be 1d

    # IML
    iml_particles_harmonics = IMLWrapper((n,2), t.particles.osc_get_pos_all_2d, 16, mrp.test_harmonics_raw, update_rate=20) # TODO: need to handle sending to MRP
    # iml_flucoma_boids = IMLWrapper((len(bela())), bela.tolist, 16) # TODO: need a boids.set_all_rules() func

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

    # @osc_bela.map.add(centroid=(20,20,20e3), spread=(20,20,20e3), skewness=(0,0,8), kurtosis=(0,0,128), rolloff=(20,20,20e3), flatness=(0,-120,0), crest=(0,0,60), io=io, count=update_rate)
    # def fluid_spectralshape(centroid: float, spread: float, skewness: float, kurtosis: float, rolloff: float, flatness: float, crest: float):
    #     nonlocal bela
    #     bela.fluid_spectral_shape['centroid'] = centroid
    #     bela.fluid_spectral_shape['spread'] = spread
    #     bela.fluid_spectral_shape['skewness'] = skewness
    #     bela.fluid_spectral_shape['kurtosis'] = kurtosis
    #     bela.fluid_spectral_shape['rolloff'] = rolloff
    #     bela.fluid_spectral_shape['flatness'] = flatness
    #     bela.fluid_spectral_shape['crest'] = crest
    #     print(f"bela.fluid_spectral_shape: {bela.fluid_spectral_shape}")
    
    # @osc_bela.map.add(novelty=(0,0,1), io=io, count=update_rate)
    # def fluid_noveltyfeature(novelty: float):
    #     nonlocal bela
    #     bela.fluid_novelty_feature = novelty
    #     print(f"bela.fluid_novelty_feature: {bela.fluid_novelty_feature}")
    
    # @osc_bela.map.add(amp=(0,0,1), io=io, count=update_rate)
    # def fluid_ampfeature(amp: float):
    #     nonlocal bela
    #     bela.fluid_amp_feature = amp
    #     print(f"bela.fluid_amp_feature: {bela.fluid_amp_feature}")

    # @osc_bela.map.add(f0=(20,20,20e3), io=io, count=update_rate)
    # def fluid_sinefeature(f0: float, f1: float, f2: float, f3: float, f4: float, f5: float, f6: float, f7: float, m0: float, m1: float, m2: float, m3: float, m4: float, m5: float, m6: float, m7: float):
    #     nonlocal fluid_sine_feature
    #     fluid_sine_feature = {
    #         0: [f0, m0], 1: [f1, m1], 2: [f2, m2], 3: [f3, m3],
    #         4: [f4, m4], 5: [f5, m5], 6: [f6, m6], 7: [f7, m7]
    #     }
    #     print(f"fluid_sine_feature: {fluid_sine_feature}")

    # '''
    # Python → Patcher
    # '''
    # io, update_rate = 'send', 7
    # send_mode = 'broadcast' # | 'event'
    # send_counter = 0


    # Render loop
    def render():
        # osc_iml_send()
        # osc_bela.map()
        osc_local.map()
        iml_particles_harmonics()
        t()

    tol.utils.render(render, t.pixels)

    @cleanup
    def _():
        mrp.mrp.cleanup()

if __name__=='__main__':
    run(main)
