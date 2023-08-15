'''
TODO: MRP Updater funcs - does `@cleanup` work?
TODO: MRP SC simulator iipyper MIDI output
TODO: IML wrapper class
TODO: Bela/Flucoma wrapper class
TODO: IML1 Particles->Harmonics test
TODO: IML2 Bela->Boids test
TODO: IML add/remove pairs funcs
TODO: IML port plotting funcs from Victor's notebook
TODO: Tolvera data synthesis...? Headless?
TODO: Tolvera IML1 & IML2 tryptych(s)
TODO: Bela Lag input data
TODO: MRP Pd simulator
'''

from iml import IML
from mrp import MRP
from iipyper import OSC, run, Updater, OSCSendUpdater, OSCMap, cleanup, repeat
import tolvera as tol
import torch

# TODO: Move into class that can be used from ipynb
# class TolveraIML:
#     def __init__(self):
#         pass

class OSCWrapper:
    def __init__(self, host_ip, client_ip, receive_port, send_port, name, create_patch=True, patch_type="Pd"):
        self.host_ip = host_ip
        self.client_ip = client_ip
        self.receive_port = receive_port
        self.send_port = send_port
        self.name = name
        self.create_patch = create_patch
        self.patch_type = patch_type
        self.host = OSC(self.host_ip, self.receive_port, verbose=True, concurrent=True)
        self.host.create_client(self.name, self.client_ip, self.send_port)
        self.map = OSCMap(self.host, self.name, create_patch=self.create_patch, patch_type=self.patch_type, patch_filepath=self.name)

def main(x=1920, y=1080, n=64, species=5, fps=120, 
        local_host="127.0.0.1", local_client="127.0.0.1",
        bela_host ="192.168.7.1", bela_client ="192.168.7.2", 
        pd_receive_port=7561, pd_send_port=7562, mrp_send_port=7770,
        headless=False
    ):

    # OSC
    osc_local = OSCWrapper(local_host, local_client, pd_receive_port, pd_send_port, "osc_local")
    osc_local.host.create_client("mrp", local_client, mrp_send_port)
    osc_bela = OSCWrapper(bela_host, bela_client, pd_receive_port, pd_send_port, "osc_bela")
    
    # Tolvera
    tol.init(x=x, y=y, n=n, species=species, fps=fps, headless=headless)
    particles = tol.Particles(x, y, n, species, wall_margin=0)
    pixels = tol.Pixels(x, y, evaporate=0.95, fps=fps)
    boids = tol.vera.Boids(x, y, species)
    attractors = tol.vera.Attractors(x, y, n=1)
    attractors.set(0, tol.vera.Attractor(p=tol.Particle(active=1,pos=[x/2, y/2], mass=2), radius=y))

    # MRP
    mrp = MRP(osc_local.host, verbose=False) # TODO: Probably this wont work
    mrp_n_min = mrp.settings['range']['start']
    mrp_n_max = mrp.settings['range']['end']
    mrp_note_duty = {n:0 for n in range(mrp_n_min, mrp_n_max+1)}
    mrp_notes = [
        24, 29, 31, 
        36, 41, 43, 
        48, 53, 55, 
        60, 65, 67, 
        72, 77, 79, 
        84]
    mrp_data = [{
        int(n):{
            'pitch': 0,
            'harmonics_raw': [0]*16
        } for n in mrp_notes
    }]
    # [mrp.note_on(n) for n in mrp_notes]

    note = 48
    note_on = False
    count=0
    test='code'#'voices', 'qualities'
    qualities=['brightness', 'intensity', 'pitch', 'pitch_vibrato', 'harmonic', 'harmonics_raw']
    
    @repeat(1)
    def _():
        nonlocal mrp, note_on, note, count, test
        if mrp is not None:
            if note_on == False:
                count+=1
                if test == 'code':
                    mrp.note_on(note)
                    mrp.quality_update(note, 'brightness', 0.5+count/10)
                    mrp.quality_update(note, 'intensity', 1.9)
                    mrp.quality_update(note, 'brightness', 1.5, relative=True)
                    mrp.quality_update(note, 'intensity', 1.9, relative=True)
                    mrp.quality_update(note, 'harmonics_raw', [1.1, 0.2, 0.3])
                    mrp.quality_update(note, 'harmonics_raw', [i/10 for i in range(0, count, 1)])
                    mrp.qualities_update(note, {
                        'brightness': 1.5,
                        'intensity': 1.0,
                        'harmonics_raw': [1.2, 0.3, 0.4]
                    })
                elif test == 'voices':
                    mrp.note_on(note+count)
                    print(len(mrp.voices), 'voices:', mrp.voices)
                elif test == 'qualities':
                    mrp.note_on(note)
                    mrp.quality_update(qualities[0], count/10)
                note_on = True
            else:
                if test == 'code':
                    mrp.note_off(note)
                elif test == 'voices':
                    if count % 2:
                        mrp.note_off(note+int(count/2))
                note_on = False

    # IML
    iml_source_size = (n, 2) # 2D array for ProjectAndSort
    iml_target_size = 16
    iml_source = torch.zeros(iml_source_size)
    iml_target = torch.zeros(iml_target_size)
    iml = IML(iml_source_size, embed='ProjectAndSort')
    def iml_add():
        for i in range(32):
            source = torch.rand(iml_source_size)
            target = torch.randn(iml_target_size)
            iml.add(source, target)
    iml_add()
    
    def iml_map():
        iml_source = particles.osc_get_pos_all_2d()
        iml_target[:] = torch.from_numpy(iml.map(iml_source, k=5))
        # print(list2model("test", iml_target[0], iml_target.tolist()))
    # iml_update = Updater(iml_map, 24)

    def iml_send():
        iml_map()
        return [0]
    # osc_iml_send = OSCSendUpdater(osc, "/resonators", iml_send, 1)

    # Features
    fluid_spectral_shape = {
        'centroid': 0.0,
        'spread': 0.0,
        'skewness': 0.0,
        'kurtosis': 0.0,
        'rolloff': 0.0,
        'flatness': 0.0,
        'crest': 0.0
    }
    fluid_novelty_feature = 0.0
    fluid_amp_feature = 0.0
    fluid_sine_feature = {n: [0.0, 0.0] for n in range(8)}

    # OSC Map

    '''
    Max → Python
    '''
    io, update_rate = 'receive', 1

    # Attractors
    @osc_bela.map.add(x=(x/2,0,x), y=(y/2,0,y), io=io, count=update_rate)
    def attractor_pos(x: float, y: float):
        nonlocal attractors
        attractors.field[0].p.pos[0] = x
        attractors.field[0].p.pos[1] = y
    
    @osc_bela.map.add(distance=(y,0,y), weight=(2,0,10), io=io, count=update_rate)
    def attractor_dist(distance: float, weight: float):
        nonlocal attractors
        attractors.field[0].p.mass = weight
        attractors.field[0].radius = distance

    @osc_bela.map.add(centroid=(20,20,20e3), spread=(20,20,20e3), skewness=(0,0,8), kurtosis=(0,0,128), rolloff=(20,20,20e3), flatness=(0,-120,0), crest=(0,0,60), io=io, count=update_rate)
    def fluid_spectralshape(centroid: float, spread: float, skewness: float, kurtosis: float, rolloff: float, flatness: float, crest: float):
        nonlocal fluid_spectral_shape
        fluid_spectral_shape['centroid'] = centroid
        fluid_spectral_shape['spread'] = spread
        fluid_spectral_shape['skewness'] = skewness
        fluid_spectral_shape['kurtosis'] = kurtosis
        fluid_spectral_shape['rolloff'] = rolloff
        fluid_spectral_shape['flatness'] = flatness
        fluid_spectral_shape['crest'] = crest
        print(f"fluid_spectral_shape: {fluid_spectral_shape}")
    
    @osc_bela.map.add(novelty=(0,0,1), io=io, count=update_rate)
    def fluid_noveltyfeature(novelty: float):
        nonlocal fluid_novelty_feature
        fluid_novelty_feature = novelty
        print(f"fluid_novelty_feature: {fluid_novelty_feature}")
    
    @osc_bela.map.add(amp=(0,0,1), io=io, count=update_rate)
    def fluid_ampfeature(amp: float):
        nonlocal fluid_amp_feature
        fluid_amp_feature = amp
        print(f"fluid_amp_feature: {fluid_amp_feature}")

    # @osc_bela.map.add(f0=(20,20,20e3), io=io, count=update_rate)
    # def fluid_sinefeature(f0: float, f1: float, f2: float, f3: float, f4: float, f5: float, f6: float, f7: float, m0: float, m1: float, m2: float, m3: float, m4: float, m5: float, m6: float, m7: float):
    #     nonlocal fluid_sine_feature
    #     fluid_sine_feature = {
    #         0: [f0, m0], 1: [f1, m1], 2: [f2, m2], 3: [f3, m3],
    #         4: [f4, m4], 5: [f5, m5], 6: [f6, m6], 7: [f7, m7]
    #     }
    #     print(f"fluid_sine_feature: {fluid_sine_feature}")

    '''
    Python → Patcher
    '''
    io, update_rate = 'send', 7
    send_mode = 'broadcast' # | 'event'
    send_counter = 0


    # Render loop
    def render():
        # osc_iml_send()
        # osc_bela.map()
        # osc_local.map()
        attractors(particles)
        particles.seek(attractors.get(0))
        pixels.diffuse()
        pixels.decay()
        boids(particles)
        particles(pixels)

    tol.utils.render(render, pixels)

    @cleanup
    def _():
        mrp.cleanup()

if __name__=='__main__':
    run(main)
