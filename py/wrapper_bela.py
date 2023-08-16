

class BelaWrapper:
    def __init__(self):
        self.fluid_spectral_shape = {
            'centroid': 0.0,
            'spread': 0.0,
            'skewness': 0.0,
            'kurtosis': 0.0,
            'rolloff': 0.0,
            'flatness': 0.0,
            'crest': 0.0
        }
        self.fluid_novelty_feature = 0.0
        self.fluid_amp_feature = 0.0
        self.fluid_sine_feature = {n: [0.0, 0.0] for n in range(8)}
    def tolist(self):
        fluid_spectral_shape_values = list(self.fluid_spectral_shape.values())
        fluid_sine_feature_values = list(self.fluid_sine_feature.values())
        self.aslist = fluid_spectral_shape_values + [self.fluid_novelty_feature] + [self.fluid_amp_feature] + fluid_sine_feature_values
        return self.aslist
    def __call__(self):
        return self.tolist()
