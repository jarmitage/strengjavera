from mrp import MRP

class MRPWrapper:
    def __init__(self, osc, notes, verbose=True):
        self.mrp = MRP(osc.host, verbose=verbose)
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
    def test_note_on(self):
        note = self.notes[4]
        self.mrp.note_on(note)
        self.mrp.quality_update(note, 'intensity', 1)
    def test_harmonics_raw(self, harmonics):
        assert type(harmonics) is list, f"harmonics_raw must be a list, received {type(harmonics)}"
        note = self.notes[4]
        self.mrp.quality_update(note, 'harmonics_raw', harmonics)
    def notes_on(self):
        [self.mrp.note_on(n) for n in self.notes]
    def notes_off(self):
        self.mrp.all_notes_off()
