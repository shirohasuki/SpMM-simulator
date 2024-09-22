class ProcessingElement:
    def __init__(self):
        self.a = 0
        self.b = 0
        self.partial_sum = 0
        self.mul_result = 0
        self.sum_left = 0

    def compute(self, enable = False):
        if enable:
            self.mul_result  = self.a * self.b
            self.partial_sum = self.sum_left + self.mul_result
    
    def reset(self):
        self.a = 0
        self.b = 0
        self.partial_sum = 0
        self.mul_result = 0
        self.sum_up = 0
        self.sum_left = 0

    