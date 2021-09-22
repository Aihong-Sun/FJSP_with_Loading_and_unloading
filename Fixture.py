from decimal import Decimal
class Fixture_Time_window:
    def __init__(self, Fixture_index):
        self.Fixture_index = Fixture_index
        self.assigned_machine = []
        self.Work_Situation = []
        self.O_start = []
        self.O_end = []
        self.End_time = 0
    
    def Machine_use(self,start,end):
        F=self.O_end.index(start)
        L=self.O_start.index(end)
        Ft=self.assigned_machine[F:L]
        if len(Ft)==2:
            return True
        else:
            if Ft!=[]:
                M=Ft[0]
                for i in Ft:
                    if M!=i:
                        return False
                return True

    def Front_and_rear(self, start, end):
        L=9999
        if end<=self.O_start[0]:
            F=9999
            L=self.assigned_machine[0]
        else:
            for i in range(len(self.O_end)):
                if start>=self.O_end[i]:
                    F = self.assigned_machine[self.O_end.index(self.O_end[i])]
                    break
            for j in range(len(self.O_start)):
                if end>self.O_start[j]:
                    pass
                else:
                    L = self.assigned_machine[self.O_start.index(self.O_start[j])]
        return [F,L]
    
    # 机器的哪些时间窗是空的,此处只考虑内部封闭的时间窗
    def Empty_time_window(self):
        time_window_start = []
        time_window_end = []
        len_time_window = []
        F_L = []  # 时间窗对应夹具前后所在的机器
        if self.O_end ==[]:
            pass
        elif len(self.O_end) == 1:
            if self.O_start[0] != 0:
                time_window_start = [0]
                time_window_end = [self.O_start[0]]
        elif len(self.O_end) > 1:
            if self.O_start[0] != 0:
                time_window_start.append(0)
                time_window_end.append(self.O_start[0])
            time_window_start.extend(self.O_end[:-1])  # 因为使用时间窗的结束点就是空时间窗的开始点
            time_window_end.extend(self.O_start[1:])
        if time_window_end !=[]:
            len_time_window = [[time_window_start[i],time_window_end[i]] for i in range(len(time_window_end)) if time_window_end[i] - time_window_start[i]!=0 ]
            if len(len_time_window)>0:
                for j in range(len(len_time_window)):
                    try:
                        F = self.assigned_machine[self.O_end.index(len_time_window[j][0])]
                    except:
                        F=9999
                    try:
                        L = self.assigned_machine[self.O_start.index(len_time_window[j][1])]
                    except:
                        L=9999
                    F_L.append([F, L])
        return  len_time_window,F_L
    
    def _Input(self,Start_Load,Start_Unload,Load,Unload,Machine,Job=None,Process=None):
        Start_Load=float(Decimal(Start_Load).quantize(Decimal("0.0")))
        Start_Unload=float(Decimal( Start_Unload).quantize(Decimal("0.0")))
        L1=float(Decimal( Start_Load+Load).quantize(Decimal("0.0")))
        Unload=float(Decimal( Unload).quantize(Decimal("0.0")))
        L2 = float(Decimal(Process+Start_Load+Load).quantize(Decimal("0.0")))
        L3=float(Decimal(Start_Unload+Unload).quantize(Decimal("0.0")))
        self.O_start.append(Start_Load)
        self.O_end.append(L1)
        self.O_start.sort()
        self.O_end.sort()
        Index = self.O_start.index(Start_Load)
        self.Work_Situation.insert(Index, 'Load')
        self.assigned_machine.insert(Index,Machine)
        if Process!=None:
            self.O_start.append(L1)
            self.O_end.append(L2)
            self.O_start.sort()
            self.O_end.sort()
            Index = self.O_start.index(L1)
            self.Work_Situation.insert(Index, Job+1)
            self.assigned_machine.insert(Index, Machine)
        self.O_start.append(Start_Unload)
        self.O_end.append(L3)
        self.O_start.sort()
        self.O_end.sort()
        Index = self.O_start.index(Start_Unload)
        self.Work_Situation.insert(Index, 'Unload')
        self.assigned_machine.insert(Index, Machine)
        self.End_time = self.O_end[-1]