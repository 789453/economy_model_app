

import scipy.optimize as opt
import random
import numpy as np

class L_M:
    def __init__(self, w) -> None:
        self.w = w
        self.labor_supply = np.nan
        self.labor_demand = np.nan
        
    def adjust_w(self, consumer, factory, g_m):
        def objective(w):
            # Calculate labor supply
            consumer.lab = opt.fminbound(lambda lab: -consumer.Utility(self, g_m), 0.1, 16)
            labor_supply = consumer.lab * consumer.n
            # Calculate labor demand
            factory.N = opt.fminbound(lambda N: -factory.Revenue(self, g_m, consumer), 0.1, consumer.n * 16)
            labor_demand = factory.N
            # Return the absolute difference
            return abs(labor_supply - labor_demand)
        
        # Optimize the wage to minimize the difference between labor supply and demand
        result = opt.minimize_scalar(objective, bounds=(max(self.w-0.001,0.00001), self.w+0.001), method='bounded')
        randomlize = random.uniform(1, 1.002)
        self.w = result.x * randomlize
        return self.w * randomlize
