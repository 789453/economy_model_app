

import scipy.optimize as opt
import numpy as np
import random

class I_M:
    def __init__(self, bop):
        self.bop = bop

class G_M:
    def __init__(self, p_fd) -> None:
        self.p_fd=p_fd
        self.p_c=1.5*random.uniform(1.01,1.02)*p_fd
        self.goods_supply = np.nan
        self.goods_demand = np.nan
    
    def adjust_p_fd(self, consumer, factory, l_m):
        def objective(p_fd):
            # Calculate labor supply
            consumer.lab = opt.fminbound(lambda lab: -consumer.Utility(l_m, self), 0.1, 16)
            labor_supply = consumer.lab * consumer.n
            # Calculate labor demand
            factory.N = opt.fminbound(lambda N: -factory.Revenue(l_m, self, consumer), 0.1, consumer.n * 16)
            labor_demand = factory.N
            # Return the absolute difference
            return abs(labor_supply - labor_demand)
        
        def constraint(p_fd):      
            return factory.A * factory.K**0.2 * factory.N**0.8 - (l_m.w * consumer.lab / p_fd) * consumer.n
        
        # Define the constraint in the format required by scipy.optimize.minimize
        cons = {'type': 'ineq', 'fun': constraint}
              
        # Optimize p_fd to minimize the difference between labor supply and demand
        result = opt.minimize(objective, x0=self.p_fd, bounds=[(min(self.p_fd-0.001,1), self.p_fd+0.001)], constraints=cons, method='SLSQP')
        
        # Debugging: Check if optimization was successful
        '''
        if result.success:
            print(f"Optimization successful: {result.x[0]}")
        else:
            print("Optimization failed:", result.message)
        '''
        randomlize = random.uniform(1, 1.0012) #控制价格的随机性，且有累计效应，如(0.99,1.015)会使得价格快速上涨，只因两端不平衡
        self.p_fd = result.x[0] * randomlize
        self.p_c=1.5*self.p_fd
        return self.p_fd * randomlize

