

import math
import random
class Factory:
    def __init__(self, A, K, consumer) -> None:
        self.A = A
        self.K = K
        self.N = consumer.n * consumer.lab
        self.revenue = 0
        self.fd = self.A * math.pow(self.K, 0.2) * math.pow(self.N, 0.8)
    
    def Production(self):
        self.fd = self.A * math.pow(self.K, 0.2) * math.pow(self.N, 0.8)
        return self.fd
    
    def Revenue(self, l_m, g_m, consumer):
        self.revenue = g_m.p_fd * ((l_m.w * consumer.lab / g_m.p_fd) * consumer.n) - l_m.w * self.N
        return self.revenue

    def Import(self, g_m):
        self.delta_K = self.revenue / g_m.p_c
        return self.delta_K


'''
2008年全球金融危机的根源是什么？

讨论次贷危机如何从房地产市场蔓延至整个金融体系，并最终导致全球经济衰退。
1997年亚洲金融危机是如何爆发的，以及它对亚洲经济体的影响？

探讨泰铢贬值如何引发连锁反应，导致多个亚洲国家的货币和股市崩溃。
20世纪70年代的石油危机如何影响了全球经济和通货膨胀？

分析两次石油危机期间，石油价格飙升对全球经济和通货膨胀的影响。
2001年阿根廷债务危机的教训是什么？

讨论阿根廷如何从固定汇率制度转向浮动汇率，以及这一过程中遇到的挑战和教训。
1987年“黑色星期一”股市崩盘的原因和长期影响是什么？

分析1987年10月19日全球股市的大幅下跌，以及其对金融监管和市场结构的长期影响。
1992年欧洲货币危机（黑色星期三）是如何发生的？'''


    