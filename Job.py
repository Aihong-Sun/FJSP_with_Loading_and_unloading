from decimal import Decimal
class Job:
    def __init__(self,Job_index,Operation_num):
        self.Job_index=Job_index
        self.Operation_num = Operation_num
        self.Processed=[]
        self.Last_Processing_end_time=0
        self.J_start=[]
        self.J_end=[]
        self.J_machine=[]
        self.J_fixture=[]
        self.Last_Processing_Machine=0

    def Process_One(self,Machine,End_time):
        self.Processed.append(1)
        self.Last_Processing_Machine=Machine
        self.Last_Processing_end_time=End_time

    def Current_Processed(self):
        return len(self.Processed)

    def _Input(self,W_Eailiest,End_time,Machine,Fixture):
        W_Eailiest =float( Decimal(W_Eailiest).quantize(Decimal("0.0")))
        End_time = float(Decimal(End_time).quantize(Decimal("0.0")))
        self.Processed.append(1)
        self.Last_Processing_Machine=Machine
        self.Last_Processing_end_time=End_time
        self.J_start.append(W_Eailiest)
        self.J_end.append(End_time)
        self.J_machine.append(Machine)
        self.J_fixture.append(Fixture)
