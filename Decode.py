from Machine import Machine_Time_window
from Job import Job
from Fixture import Fixture_Time_window
import random
import matplotlib.pyplot as plt
import numpy as np
from decimal import Decimal

class Decode:
    def __init__(self,Processing_time,Fixture,Loading_time,Unloading_time,J,M_num,Fix_num):
        self.Processing_time=Processing_time
        self.Fixture=Fixture
        self.Loading_time=Loading_time
        self.Unloading_time=Unloading_time
        self.Machines=[]
        for j in range(M_num):
            self.Machines.append(Machine_Time_window(j))
        self.Jobs = []
        for k, v in J.items():
            self.Jobs.append(Job(k, v))
        self.Fixtures=[]
        for i in range(Fix_num):
            self.Fixtures.append(Fixture_Time_window(i))
        self.P1=0.5     #选择完工时间最小的概率
        self.P2=0.8     #选择准结时间最小的概率

    def Pair(self,Job):
        O_num=Job.Current_Processed()
        P=[]    #可用资源组合
        Machine=[M for M in range(len(self.Processing_time[Job.Job_index-1][O_num])) if self.Processing_time[Job.Job_index-1][O_num][M]!=9999]
        Fixture=self.Fixture[Job.Job_index-1][O_num]
        for i in Machine:
            for j in Fixture:
                P.append([i,j-1])
        return P

    #机器和夹具的时间窗交集
    def Intersection_of_time_windows(self, F_w,M_w, M_end_time, W_end_time,Machine,Fixture):
        W_Tstart=[F_w[i_2][0] for i_2 in range(len(F_w))]
        W_Tend=[F_w[i_3][1] for i_3 in range(len(F_w))]
        M_Tstart=[M_w[i_4][0] for i_4 in range(len(M_w))]
        M_Tend = [M_w[i_5][1] for i_5 in range(len(M_w))]

        if M_end_time < W_end_time:
            M_Tstart.append(M_end_time)
            M_Tend.append(W_end_time)
        if M_end_time > W_end_time:
            W_Tstart.append(W_end_time)
            W_Tend.append(M_end_time)
        I_start = []
        I_end = []
        for i in range(len(M_Tstart)):
            for j in range(len(W_Tstart)):
                if W_Tstart[j] <= M_Tstart[i] and W_Tend[j] <= M_Tend[i] and W_Tend[j] - M_Tstart[i]>0:
                    I_start.append(M_Tstart[i])
                    I_end.append(W_Tend[j])
                if M_Tstart[i] <= W_Tstart[j] and W_Tend[j] <= M_Tend[i]:
                    I_start.append(W_Tstart[j])
                    I_end.append(W_Tend[j])
                if M_Tstart[i] <= W_Tstart[j] and M_Tend[i] <= W_Tend[j] and M_Tend[i] - W_Tstart[j] > 0:
                    I_start.append(W_Tstart[j])
                    I_end.append(M_Tend[i])
                if W_Tstart[j] < M_Tstart[i] and M_Tend[i] < W_Tend[j]:
                    I_start.append(M_Tstart[i])
                    I_end.append(M_Tend[i])
        I_len = [[I_start[i_1], I_end[i_1]] for i_1 in range(len(I_start)) if I_end[i_1]- I_start[i_1]!=0]
        MFL=[]
        FFL=[]
        if I_len!=[]:
            for i_1 in range(len(I_len)):
                MFL.append(self.Machines[Machine].Front_and_rear(I_len[i_1][0],I_len[i_1][1]))
                FFL.append(self.Fixtures[Fixture]. Front_and_rear(I_len[i_1][0],I_len[i_1][1]))
        return  I_len,MFL,FFL

    #情况1：机器和夹具都未使用
    def Situation1(self,Job,Pair):
        ealiest=Job.Last_Processing_end_time
        O_num=Job.Current_Processed()
        load_time=self.Loading_time[Pair[1]][Pair[0]]
        unloading_time=self.Unloading_time[Pair[1]][Pair[0]]
        load_time2=0
        unloading_time2=0
        processing_time=self.Processing_time[Job.Job_index-1][O_num][Pair[0]]
        Influenced_Fixture=None
        Influenced_Machine=None
        return ealiest,processing_time,load_time,unloading_time,load_time2,unloading_time2,Influenced_Machine,Influenced_Fixture

    #情况2：机器未使用，夹具已使用
    def Situation2(self,Job,Pair,Fixture):
        J_let=Job.Last_Processing_end_time      #工件前道工序完成时间
        F_let=Fixture.End_time                  #夹具的最后完工时间
        O_num = Job.Current_Processed()
        load_time = self.Loading_time[Pair[1]][Pair[0]]
        unloading_time = self.Unloading_time[Pair[1]][Pair[0]]
        load_time2=0
        unloading_time2=0
        Influenced_Machine=None
        Influenced_Fixture=None
        processing_time = self.Processing_time[Job.Job_index-1][O_num][Pair[0]]
        F_w,F_L=Fixture.Empty_time_window()     #注：F_w:时间窗，F_L:时间窗前后使用机器情况
        ealiest=max(J_let,F_let)
        if len(F_w)>=1:
            for i in range(len(F_w)):
                if F_L[i][0]!=F_L[i][1]:    #时间窗前后夹具所在机器不同
                    if F_w[i][1]-F_w[i][0]>=load_time+unloading_time+processing_time:
                        if F_w[i][0]>=J_let:
                            ealiest=F_w[i][0]
                            break
                        if F_w[i][0]<J_let and F_w[i][1]-J_let>=load_time+unloading_time+processing_time:
                            ealiest=J_let
                            break
                else:   #时间窗前后夹具所在机器相同
                    #第一种情况：时间窗内机器上有另一道使用了其他夹具的工序，无需增加装卸时间
                    if self.Machines[F_L[i][0]].Fixture_use(F_w[i][0],F_w[i][1])==False:
                        if F_w[i][1] - F_w[i][0] >= load_time + unloading_time + processing_time:
                            if F_w[i][0] >= J_let:
                                ealiest = F_w[i][0]
                                break
                            if F_w[i][0] < J_let and F_w[i][1] - J_let >= load_time + unloading_time + processing_time:
                                ealiest = J_let
                                break
                    #第二种情况：时间窗内没有使用其他夹具的工序，需增加装卸时间
                    else:
                        Influenced_Machine=F_L[i][0]
                        Influenced_Fixture=Pair[1]
                        load_time2=self.Loading_time[Pair[1]][F_L[i][0]]
                        unloading_time2=self.Unloading_time[Pair[1]][F_L[i][0]]
                        if F_w[i][1] - F_w[i][0] >= load_time+load_time2 + unloading_time+unloading_time2 + processing_time:
                            if F_w[i][0] >= J_let:
                                ealiest = F_w[i][0]
                                break
                            if F_w[i][0] < J_let and F_w[i][1] - J_let >= load_time+load_time2 + unloading_time+unloading_time2 + processing_time:
                                ealiest = J_let
                                break
        return ealiest,processing_time,load_time,unloading_time,load_time2,unloading_time2,Influenced_Machine,Influenced_Fixture
    
    #情况3：机器已使用，夹具未使用
    def Situation3(self,Job,Pair,Machine):
        J_let = Job.Last_Processing_end_time  # 工件前道工序完成时间
        M_let = Machine.End_time  # 机器的最后完工时间
        O_num = Job.Current_Processed()
        load_time = self.Loading_time[Pair[1]][Pair[0]]
        unloading_time = self.Unloading_time[Pair[1]][Pair[0]]
        load_time2=0
        unloading_time2=0
        Influenced_Machine=None
        Influenced_Fixture=None
        processing_time = self.Processing_time[Job.Job_index-1][O_num][Pair[0]]
        ealiest = max(J_let, M_let)
        F_w ,F_L= Machine.Empty_time_window()
        ealiest = max(J_let, M_let)
        if len(F_w) >= 1:
            for i in range(len(F_w)):
                if F_L[i][0]!=F_L[i][1]:    #时间窗前后机器上的夹具不一样
                    if F_w[i][1] - F_w[i][0] >= load_time + unloading_time + processing_time:
                        if F_w[i][0] >= J_let:
                            ealiest = F_w[i][0]
                            break
                        if F_w[i][0] < J_let and F_w[i][1] - J_let >= load_time + unloading_time + processing_time:
                            ealiest = J_let
                            break
                else:   #时间窗前后机器上的夹具一样
                    #第一种情况，尽管时间窗前后的夹具一样，但时间窗内夹具可能使用在其他机器，不用增加装卸时间
                    if self.Fixtures[F_L[i][0]].Machine_use(F_w[i][0],F_w[i][1])==False:
                        if F_w[i][1] - F_w[i][0] >= load_time + unloading_time + processing_time:
                            if F_w[i][0] >= J_let:
                                ealiest = F_w[i][0]
                                break
                            if F_w[i][0] < J_let and F_w[i][1] - J_let >= load_time + unloading_time + processing_time:
                                ealiest = J_let
                                break
                    #第二种情况，时间窗前后夹具一样，且时间窗内该夹具没有用到其他地方
                    else:
                        Influenced_Machine=Pair[0]
                        Influenced_Fixture=F_L[i][0]
                        load_time2=self.Loading_time[F_L[i][0]][Pair[0]]
                        unloading_time2=self.Unloading_time[F_L[i][0]][Pair[0]]
                        if F_w[i][1] - F_w[i][0] >= load_time+load_time2 + unloading_time+unloading_time2 + processing_time:
                            if F_w[i][0] >= J_let:
                                ealiest = F_w[i][0]
                                break
                            if F_w[i][0] < J_let and F_w[i][1] - J_let >= load_time+load_time2 + unloading_time+unloading_time2 + processing_time:
                                ealiest = J_let
                                break
        return ealiest, processing_time, load_time, unloading_time,load_time2,unloading_time2,Influenced_Machine,Influenced_Fixture

    #情况4：机器和夹具都已使用
    def Situation4(self,Job,Pair,Machine,Fixture):
        J_let = Job.Last_Processing_end_time  # 工件前道工序完成时间
        M_let = Machine.End_time  # 机器的最后完工时间
        F_let=Fixture.End_time    # 夹具的最后完工时间
        O_num = Job.Current_Processed()
        load_time = self.Loading_time[Pair[1]][Pair[0]]
        unloading_time = self.Unloading_time[Pair[1]][Pair[0]]
        load_time2=0
        unloading_time2=0
        Influenced_Machine=None
        Influenced_Fixture=None
        processing_time = self.Processing_time[Job.Job_index-1][O_num][Pair[0]]
        if Machine.assigned_Fixture!=[] and Fixture.assigned_machine!=[]:
            if Machine.assigned_Fixture[-1]==Pair[1] and Fixture.assigned_machine[-1]==Pair[0]: #夹具在当前机器上
                ealiest=max(J_let,M_let)-unloading_time
            else:
                ealiest = max(J_let, M_let, F_let)
        else:
            ealiest = max(J_let, M_let,F_let)
        M_w, MF_L0= Machine.Empty_time_window()
        F_w,FF_L0=Fixture.Empty_time_window()
        if len(M_w)>0 and len(F_w)>0:
            WT,MF_L,FF_L=self.Intersection_of_time_windows(F_w,M_w,M_let,F_let,Pair[0],Pair[1])
            if len(WT)>0:
                for i in range(len(WT)):
                    #考虑机器时间窗前后夹具不同的使用情况
                    if MF_L[i][0]!=MF_L[i][1]:
                        if MF_L[i][0]!=Pair[1] and MF_L[i][1]!=Pair[1]:   #情况1：时间窗前后机器所用夹具与所选夹具都不相同
                            if WT[i][1] - WT[i][0] >= load_time + unloading_time + processing_time:
                                if WT[i][0] >= J_let:
                                    ealiest = WT[i][0]
                                    break
                                if WT[i][0] < J_let and WT[i][1] - J_let >= load_time + unloading_time + processing_time:
                                    ealiest = J_let
                                    break
                        if MF_L[i][0]==Pair[1]:    #情况2：时间窗前机器使用的夹具与所选相同，后不同
                            if WT[i][1] - WT[i][0] >=  unloading_time + processing_time:
                                if WT[i][0] >= J_let:
                                    ealiest = WT[i][0]
                                    load_time=0
                                    break
                                if WT[i][0] < J_let and WT[i][1] - J_let >=  unloading_time + processing_time:
                                    ealiest = J_let
                                    load_time=0
                                    break
                        if MF_L[i][1]==Pair[1]:    #情况3：时间窗后机器使用的夹具与所选相同，前不同
                            if WT[i][1] - WT[i][0] >= load_time +  processing_time:
                                if WT[i][0] >= J_let:
                                    ealiest = WT[i][0]
                                    unloading_time=0
                                    break
                                if WT[i][0] < J_let and WT[i][1] - J_let >= load_time +  processing_time:
                                    ealiest = J_let
                                    unloading_time=0
                                    break
                    #时间窗前后机器使用的夹具相同但与所选夹具不同
                    if MF_L[i][0]==MF_L[i][1] and MF_L[i][0]!=Pair[1]:
                        if self.Fixtures[MF_L[i][0]].Machine_use(WT[i][0], WT[i][1]) == True: #情况4：时间窗内夹具没有在其他机器上使用
                            Influenced_Machine=Pair[0]
                            Influenced_Fixture=MF_L[i][1]
                            load_time2=self.Loading_time[Pair[0]][MF_L[i][0]]
                            unloading_time2=self.Unloading_time[Pair[0]][MF_L[i][0]]
                            if WT[i][1] - WT[i][0] >= load_time+load_time2 + unloading_time+unloading_time2 + processing_time:
                                if WT[i][0] >= J_let:
                                    ealiest = WT[i][0]
                                    break
                                if WT[i][0] < J_let and WT[i][1] - J_let >= load_time+load_time2 + unloading_time+unloading_time2 + processing_time:
                                    ealiest = J_let
                                    break
                        else:               #情况5：时间窗内夹具在其他机器上使用了
                            if WT[i][1] - WT[i][0] >= load_time + unloading_time + processing_time:
                                if WT[i][0] >= J_let:
                                    ealiest = WT[i][0]
                                    break
                                if WT[i][0] < J_let and WT[i][1] - J_let >= load_time + unloading_time + processing_time:
                                    ealiest = J_let
                                    break
                    #时间窗前后机器上使用的夹具相同，且与所选夹具相同
                    if MF_L[i][0]==MF_L[i][1] and MF_L[i][0]==Pair[1]:
                        if FF_L[i][0]==FF_L[i][1]:    #情况6：夹具时间窗前后使用机器相同
                            if WT[i][1] - WT[i][0] >=  processing_time:
                                if WT[i][0] >= J_let:
                                    ealiest = WT[i][0]
                                    load_time==0
                                    unloading_time==0
                                    break
                                if WT[i][0] < J_let and WT[i][1] - J_let >=  processing_time:
                                    ealiest = J_let
                                    load_time==0
                                    unloading_time==0
                                    break
                        else:                   #情况7：夹具时间窗前后使用机器不同
                            if WT[i][1] - WT[i][0] >= unloading_time + processing_time:
                                if WT[i][0] >= J_let:
                                    ealiest = WT[i][0]
                                    load_time=0
                                    break
                                if WT[i][0] < J_let and WT[i][1] - J_let >= unloading_time + processing_time:
                                    ealiest = J_let
                                    load_time=0
                                    break
        return ealiest, processing_time, load_time, unloading_time,load_time2,unloading_time2,Influenced_Machine,Influenced_Fixture

    def Gantt(self, Machines):
        M = ['red', 'blue', 'yellow', 'orange', 'green', 'palegoldenrod', 'purple', 'pink', 'Thistle', 'Magenta',
             'SlateBlue', 'RoyalBlue', 'Cyan', 'Aqua', 'floralwhite', 'ghostwhite', 'goldenrod', 'mediumslateblue',
             'navajowhite',
             'navy', 'sandybrown', 'moccasin']
        for i in range(len(Machines)):
            Machine = Machines[i]
            Start_time = Machine.O_start
            End_time = Machine.O_end
            for i_1 in range(len(End_time)):
                # plt.barh(i,width=End_time[i_1]-Start_time[i_1],height=0.8,left=Start_time[i_1],\
                #          color=M[Machine.assigned_task[i_1][0]],edgecolor='black')
                # plt.text(x=Start_time[i_1]+0.1,y=i,s=Machine.assigned_task[i_1])
                K = Machine.Work_Situation[i_1]
                if K=='Load':
                    plt.barh(i, width=End_time[i_1] - Start_time[i_1], height=0.8, left=Start_time[i_1], \
                             color='navy', edgecolor='black')
                    # plt.text(x=Start_time[i_1] + (End_time[i_1] - Start_time[i_1]) / 2 - 0.5, y=i, s=K)
                elif K=='Unload':
                    plt.barh(i, width=End_time[i_1] - Start_time[i_1], height=0.8, left=Start_time[i_1], \
                             color='red', edgecolor='black')
                else:
                    plt.barh(i, width=End_time[i_1] - Start_time[i_1], height=0.8, left=Start_time[i_1], \
                             color='white', edgecolor='black')
                    # K = Machine.Work_Situation[i_1]
                    # K=Machine.assigned_task[i_1]
                    plt.text(x=Start_time[i_1] + (End_time[i_1] - Start_time[i_1]) / 2 - 0.5, y=i, s=K)
        plt.yticks(np.arange(i + 1), np.arange(1, i + 2))
        plt.title('Scheduling Gantt chart ')
        plt.ylabel('Machines')
        plt.xlabel('Time(s)')
        plt.show()

    def arrange_Operation(self,Time,Pair,i):
        Ci = []  # 完工时间
        Setup = []  # 准结时间
        for T_i in Time:
            K = sum(T_i[0:6])
            Q = sum(T_i[2:6])
            Ci.append(K)
            Setup.append(Q)
        r = random.random()
        if r < self.P1:
            Pair_Select = Pair[Ci.index(min(Ci))]
            T = Time[Ci.index(min(Ci))]
        elif r >= self.P1 and r < self.P2:
            Pair_Select = Pair[Setup.index(min(Setup))]
            T = Time[Setup.index(min(Setup))]
        else:
            Pair_Select = random.choice(Pair)
            T = Time[Pair.index(Pair_Select)]
        self.Jobs[i]._Input(T[0], T[0] + T[1] + T[2] + T[3] + T[4], Pair_Select[0], Pair_Select[1])
        if T[6] != None:
            self.Machines[T[6]]._Input(T[0], T[0] + T[1] + T[2] + T[3] + T[4], T[4], T[5], T[7])
            self.Fixtures[T[7]]._Input(T[0], T[0] + T[1] + T[2] + T[3] + T[4], T[4], T[5], T[6])
            self.Machines[Pair_Select[0]]._Input(T[0] + T[4], T[0] + T[4] + T[2] + T[1], T[2], T[3], Pair_Select[1], i,
                                                 T[1])
            self.Fixtures[Pair_Select[1]]._Input(T[0] + T[4], T[0] + T[4] + T[2] + T[1], T[2], T[3], Pair_Select[0], i,
                                                 T[1])
        else:
            self.Machines[Pair_Select[0]]._Input(T[0], T[0] + T[2] + T[1], T[2], T[3], Pair_Select[1], i, T[1])
            self.Fixtures[Pair_Select[1]]._Input(T[0], T[0] + T[2] + T[1], T[2], T[3], Pair_Select[0], i, T[1])

    def Operation_Insert(self,T,Pair_Select,i):
        self.Jobs[i]._Input(T[0], T[0]+T[1]+T[2]+T[3]+T[4], Pair_Select[0], Pair_Select[1])
        if T[6] != None:
            self.Machines[T[6]]._Input(T[0],T[0]+T[1]+T[2]+T[3]+T[4],T[4],T[5],T[7])
            self.Fixtures[T[7]]._Input(T[0], T[0]+T[1]+T[2]+T[3]+T[4], T[4], T[5], T[6])
            self.Machines[Pair_Select[0]]._Input(T[0] + T[4], T[0] + T[4] + T[2] + T[1], T[2], T[3], Pair_Select[1], i,
                                                 T[1])
            self.Fixtures[Pair_Select[1]]._Input(T[0] + T[4], T[0] + T[4] + T[2] + T[1], T[2], T[3], Pair_Select[0], i,
                                                 T[1])
        else:
            self.Machines[Pair_Select[0]]._Input(T[0], T[0] + T[2] + T[1], T[2], T[3], Pair_Select[1], i, T[1])
            self.Fixtures[Pair_Select[1]]._Input(T[0], T[0] + T[2] + T[1], T[2], T[3], Pair_Select[0], i, T[1])

    def main(self,CHS):
        for i in CHS:
            Job=self.Jobs[i]
            Pair=self.Pair(Job)
            Time=[]
            for j in range(len(Pair)):
                Machine = self.Machines[Pair[j][0]]
                Fixture = self.Fixtures[Pair[j][1]]
                #机器和夹具都未使用
                if Machine.End_time==0 and Fixture.End_time==0: 
                    A1=self.Situation1(Job,Pair[j])
                    Time.append(A1)
                #机器未使用，夹具已使用
                if Machine.End_time==0 and  Fixture.End_time!=0:
                    A2=self.Situation2(Job,Pair[j],Fixture)
                    Time.append(A2)
                #机器已使用，夹具未使用
                if Machine.End_time != 0 and Fixture.End_time == 0:
                    A3 = self.Situation3(Job, Pair[j], Machine)
                    Time.append(A3)
                #机器已使用，夹具已使用
                if Machine.End_time != 0 and Fixture.End_time != 0:
                    A4 = self.Situation4(Job, Pair[j], Machine,Fixture)
                    Time.append(A4)
            #按照规则选择合适的组合
            self.arrange_Operation(Time,Pair,i)
            self.Gantt(self.Machines)

if __name__=='__main__':
    from Instance1 import Processing_time,fixture,Loading_time,Unloading_time,J_num,O_num,M_num,Fix_num,J
    D=Decode(Processing_time,fixture,Loading_time,Unloading_time,J,M_num,Fix_num)
    # Pair1=[1,0]
    # T1=[0,12,1.6,0.7,0,0,None,None]
    # i1=0
    # D.Operation_Insert(T1,Pair1,i1)
    # Pair2 = [2, 0]
    # T2 = [14.3, 9,0.7,1.4, 0, 0, None, None]
    # i2 = 1
    # D.Operation_Insert(T2, Pair2, i2)
    # Pair3 = [1, 0]
    # T3 = [25.4, 9, 1.6, 0.7, 0, 0, None, None]
    # i3 = 1
    # D.Operation_Insert(T3, Pair3, i3)
    # # D.Gantt(D.Fixtures)
    CHS=[1,1,0,0,0,1,2,2,2]
    D.main(CHS)



                    
            



