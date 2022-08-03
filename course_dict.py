class course_dict:
    def __init__(self):
        super().__init__()

        self.course_type()
        self.course_inout()
        self.course_turn()

    def course_type(self):
        self.type = {'잔디': 1,
                     '더트': 2,
                     1: '잔디',
                     2: '더트'}

    def course_inout(self):
        self.inout = {'구분없음': 1,
                      '내': 2,
                      '내측': 2,
                      '외': 3,
                      '외측': 3,
                      '외내': 4,
                      '내외': 5,
                      1: '구분없음',
                      2: '내',
                      3: '외',
                      4: '외내',
                      5: '내외'}

    def course_turn(self):
        self.turn = {'우': 1,
                     '좌': 2,
                     '직선': 4,
                     1: '우',
                     2: '좌',
                     4: '직선'}