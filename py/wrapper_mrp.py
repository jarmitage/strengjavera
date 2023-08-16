from mrp import MRP

class MRPWrapper:
    def __init__(self, osc, notes):
        self.mrp = MRP(osc.host, verbose=False)
        self.n_min = self.mrp.settings['range']['start']
        self.n_max = self.mrp.settings['range']['end']
        self.n_duty = {n:0 for n in range(self.n_min, self.n_max+1)}
        self.notes = notes
        self.data = [{
            int(n):{
                'pitch': 0,
                'harmonics_raw': [0]*16
            } for n in self.notes
        }]
        # [self.mrp.note_on(n) for n in self.notes]

