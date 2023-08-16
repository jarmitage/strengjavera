import torch
from iml import IML
from iipyper import OSCSendUpdater, Updater

from harmonics import basic_harmonic_series

class IMLWrapper:
    '''
    Operates in two modes:
    1. If the target is remote (OSC), send the target out as OSC
    2. If the target is local (function), run the target_f function
    '''
    def __init__(self, source_size, source_f, target_size, target_f=None, update_rate=10, osc=None, path=None, random_pairs=32, randomise=True):
        assert callable(source_f), "source_f must be a function"
        self.source_f = source_f
        if target_f is not None:
            assert callable(target_f), "target_f must be a function"
            self.target_f = target_f
        self.source_size = source_size
        self.target_size = target_size
        self.source = torch.zeros(self.source_size)
        self.target = torch.zeros(self.target_size)
        if type(self.source_size) is tuple:
            self.iml = IML(self.source_size, embed='ProjectAndSort')
        else:
            self.iml = IML(self.source_size)
        self.random_pairs = random_pairs
        if randomise:
            self.randomise()
        self.update_rate = update_rate
        self.osc = osc
        self.path = path
        if self.osc is not None:
            self.updater = OSCSendUpdater(self.osc, self.path, self.map, self.update_rate)
        else:
            self.updater = Updater(self.update_target_f, self.update_rate)
    def sigmoid_randn(self, n, factor=0.5):
        tensor = torch.randn(n) * factor
        return torch.sigmoid(tensor)
    def beta_randn(self, n, theta, beta):
        dist = torch.distributions.beta.Beta(theta, beta)
        return dist.sample((n,))
    def randomise(self):
        for i in range(self.random_pairs):
            # self.source = self.sigmoid_randn(self.source_size, factor=0.9)
            # self.target = self.sigmoid_randn(self.target_size, factor=0.9)
            # self.source = torch.rand(self.source_size)
            # self.target = torch.rand(self.target_size)
            self.source = torch.rand(self.source_size)
            self.target = self.beta_randn(self.target_size, 0.1, 0.1)
            # series = torch.from_numpy(basic_harmonic_series(self.target_size))
            # self.target = series * self.target
            # print(self.source, self.target)
            self.iml.add(self.source, self.target)
    def map(self, k=5):
        self.source = self.source_f()
        self.target[:] = torch.from_numpy(self.iml.map(self.source, k=k))
        return self.target.tolist()
    # def send(self, k=5):
    #     '''
    #     Take output of map() and prepare to be sent as OSC
    #     '''
    #     target = self.map(k=k)
    #     return target
    def update_target_f(self):
        assert self.target_f is not None, "target_f must be a function"
        target = self.map()
        self.target_f(target)
    def __call__(self):
        return self.updater()
