# Copyright (c) 2024 Huang Zengyang
# All rights reserved.
#
# This code is proprietary and confidential. Unauthorized copying,
# distribution, or modification of this file, via any medium, is strictly prohibited.
# Proprietary and confidential.

# 版权所有 (c) 2024 黄增阳
# 保留所有权利。
#
# 本代码为专有和机密信息。未经授权，严禁通过任何媒介复制、分发或修改本文件。
# 专有和机密。

import scipy.optimize as opt
import math
import random

class Consumer:
    def __init__(self, n, lab) -> None:
        self.n = n  #number of consumer
        self.lab = lab  #labor time
        self.lei = 16 - lab  #leisure time
        self.utility = 0
        self.utility_alg1 = 1 
        self.utility_alg2 = 1.5 

    def Utility(self, l_m, g_m):
        self.utility = self.utility_alg1 * math.log(self.lei) + self.utility_alg2 * math.log(l_m.w * self.lab / g_m.p_fd)
        return self.utility
    
    def Population_growth(self, fd_growth_rate):
        self.n = self.n * (1 + fd_growth_rate / 1000) 

    def update_lab(self, l_m, g_m):
        def utility_to_minimize(lab):
            lei = 16 - lab
            return -(self.utility_alg1 * math.log(lei) + self.utility_alg2 * math.log(l_m.w * lab / g_m.p_fd))

        # result = opt.minimize_scalar(utility_to_minimize, bounds=(min(max(self.lab-0.001, 4),min(self.lab+0.001, 15.9)), max(max(self.lab-0.001, 4),min(self.lab+0.001, 15.9))), method='bounded')
        result = opt.minimize_scalar(utility_to_minimize, bounds=(min(self.lab-0.1, 0.01), max(self.lab+0.1, 16)), method='bounded')
        randomlize = random.uniform(0.98, 1.02) #影响供给侧的随机化
        self.lab = result.x * randomlize
        self.lei = 16 - self.lab * randomlize
        return self.lab * randomlize

'''
读取python文件，删除tab4，要求政策实施给出一个新tab，单独可以调整财政政策1、2、货币政策3、4 定量调节（在主页面设置并配上图），整个文件给出背景图，
文字排版改为游戏画风； 代码逻辑模型内容不变，且导入的其他文件都正确不用调整不用给出；  萧条和不同类型的冲击，也给出新tab，配图，多选的调节在主页面
（侧栏仍保留不变），给出修改后的对应部分代码，不用全部给出
'''



