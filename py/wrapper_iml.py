import torch
from iml import IML
from iipyper import OSCSendUpdater

class IMLWrapper:
    '''
    Operates in two modes:
    1. If the target is remote (OSC), then IMLWrapper() will send the target out as OSC
    2. If the target is local (function), then IMLWrapper() will run the target_f function
    '''
    def __init__(self, source_size, source_f, target_size, target_f=None, osc=None, path=None, random_pairs=32, randomise=True):
        assert callable(source_f), "source_f must be a function"
        self.source_f = source_f
        if self.target_f is not None:
            assert callable(target_f), "target_f must be a function"
            self.target_f = target_f
        self.source_size = source_size
        self.target_size = target_size
        self.source = torch.zeros(self.source_size)
        self.target = torch.zeros(self.target_size)
        self.random_pairs = random_pairs
        if type(self.source_size) is tuple:
            self.iml = IML(self.source_size, embed='ProjectAndSort')
        else:
            self.iml = IML(self.source_size)
        if randomise:
            self.randomise()
        self.osc = osc
        self.path = path
        if self.osc is not None:
            self.updater = OSCSendUpdater(self.osc, self.path, self.send(), 1)
    def randomise(self):
        for i in range(self.random_pairs):
            self.source = torch.rand(self.source_size)
            self.target = torch.randn(self.target_size)
            self.iml.add(self.source, self.target)
    def map(self, k=5):
        self.source = self.source_f()
        self.target[:] = torch.from_numpy(self.iml.map(self.source, k=k))
        return self.target
    def send(self, k=5):
        '''
        Take output of map() and prepare to be sent as OSC
        '''
        target = self.map(k=k)
        return target.tolist()
    def __call__(self):
        '''
        Either send target out as OSC, or run target_f
        '''
        if self.osc is not None:
            return self.updater()
        else:
            target = self.map()
            self.target_f(target)
            return target
