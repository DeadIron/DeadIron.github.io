#!user/bin/python
#coding:utf-8
from tkinter import *
from tkinter import ttk
import shikigami as sg
import process as pr
import threading
from tkinter import filedialog
from tkinter import messagebox
import animation as anm


tempFlag=0

file=None

def center_window(w, h):
    # 获取屏幕 宽、高
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    # 计算 x, y 位置
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    
def checkData():
    for j in teamInfo[0]:
        if j.get() not in sg.shikigamiNameList:
            messagebox.showerror('错误','式神名错误：“%s”未在列表中'%j.get())
            return 1
    for j in teamInfo[-1]:
        if j.get() not in sg.soulList:
            messagebox.showerror('错误','御魂名错误：“%s”未在列表中'%j.get())
            return 1
    for i in teamInfo[1:-1]:
        for j in i:
            temp=''.join(list(filter(lambda x:x not in '0123456789%',j.get())))
            if temp:
                if not messagebox.askokcancel('提示','属性数据中存在非常规输入，可能引起错误，是否继续？'):
                    return 1
    for i in teamInfo[5:-1]:
        for j in i:
            if my_float(j.get())>4:
                if not messagebox.askokcancel('提示','属性数据中存在非常规输入，可能引起错误，是否继续？'):
                    return 1
def saveTeam():
    global teamInfo,file
    if not file:
        file=filedialog.asksaveasfilename(initialdir = './',title = "请选择保存地址",filetypes = (("阵容文件","*.gss"),("所有文件","*.*")))
    f=open(file,'w')
    for i in teamInfo:
        temp=[x.get() for x in i]
        f.write(' '.join(temp)+'\n')
    f.close()
    b3v.set(1)
    lockTeam()
    messagebox.showinfo('提示','保存成功')
def fastSaveTeam():
    f=open('teamInfo.gss','w')
    for i in teamInfo:
        temp=[x.get() for x in i]
        f.write(' '.join(temp)+'\n')
    f.close()
    b3v.set(1)
    lockTeam()
def fastReadTeam():
    with open('teamInfo.gss','r') as f:
        for i,c in enumerate(f):
            csp=c.split()
            for j,cspc in enumerate(csp):
                if isinstance(teamInfo[i][j],Entry):
                    teamInfo[i][j].delete(0,END)
                    teamInfo[i][j].insert(0,cspc)
                else:
                    teamInfo[i][j].set(cspc)
    b3v.set(1)
    lockTeam()
def saveAsTeam():
    global teamInfo,file
    file=filedialog.asksaveasfilename(initialdir = './',title = "请选择保存地址",filetypes = (("阵容文件","*.gss"),("所有文件","*.*")))
    f=open(file,'w')
    for i in teamInfo:
        temp=[x.get() for x in i]
        f.write(' '.join(temp)+'\n')
    f.close()
    b3v.set(1)
    lockTeam()
    messagebox.showinfo('提示','保存成功')    

def readTeam():
    global teamInfo
    fileToOpen=filedialog.askopenfilename(initialdir = './',title = "请选择阵容文件",filetypes = (("阵容文件","*.gss"),("所有文件","*.*")))
    with open(fileToOpen,'r') as f:
        for i,c in enumerate(f):
            csp=c.split()
            for j,cspc in enumerate(csp):
                if isinstance(teamInfo[i][j],Entry):
                    teamInfo[i][j].delete(0,END)
                    teamInfo[i][j].insert(0,cspc)
                else:
                    teamInfo[i][j].set(cspc)
    b3v.set(1)
    lockTeam()
    messagebox.showinfo('提示','读取成功')
  
def my_float(x):
    temp=0
    if x[-1]=='%':
        temp=float(x[:-1])/100
    else:
        temp=float(x)
    return temp
def loadData():
    if checkData():
        return 0
    r={}
    b={}
    r1=sg.shikigamiDict[mz1.get()]
    r[1]=r1({
    'id':1,
    '名字':mz1.get(),
    '速度':float(sd1.get()),
    '位置':0,
    '队伍':0,
    '生命':float(sm1.get()),
    '攻击':float(gj1.get()),
    '防御':float(fy1.get()),
    '暴击':my_float(bj1.get()),
    '暴击伤害':my_float(bjsh1.get()),
    '效果命中':my_float(xgmz1.get()),
    '效果抵抗':my_float(xgdk1.get()),
    '御魂':yhxg1.get(),
    })
    r2=sg.shikigamiDict[mz2.get()]
    r[2]=r2({
    'id':2,
    '名字':mz2.get(),
    '速度':float(sd2.get()),
    '位置':0,
    '队伍':0,
    '生命':float(sm2.get()),
    '攻击':float(gj2.get()),
    '防御':float(fy2.get()),
    '暴击':my_float(bj2.get()),
    '暴击伤害':my_float(bjsh2.get()),
    '效果命中':my_float(xgmz2.get()),
    '效果抵抗':my_float(xgdk2.get()),
    '御魂':yhxg2.get(),    
    })
    r3=sg.shikigamiDict[mz3.get()]
    r[3]=r3({
    'id':3,
    '名字':mz3.get(),
    '速度':float(sd3.get()),
    '位置':0,
    '队伍':0,
    '生命':float(sm3.get()),
    '攻击':float(gj3.get()),
    '防御':float(fy3.get()),
    '暴击':my_float(bj3.get()),
    '暴击伤害':my_float(bjsh3.get()),
    '效果命中':my_float(xgmz3.get()),
    '效果抵抗':my_float(xgdk3.get()),
    '御魂':yhxg3.get(),
    })
    r4=sg.shikigamiDict[mz4.get()]
    r[4]=r4({
    'id':4,
    '名字':mz4.get(),
    '速度':float(sd4.get()),
    '位置':0,
    '队伍':0,
    '生命':float(sm4.get()),
    '攻击':float(gj4.get()),
    '防御':float(fy4.get()),
    '暴击':my_float(bj4.get()),
    '暴击伤害':my_float(bjsh4.get()),
    '效果命中':my_float(xgmz4.get()),
    '效果抵抗':my_float(xgdk4.get()),
    '御魂':yhxg4.get(),
    })
    r5=sg.shikigamiDict[mz5.get()]
    r[5]=r5({
    'id':5,
    '名字':mz5.get(),
    '速度':float(sd5.get()),
    '位置':0,
    '队伍':0,
    '生命':float(sm5.get()),
    '攻击':float(gj5.get()),
    '防御':float(fy5.get()),
    '暴击':my_float(bj5.get()),
    '暴击伤害':my_float(bjsh5.get()),
    '效果命中':my_float(xgmz5.get()),
    '效果抵抗':my_float(xgdk5.get()),
    '御魂':yhxg5.get(),
    })
    b1=sg.shikigamiDict[mz21.get()]
    b[1]=b1({
    'id':6,
    '名字':mz21.get(),
    '速度':float(sd21.get()),
    '位置':0,
    '队伍':1,
    '生命':float(sm21.get()),
    '攻击':float(gj21.get()),
    '防御':float(fy21.get()),
    '暴击':my_float(bj21.get()),
    '暴击伤害':my_float(bjsh21.get()),
    '效果命中':my_float(xgmz21.get()),
    '效果抵抗':my_float(xgdk21.get()),
    '御魂':yhxg21.get(),
    })
    b2=sg.shikigamiDict[mz22.get()]
    b[2]=b2({
    'id':7,
    '名字':mz22.get(),
    '速度':float(sd22.get()),
    '位置':0,
    '队伍':1,
    '生命':float(sm22.get()),
    '攻击':float(gj22.get()),
    '防御':float(fy22.get()),
    '暴击':my_float(bj22.get()),
    '暴击伤害':my_float(bjsh22.get()),
    '效果命中':my_float(xgmz22.get()),
    '效果抵抗':my_float(xgdk22.get()),
    '御魂':yhxg22.get(),
    })
    b3=sg.shikigamiDict[mz23.get()]
    b[3]=b3({
    'id':8,
    '名字':mz23.get(),
    '速度':float(sd23.get()),
    '位置':0,
    '队伍':1,
    '生命':float(sm23.get()),
    '攻击':float(gj23.get()),
    '防御':float(fy23.get()),
    '暴击':my_float(bj23.get()),
    '暴击伤害':my_float(bjsh23.get()),
    '效果命中':my_float(xgmz23.get()),
    '效果抵抗':my_float(xgdk23.get()),
    '御魂':yhxg23.get(),
    })
    b4=sg.shikigamiDict[mz24.get()]
    b[4]=b4({
    'id':9,
    '名字':mz24.get(),
    '速度':float(sd24.get()),
    '位置':0,
    '队伍':1,
    '生命':float(sm24.get()),
    '攻击':float(gj24.get()),
    '防御':float(fy24.get()),
    '暴击':my_float(bj24.get()),
    '暴击伤害':my_float(bjsh24.get()),
    '效果命中':my_float(xgmz24.get()),
    '效果抵抗':my_float(xgdk24.get()),
    '御魂':yhxg24.get(),
    })
    b5=sg.shikigamiDict[mz25.get()]
    b[5]=b5({
    'id':10,
    '名字':mz25.get(),
    '速度':float(sd25.get()),
    '位置':0,
    '队伍':1,
    '生命':float(sm25.get()),
    '攻击':float(gj25.get()),
    '防御':float(fy25.get()),
    '暴击':my_float(bj25.get()),
    '暴击伤害':my_float(bjsh25.get()),
    '效果命中':my_float(xgmz25.get()),
    '效果抵抗':my_float(xgdk25.get()),
    '御魂':yhxg25.get(),
    })
    return r,b
def run():
    t=loadData()
    if t:
        r,b=t
    else:
        return 0
    win,log=pr.main(0,r,b,debug=b4v.get())
    T.delete(1.0,END)
    T.insert(END,('胜利队：%d队\n'%(2-win))+'=====================\n')
    T.insert(END,'\n'.join(log))



def run2():
    rwins=0
    for i in range(100):
        t=loadData()
        if t:
            r,b=t
        else:
            return 0
        win,log=pr.main(0,r,b,debug=b4v.get())
        rwins+=win
        temp='进度：%d/10000\n目前1队胜利次数为%d次，胜率为%.2f%%\n'%((i+1),rwins,rwins/(i+1)*100)
        T.delete(1.0,END)
        T.insert(END,temp)
    T.insert(END,'最后一局战况：%d队胜利\n=====================\n'%(2-win))
    T.insert(END,'\n'.join(log))


def run3():
    global rwins
    th=threading.Thread(target=run2,args=())
    th.start()

def run4():
    t=loadData()
    if t:
        r,b=t
    else:
        return 0
    g={}
    g[0]=sg.裁判旗()
    g[1]=pr.animation()
#行动条的初始化

    action=[b[1],b[2],b[3],b[4],b[5],r[1],r[2],r[3],r[4],r[5],g[0]]
    action.sort(key=lambda x:(x.sp,-x.id))

#设立data是为了后面能够更容易传参，利用了python传字典参数时浅拷贝，变相使得变量全局化，同时使得调全局变量更加统一有条理。

    data={'units':[r[1],r[2],r[3],r[4],r[5],b[1],b[2],b[3],b[4],b[5]],
          'uands':[r[1],r[2],r[3],r[4],r[5],b[1],b[2],b[3],b[4],b[5]],
          'teams':[r,b],
          'action':action,
          'win':0,
          'mode':-1,
          'orb':[4,4],
          'getOrb':[3,3],
          'orbPo':[0,0],
          'swords':0,
          'extra':[],
          '反击':[],
          'summons':[None,None],
          'summonsSpecial':[None,None,None,None,None,None,None,None,None,None],
          'ids':10,
          'log':[],
          'debug':0,
          'animation':g[1],
          }
    th2=threading.Thread(target=anm.main,kwargs=({'data':data}))
    th2.start()
    th3=threading.Thread(target=pr.main,args=(-1,r,b),kwargs=({'animation':g[1],'data':data}))
    th3.start()
    
    
def lockTeam():
    if teamInfo:
        if b3v.get():
            for i in teamInfo:
                for j in i:
                 j['state']='disabled'
        else:
            for i in teamInfo:
                for j in i:
                 j['state']='normal'

root=Tk()
teamInfo=[]
center_window(500, 320)
root.resizable(1,1)
root.title('对弈！平安京')


tab=ttk.Notebook(root)
tab1=ttk.Frame(tab)
tab.add(tab1,text='基本')
tab.pack(expand=1,fill="both")
tab2=ttk.Frame(tab)
tab.add(tab2,text='1队阵容详情')
tab3=ttk.Frame(tab)
tab.add(tab3,text='2队阵容详情')

#tab1
monty01=ttk.LabelFrame(tab1,text='操作按钮')
monty01.grid(column=0,row=0,padx=10,pady=10)

b1=Button(monty01,text='单局过程',command=run)
b1.grid(column=0,row=0,padx=10,pady=10)
b2=Button(monty01,text='多局胜率',command=run3)
b2.grid(column=0,row=1,padx=10,pady=10)
b3=Button(monty01,text='单局动画',command=run4)
b3.grid(column=0,row=2,padx=10,pady=10)

monty03=ttk.LabelFrame(tab1,text='辅助选项')
monty03.grid(column=0,row=1,padx=10,pady=10)

b3v=IntVar()
b3=Checkbutton(monty03,text='锁定阵容',variable=b3v, command=lockTeam)
b3.grid(column=0,row=0,padx=10,pady=10)

b4v=IntVar()
b4=Checkbutton(monty03,text='开发模式',variable=b4v)
b4.grid(column=0,row=1,padx=10,pady=10)

monty02=ttk.LabelFrame(tab1,text='显示区域')
monty02.grid(column=1,row=0,padx=10,pady=10,rowspan=2)
S = Scrollbar(monty02)
T = Text(monty02, height=18, width=50)
S.pack(side=RIGHT, fill=Y)
T.pack(side=LEFT, fill=Y)
S.config(command=T.yview)
T.config(yscrollcommand=S.set)
initialWords="""使用方法：
    切换到1队、2队的阵容详情界面，然后将数据、式神填入，再切换到本页面，单击右方的按钮即可。
    
    “单局过程”模式下，将会模拟一局，并将过程输出到此框中。
    
    “多局胜率”模式下，将会模拟一万局，并将1队的胜率输出到此框中。

注意事项：
    
    1.式神名和御魂名需要与官方的完全一致，如“酒吞童子”而非“酒吞”，“招财猫”而非“招财”，“日女巳时”而非“日女”。如果不确定，可以从右侧的下拉列表中选择。
    
    2.暴击可以是“0.12”这种格式，也可以是“12%”这种格式，但请勿填写为“12”，这意味着1200%的暴击。暴击伤害、效果命中、效果抵抗同理。

本程序只做交流学习之用，无任何商业用途
本程序由 @两情相悦-午夜鹣鹣梦早醒 开发
因使用本程序分析结果而产生损失本人概不负责
版本号:0.1
"""
T.insert(END,initialWords)
#tab2   
monty = ttk.LabelFrame(tab2, text='红方', width=80, height=250)  
monty.grid(column=0, row=0, padx=0, pady=10) 
Label(monty,width=10, text="", relief='groove').grid(column=0, row=0, sticky='W')  
Label(monty,width=10, text="式神", relief='groove').grid(column=0, row=1, sticky='W')  
Label(monty,width=10, text="攻击", relief='groove').grid(column=0, row=2, sticky='W')
Label(monty,width=10, text="生命", relief='groove').grid(column=0, row=3, sticky='W')
Label(monty,width=10, text="防御", relief='groove').grid(column=0, row=4, sticky='W')
Label(monty,width=10, text="速度", relief='groove').grid(column=0, row=5, sticky='W')
Label(monty,width=10, text="暴击", relief='groove').grid(column=0, row=6, sticky='W')
Label(monty,width=10, text="暴击伤害", relief='groove').grid(column=0, row=7, sticky='W')
Label(monty,width=10, text="效果命中", relief='groove').grid(column=0, row=8, sticky='W')
Label(monty,width=10, text="效果抵抗", relief='groove').grid(column=0, row=9, sticky='W')
Label(monty,width=10, text="御魂效果", relief='groove').grid(column=0, row=10, sticky='W')

 #第1个式神
Label(monty,width=10, text="式神1", relief='groove').grid(column=1, row=0, sticky='W') 

mz1Var = StringVar()  
mz1 = ttk.Combobox(monty, textvariable=mz1Var, width=8)  
mz1["values"] = sg.shikigamiNameList
mz1.grid(column=1,row=1,pady=1 ,sticky='W')
mz1.current(0)

gj1=Entry(monty, width=10)
gj1.grid(column=1,row=2,pady=1 ,sticky='W')

sm1=Entry(monty, width=10)
sm1.grid(column=1,row=3,pady=1 ,sticky='W')

fy1=Entry(monty, width=10)
fy1.grid(column=1,row=4,pady=1 ,sticky='W')

sd1=Entry(monty, width=10)
sd1.grid(column=1,row=5,pady=1 ,sticky='W')

bj1=Entry(monty, width=10)
bj1.grid(column=1,row=6,pady=1 ,sticky='W')

bjsh1=Entry(monty, width=10)
bjsh1.grid(column=1,row=7,pady=1 ,sticky='W') 

xgmz1=Entry(monty, width=10)
xgmz1.grid(column=1,row=8,pady=1 ,sticky='W') 

xgdk1=Entry(monty, width=10)
xgdk1.grid(column=1,row=9,pady=1 ,sticky='W') 

yhxg1Var = StringVar()  
yhxg1 = ttk.Combobox(monty, textvariable=yhxg1Var, width=8)  
yhxg1["values"] = sg.soulList
yhxg1.grid(column=1,row=10,sticky='W')
 #第2个式神
Label(monty,width=10, text="式神2", relief='groove').grid(column=2, row=0, sticky='W') 

mz2Var = StringVar()  
mz2 = ttk.Combobox(monty, textvariable=mz2Var, width=8)  
mz2["values"] = sg.shikigamiNameList
mz2.grid(column=2,row=1,pady=1 ,sticky='W')
mz2.current(1)

gj2=Entry(monty, width=10)
gj2.grid(column=2,row=2,pady=1 ,sticky='W')

sm2=Entry(monty, width=10)
sm2.grid(column=2,row=3,pady=1 ,sticky='W')

fy2=Entry(monty, width=10)
fy2.grid(column=2,row=4,pady=1 ,sticky='W')

sd2=Entry(monty, width=10)
sd2.grid(column=2,row=5,pady=1 ,sticky='W')

bj2=Entry(monty, width=10)
bj2.grid(column=2,row=6,pady=1 ,sticky='W')

bjsh2=Entry(monty, width=10)
bjsh2.grid(column=2,row=7,pady=1 ,sticky='W') 

xgmz2=Entry(monty, width=10)
xgmz2.grid(column=2,row=8,pady=1 ,sticky='W') 

xgdk2=Entry(monty, width=10)
xgdk2.grid(column=2,row=9,pady=1 ,sticky='W') 

yhxg2Var = StringVar()  
yhxg2 = ttk.Combobox(monty, textvariable=yhxg2Var, width=8)  
yhxg2["values"] = sg.soulList
yhxg2.grid(column=2,row=10,sticky='W')

 #第3个式神
Label(monty,width=10, text="式神3", relief='groove').grid(column=3, row=0, sticky='W') 

mz3Var = StringVar()  
mz3 = ttk.Combobox(monty, textvariable=mz3Var, width=8)  
mz3["values"] = sg.shikigamiNameList
mz3.grid(column=3,row=1,pady=1 ,sticky='W')
mz3.current(3)

gj3=Entry(monty, width=10)
gj3.grid(column=3,row=2,pady=1 ,sticky='W')

sm3=Entry(monty, width=10)
sm3.grid(column=3,row=3,pady=1 ,sticky='W')

fy3=Entry(monty, width=10)
fy3.grid(column=3,row=4,pady=1 ,sticky='W')

sd3=Entry(monty, width=10)
sd3.grid(column=3,row=5,pady=1 ,sticky='W')

bj3=Entry(monty, width=10)
bj3.grid(column=3,row=6,pady=1 ,sticky='W')

bjsh3=Entry(monty, width=10)
bjsh3.grid(column=3,row=7,pady=1 ,sticky='W') 

xgmz3=Entry(monty, width=10)
xgmz3.grid(column=3,row=8,pady=1 ,sticky='W') 

xgdk3=Entry(monty, width=10)
xgdk3.grid(column=3,row=9,pady=1 ,sticky='W') 

yhxg3Var = StringVar()  
yhxg3 = ttk.Combobox(monty, textvariable=yhxg3Var, width=8)  
yhxg3["values"] = sg.soulList
yhxg3.grid(column=3,row=10,sticky='W')

 #第4个式神
Label(monty,width=10, text="式神4", relief='groove').grid(column=4, row=0, sticky='W') 

mz4Var = StringVar()  
mz4 = ttk.Combobox(monty, textvariable=mz4Var, width=8)  
mz4["values"] = sg.shikigamiNameList
mz4.grid(column=4,row=1,pady=1 ,sticky='W')
mz4.current(4)

gj4=Entry(monty, width=10)
gj4.grid(column=4,row=2,pady=1 ,sticky='W')

sm4=Entry(monty, width=10)
sm4.grid(column=4,row=3,pady=1 ,sticky='W')

fy4=Entry(monty, width=10)
fy4.grid(column=4,row=4,pady=1 ,sticky='W')

sd4=Entry(monty, width=10)
sd4.grid(column=4,row=5,pady=1 ,sticky='W')

bj4=Entry(monty, width=10)
bj4.grid(column=4,row=6,pady=1 ,sticky='W')

bjsh4=Entry(monty, width=10)
bjsh4.grid(column=4,row=7,pady=1 ,sticky='W') 

xgmz4=Entry(monty, width=10)
xgmz4.grid(column=4,row=8,pady=1 ,sticky='W') 

xgdk4=Entry(monty, width=10)
xgdk4.grid(column=4,row=9,pady=1 ,sticky='W') 

yhxg4Var = StringVar()  
yhxg4 = ttk.Combobox(monty, textvariable=yhxg4Var, width=8)  
yhxg4["values"] = sg.soulList
yhxg4.grid(column=4,row=10,sticky='W')

 #弟5个式神
Label(monty,width=10, text="式神5", relief='groove').grid(column=5, row=0, sticky='W') 

mz5Var = StringVar()  
mz5 = ttk.Combobox(monty, textvariable=mz5Var, width=8)  
mz5["values"] = sg.shikigamiNameList
mz5.grid(column=5,row=1,pady=1 ,sticky='W')
mz5.current(5)

gj5=Entry(monty, width=10)
gj5.grid(column=5,row=2,pady=1 ,sticky='W')

sm5=Entry(monty, width=10)
sm5.grid(column=5,row=3,pady=1 ,sticky='W')

fy5=Entry(monty, width=10)
fy5.grid(column=5,row=4,pady=1 ,sticky='W')

sd5=Entry(monty, width=10)
sd5.grid(column=5,row=5,pady=1 ,sticky='W')

bj5=Entry(monty, width=10)
bj5.grid(column=5,row=6,pady=1 ,sticky='W')

bjsh5=Entry(monty, width=10)
bjsh5.grid(column=5,row=7,pady=1 ,sticky='W') 

xgmz5=Entry(monty, width=10)
xgmz5.grid(column=5,row=8,pady=1 ,sticky='W') 

xgdk5=Entry(monty, width=10)
xgdk5.grid(column=5,row=9,pady=1 ,sticky='W') 

yhxg5Var = StringVar()  
yhxg5 = ttk.Combobox(monty, textvariable=yhxg5Var, width=8)  
yhxg5["values"] = sg.soulList
yhxg5.grid(column=5,row=10,sticky='W')

#tab3    
monty2 = ttk.LabelFrame(tab3, text='红方', width=80, height=250)  
monty2.grid(column=0, row=0, padx=0, pady=10) 
Label(monty2,width=10, text="", relief='groove').grid(column=0, row=0, sticky='W')  
Label(monty2,width=10, text="式神", relief='groove').grid(column=0, row=1, sticky='W')  
Label(monty2,width=10, text="攻击", relief='groove').grid(column=0, row=2, sticky='W')
Label(monty2,width=10, text="生命", relief='groove').grid(column=0, row=3, sticky='W')
Label(monty2,width=10, text="防御", relief='groove').grid(column=0, row=4, sticky='W')
Label(monty2,width=10, text="速度", relief='groove').grid(column=0, row=5, sticky='W')
Label(monty2,width=10, text="暴击", relief='groove').grid(column=0, row=6, sticky='W')
Label(monty2,width=10, text="暴击伤害", relief='groove').grid(column=0, row=7, sticky='W')
Label(monty2,width=10, text="效果命中", relief='groove').grid(column=0, row=8, sticky='W')
Label(monty2,width=10, text="效果抵抗", relief='groove').grid(column=0, row=9, sticky='W')
Label(monty2,width=10, text="御魂效果", relief='groove').grid(column=0, row=10, sticky='W')

 #第1个式神
Label(monty2,width=10, text="式神1", relief='groove').grid(column=1, row=0, sticky='W') 

mz21Var = StringVar()  
mz21 = ttk.Combobox(monty2, textvariable=mz21Var, width=8)  
mz21["values"] = sg.shikigamiNameList
mz21.grid(column=1,row=1,pady=1 ,sticky='W')
mz21.current(6)

gj21=Entry(monty2, width=10)
gj21.grid(column=1,row=2,pady=1 ,sticky='W')

sm21=Entry(monty2, width=10)
sm21.grid(column=1,row=3,pady=1 ,sticky='W')

fy21=Entry(monty2, width=10)
fy21.grid(column=1,row=4,pady=1 ,sticky='W')

sd21=Entry(monty2, width=10)
sd21.grid(column=1,row=5,pady=1 ,sticky='W')

bj21=Entry(monty2, width=10)
bj21.grid(column=1,row=6,pady=1 ,sticky='W')

bjsh21=Entry(monty2, width=10)
bjsh21.grid(column=1,row=7,pady=1 ,sticky='W') 

xgmz21=Entry(monty2, width=10)
xgmz21.grid(column=1,row=8,pady=1 ,sticky='W') 

xgdk21=Entry(monty2, width=10)
xgdk21.grid(column=1,row=9,pady=1 ,sticky='W') 

yhxg21Var = StringVar()  
yhxg21 = ttk.Combobox(monty2, textvariable=yhxg21Var, width=8)  
yhxg21["values"] = sg.soulList
yhxg21.grid(column=1,row=10,sticky='W')


 #第2个式神
Label(monty2,width=10, text="式神2", relief='groove').grid(column=2, row=0, sticky='W') 

mz22Var = StringVar()  
mz22 = ttk.Combobox(monty2, textvariable=mz22Var, width=8)  
mz22["values"] = sg.shikigamiNameList
mz22.grid(column=2,row=1,pady=1 ,sticky='W')
mz22.current(7)

gj22=Entry(monty2, width=10)
gj22.grid(column=2,row=2,pady=1 ,sticky='W')

sm22=Entry(monty2, width=10)
sm22.grid(column=2,row=3,pady=1 ,sticky='W')

fy22=Entry(monty2, width=10)
fy22.grid(column=2,row=4,pady=1 ,sticky='W')

sd22=Entry(monty2, width=10)
sd22.grid(column=2,row=5,pady=1 ,sticky='W')

bj22=Entry(monty2, width=10)
bj22.grid(column=2,row=6,pady=1 ,sticky='W')

bjsh22=Entry(monty2, width=10)
bjsh22.grid(column=2,row=7,pady=1 ,sticky='W') 

xgmz22=Entry(monty2, width=10)
xgmz22.grid(column=2,row=8,pady=1 ,sticky='W') 

xgdk22=Entry(monty2, width=10)
xgdk22.grid(column=2,row=9,pady=1 ,sticky='W') 

yhxg22Var = StringVar()  
yhxg22 = ttk.Combobox(monty2, textvariable=yhxg22Var, width=8)  
yhxg22["values"] = sg.soulList
yhxg22.grid(column=2,row=10,sticky='W')

 #第3个式神
Label(monty2,width=10, text="式神3", relief='groove').grid(column=3, row=0, sticky='W') 

mz23Var = StringVar()  
mz23 = ttk.Combobox(monty2, textvariable=mz23Var, width=8)  
mz23["values"] = sg.shikigamiNameList
mz23.grid(column=3,row=1,pady=1 ,sticky='W')
mz23.current(8)

gj23=Entry(monty2, width=10)
gj23.grid(column=3,row=2,pady=1 ,sticky='W')

sm23=Entry(monty2, width=10)
sm23.grid(column=3,row=3,pady=1 ,sticky='W')

fy23=Entry(monty2, width=10)
fy23.grid(column=3,row=4,pady=1 ,sticky='W')

sd23=Entry(monty2, width=10)
sd23.grid(column=3,row=5,pady=1 ,sticky='W')

bj23=Entry(monty2, width=10)
bj23.grid(column=3,row=6,pady=1 ,sticky='W')

bjsh23=Entry(monty2, width=10)
bjsh23.grid(column=3,row=7,pady=1 ,sticky='W') 

xgmz23=Entry(monty2, width=10)
xgmz23.grid(column=3,row=8,pady=1 ,sticky='W') 

xgdk23=Entry(monty2, width=10)
xgdk23.grid(column=3,row=9,pady=1 ,sticky='W') 

yhxg23Var = StringVar()  
yhxg23 = ttk.Combobox(monty2, textvariable=yhxg23Var, width=8)  
yhxg23["values"] = sg.soulList
yhxg23.grid(column=3,row=10,sticky='W')

 #第4个式神
Label(monty2,width=10, text="式神4", relief='groove').grid(column=4, row=0, sticky='W') 

mz24Var = StringVar()  
mz24 = ttk.Combobox(monty2, textvariable=mz24Var, width=8)  
mz24["values"] = sg.shikigamiNameList
mz24.grid(column=4,row=1,pady=1 ,sticky='W')
mz24.current(9)

gj24=Entry(monty2, width=10)
gj24.grid(column=4,row=2,pady=1 ,sticky='W')

sm24=Entry(monty2, width=10)
sm24.grid(column=4,row=3,pady=1 ,sticky='W')

fy24=Entry(monty2, width=10)
fy24.grid(column=4,row=4,pady=1 ,sticky='W')

sd24=Entry(monty2, width=10)
sd24.grid(column=4,row=5,pady=1 ,sticky='W')

bj24=Entry(monty2, width=10)
bj24.grid(column=4,row=6,pady=1 ,sticky='W')

bjsh24=Entry(monty2, width=10)
bjsh24.grid(column=4,row=7,pady=1 ,sticky='W') 

xgmz24=Entry(monty2, width=10)
xgmz24.grid(column=4,row=8,pady=1 ,sticky='W') 

xgdk24=Entry(monty2, width=10)
xgdk24.grid(column=4,row=9,pady=1 ,sticky='W') 

yhxg24Var = StringVar()  
yhxg24 = ttk.Combobox(monty2, textvariable=yhxg24Var, width=8)  
yhxg24["values"] = sg.soulList
yhxg24.grid(column=4,row=10,sticky='W')

 #弟5个式神
Label(monty2,width=10, text="式神5", relief='groove').grid(column=5, row=0, sticky='W') 

mz25Var = StringVar()  
mz25 = ttk.Combobox(monty2, textvariable=mz25Var, width=8)  
mz25["values"] = sg.shikigamiNameList
mz25.grid(column=5,row=1,pady=1 ,sticky='W')
mz25.current(10)

gj25=Entry(monty2, width=10)
gj25.grid(column=5,row=2,pady=1 ,sticky='W')

sm25=Entry(monty2, width=10)
sm25.grid(column=5,row=3,pady=1 ,sticky='W')

fy25=Entry(monty2, width=10)
fy25.grid(column=5,row=4,pady=1 ,sticky='W')

sd25=Entry(monty2, width=10)
sd25.grid(column=5,row=5,pady=1 ,sticky='W')

bj25=Entry(monty2, width=10)
bj25.grid(column=5,row=6,pady=1 ,sticky='W')

bjsh25=Entry(monty2, width=10)
bjsh25.grid(column=5,row=7,pady=1 ,sticky='W') 

xgmz25=Entry(monty2, width=10)
xgmz25.grid(column=5,row=8,pady=1 ,sticky='W') 

xgdk25=Entry(monty2, width=10)
xgdk25.grid(column=5,row=9,pady=1 ,sticky='W') 

yhxg25Var = StringVar()  
yhxg25 = ttk.Combobox(monty2, textvariable=yhxg25Var, width=8)  
yhxg25["values"] = sg.soulList
yhxg25.grid(column=5,row=10,sticky='W')
#填写默认值
gj1.insert(0,3000)
gj2.insert(0,3000)
gj3.insert(0,3000)
gj4.insert(0,3000)
gj5.insert(0,3000)
gj21.insert(0,3000)
gj22.insert(0,3000)
gj23.insert(0,3000)
gj24.insert(0,3000)
gj25.insert(0,3000)

fy1.insert(0,500)
fy2.insert(0,500)
fy3.insert(0,500)
fy4.insert(0,500)
fy5.insert(0,500)
fy21.insert(0,500)
fy22.insert(0,500)
fy23.insert(0,500)
fy24.insert(0,500)
fy25.insert(0,500)

sm1.insert(0,10000)
sm2.insert(0,10000)
sm3.insert(0,10000)
sm4.insert(0,10000)
sm5.insert(0,10000)
sm21.insert(0,10000)
sm22.insert(0,10000)
sm23.insert(0,10000)
sm24.insert(0,10000)
sm25.insert(0,10000)

sd1.insert(0,120)
sd2.insert(0,120)
sd3.insert(0,120)
sd4.insert(0,120)
sd5.insert(0,120)
sd21.insert(0,120)
sd22.insert(0,120)
sd23.insert(0,120)
sd24.insert(0,120)
sd25.insert(0,120)

bjsh1.insert(0,'150%')
bjsh2.insert(0,'150%')
bjsh3.insert(0,'150%')
bjsh4.insert(0,'150%')
bjsh5.insert(0,'150%')
bjsh21.insert(0,'150%')
bjsh22.insert(0,'150%')
bjsh23.insert(0,'150%')
bjsh24.insert(0,'150%')
bjsh25.insert(0,'150%')

xgdk1.insert(0,'40%')
xgdk2.insert(0,'40%')
xgdk3.insert(0,'40%')
xgdk4.insert(0,'40%')
xgdk5.insert(0,'40%')
xgdk21.insert(0,'40%')
xgdk22.insert(0,'40%')
xgdk23.insert(0,'40%')
xgdk24.insert(0,'40%')
xgdk25.insert(0,'40%')

xgmz1.insert(0,'40%')
xgmz2.insert(0,'40%')
xgmz3.insert(0,'40%')
xgmz4.insert(0,'40%')
xgmz5.insert(0,'40%')
xgmz21.insert(0,'40%')
xgmz22.insert(0,'40%')
xgmz23.insert(0,'40%')
xgmz24.insert(0,'40%')
xgmz25.insert(0,'40%')

bj1.insert(0,'40%')
bj2.insert(0,'40%')
bj3.insert(0,'40%')
bj4.insert(0,'40%')
bj5.insert(0,'40%')
bj21.insert(0,'40%')
bj22.insert(0,'40%')
bj23.insert(0,'40%')
bj24.insert(0,'40%')
bj25.insert(0,'40%')

yhxg1.current(22)
yhxg2.current(22)
yhxg3.current(22)
yhxg4.current(22)
yhxg5.current(22)
yhxg21.current(22)
yhxg22.current(22)
yhxg23.current(22)
yhxg24.current(22)
yhxg25.current(22)
# Add menu items


menuBar = Menu(root)  
root.config(menu=menuBar)
  
fileMenu = Menu(menuBar, tearoff=0,relief='raised')  

fileMenu.add_command(label="快捷保存", command=fastSaveTeam)  
fileMenu.add_command(label="快捷读取", command=fastReadTeam)    
fileMenu.add_separator()  

fileMenu.add_command(label="保存阵容", command=saveTeam)
fileMenu.add_command(label="另存为阵容", command=saveAsTeam)
fileMenu.add_command(label="读取阵容", command=readTeam)
fileMenu.add_separator()  

fileMenu.add_command(label="退出")  

menuBar.add_cascade(label="文件", menu=fileMenu)

anotherMenu = Menu(menuBar, tearoff=0,relief='raised')
anotherMenu.add_command(label="新建")  
anotherMenu.add_command(label="退出")  
menuBar.add_cascade(label="设置", menu=anotherMenu)
#data process

mzx=[mz1,mz2,mz3,mz4,mz5,mz21,mz22,mz23,mz24,mz25]
gjx=[gj1,gj2,gj3,gj4,gj5,gj21,gj22,gj23,gj24,gj25]
smx=[sm1,sm2,sm3,sm4,sm5,sm21,sm22,sm23,sm24,sm25]
fyx=[fy1,fy2,fy3,fy4,fy5,fy21,fy22,fy23,fy24,fy25]
sdx=[sd1,sd2,sd3,sd4,sd5,sd21,sd22,sd23,sd24,sd25]
bjx=[bj1,bj2,bj3,bj4,bj5,bj21,bj22,bj23,bj24,bj25]
bjshx=[bjsh1,bjsh2,bjsh3,bjsh4,bjsh5,bjsh21,bjsh22,bjsh23,bjsh24,bjsh25]
xhmzx=[xgmz1,xgmz2,xgmz3,xgmz4,xgmz5,xgmz21,xgmz22,xgmz23,xgmz24,xgmz25]
mgdkx=[xgdk1,xgdk2,xgdk3,xgdk4,xgdk5,xgdk21,xgdk22,xgdk23,xgdk24,xgdk25]
yhxgx=[yhxg1,yhxg2,yhxg3,yhxg4,yhxg5,yhxg21,yhxg22,yhxg23,yhxg24,yhxg25]
teamInfo=[mzx,gjx,smx,fyx,sdx,bjx,bjshx,xhmzx,mgdkx,yhxgx]

root.mainloop()
