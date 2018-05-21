#!/usr/bin/python 
# -*- coding: utf-8 -*-

from random import sample
from random import random
from random import randint
from math import ceil
from math import floor
from copy import deepcopy
from time import sleep

def my_print(data,s):
    data['log'].append(s)

def isFriend(i,j,d=None):
    if i.team==j.team:
        return True
    if d:
        temp=0
        for buff,buffInfo in d.buff.items():
            if '混乱' in buffInfo.keys():
                temp=1
                break
        if temp:
            return True
        return False

def isEnemy(i,j,d=None):
    if i==j:
        return False
    if i.team!=j.team:
        return True
    if d:
        temp=0
        for buff,buffInfo in i.buff.items():
            if '混乱' in buffInfo.keys():
                temp=1
                break
        if temp:
            return True
        return False

def gainOrb(who,n,data,mark=0):
    data['orb'][who.team]+=n
    if data['orb'][who.team]>8:
        data['orb'][who.team]=8
    if data['orb'][who.team]<0:
        data['orb'][who.team]=0
    if data['mode']==0:
        if n>0:
            my_print(data,'%d队获得%d点鬼火，现在鬼火数为%d'%(who.team+1,n,data['orb'][who.team]))
        else:
            my_print(data,'%d队失去%d点鬼火，现在鬼火数为%d'%(who.team+1,-n,data['orb'][who.team]))
    if not mark and n<0:
        b={'结算':-2,  #回合后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':1,
                                   '隐藏':0,
                                   }
        gainBuff(who,'用了鬼火',b,data)

                

def gainExtraTurn(who,data):
    data['action'].remove(who)
    who.po=1
    data['action'].append(who)
    data['extra'].append(who)
    if data['mode']==0:
        my_print(data,"%s获得额外的回合"%who.name)

def resisted(r,giver,data):
    if data['mode']==0:
        my_print(data,r.name+'触发了抵抗')
    if r.type=='奴良陆生':
        r.sk2b(giver,data)
    if r.soul=='骰子鬼' and canUseSoul(r,data) :
        if data['mode']==0:
            my_print(data,r.name+'触发了御魂骰子鬼')
        tempFlag='骰子鬼'
        toList=[]
        for i in data['uands']:
            if i.alive==1 and isEnemy(r,i,r):
                toList.append(i)
        if toList:
            to=sample(toList,1)[0]
            data['反击'].append({'to':to,
                            'from':r,
                            'flag':tempFlag
                            })


def hpChange(changer,num,data,flag=None,label=None):
    if changer.soul=='镇墓兽' and canUseSoul(d['from'],data) :
        temp=num
        if num<-changer.hp:
            temp=changer.hp
        if num>changer.maxhp-changer.hp:
            temp=changer.maxhp-changer.hp
        changer.critDamage-=temp/changer.maxhp*0.6
        if data['mode']==0:
            my_print(data,"%s触发了御魂镇墓兽"%changer.name)
            my_print(data,"%s的暴伤现在为%.0f%%"%(changer.name,changer.critDamage*100))

    if changer.type=='兵俑':
        changer.sk2(data)
    
    if changer.type=='彼岸花':
        changer.sk2b(data)
    
    if '天平' in changer.buff.keys():
        for i in data['units']:
            if i.type=='卖药郎' and i.alive:
                i.sk2b(changer,data)
                break
    changer.hp+=num
    if changer.hp>changer.maxhp:
        changer.hp=changer.maxhp
    if changer.hp<=0:
        if flag:
            die(changer,flag,data)
    if data['mode']==0:
        if num>0:
            my_print(data,"%s回复生命%.0f，现在生命为%.0f"%(changer.name,num,changer.hp))
        elif num<0:
            my_print(data,"%s损失生命%.0f，现在生命为%.0f"%(changer.name,-num,changer.hp))
    if data['mode']==-1:
        data['animation'].hpChange.append([changer,num,label])
def dispel(to,n,frm,data,flag='驱散'):            
    if to.team!=frm.team:
        temp=[]
        for buff,buffInfo in to.buff.items():
            if buffInfo['驱散']==1 and buffInfo['有益']==1:
                temp.append(buff)
        temp.reverse()
        while temp and n!=0:
            n-=1
            tbuff=temp[-1]
            if '层数' in to.buff[tbuff].keys():
                if data['mode']==0:
                    my_print(data,frm.name+flag+'了'+to.name+'的一层'+tbuff)
                to.buff[tbuff]['层数']-=1
                if '限制驱散' in to.buff[tbuff].keys():
                    temp.pop()
                if to.buff[tbuff]['层数']==0:
                    temp.pop()
 
                    removeBuff(to,tbuff,data)
            else:
                temp.pop()
                if data['mode']==0:
                    my_print(data,frm.name+flag+'了'+to.name+'的'+tbuff+'buff')
                removeBuff(to,tbuff,data)
    else:
        temp=[]
        for buff,buffInfo in to.buff.items():
            if buffInfo['驱散']==1 and buffInfo['有益']==-1:
                temp.append(buff)
        while temp and n!=0:
            n-=1
            tbuff=temp.pop()
            if data['mode']==0:
                my_print(data,frm.name+flag+'了'+to.name+'的'+tbuff+'buff')
            removeBuff(to,tbuff,data)

############################################
"""
d字典里面，to是对象，from是来源，td是真实伤害，df是防御，flag是标志
"""
############################################

def die(to,d,data):  #处理死亡
    summonFlag=0
    if to in data['summons']:
        summonFlag=1
        data['summons'][to.team]=None
        data['uands'].remove(to)
    if to in data['summonsSpecial']:
        summonFlag=1
        data['summonsSpecial'][data['summonsSpecial'].index(to)]=None
        data['uands'].remove(to)
    if to.alive==1:
        data['action'].remove(to)  #从行动条里移除
    溢出=-to.hp
    to.hp=0
    if to.alive==0:
        return
    to.alive=0
    if data['mode']==0:
        my_print(data,"%s死亡"%to.name)

    if to.type=='骨女':
        to.sk2b(data)
#判定游戏结束
    if summonFlag==0 and data['win']==0:  #只有在前面没有判定出某方游戏胜利时才判定
        win=1
        for key,unit in data['teams'][to.team].items(): #遍历所有死者队伍里的队友是否都死亡以判定对方胜利
            if unit.alive==1:
                win=0
                break
        if win==1:
            data['win']=abs(1-(to.team))+1
            
    #白色小鬼爆炸
    if to.type=='白色小鬼':
        to.sk2(data)
    #棺材复活
    if to.type=='棺材' and d=='棺材自杀':
        to.sk2(data)
    #阎魔召唤白色小鬼
    if not summonFlag:
        for i in data['units']:
            if i.team!=to.team and i.alive and i.type=='阎魔':
                i.sk2b(to,data)
                break
    #正常死亡的时候
    if isinstance(d,dict):
        #阴摩罗
        if d['from'].soul=="阴摩罗" and canUseSoul(d['from'],data) :
            if data['mode']==0:
                my_print(data,"%s触发了御魂阴摩罗"%d['from'].name)
            gainOrb(d['from'],3,data,1)
        #伤魂鸟
        if d['from'].soul=="伤魂鸟" and canUseSoul(d['from'],data) :
            if data['mode']==0:
                my_print(data,"%s触发了御魂伤魂鸟"%d['from'].name)
            b={'结算':-1,  #回合后结算
                                       '回合':1,
                                       '驱散':1,
                                       '有益':1,
                                       '攻击':0.15,
                                       '覆盖':['伤魂鸟·加攻']
                                       }
            hpChange(d['from'],d['from'].maxhp*0.15,data)
            gainBuff(d['from'],'伤魂鸟·加攻',b,data)        
        #红叶红枫娃娃爆炸
        if '红枫娃娃' in to.buff.keys():
            to.buff['红枫娃娃']['from'].sk2(data)
        #妖刀大招转火
        if '杀戮' in d['flag'] and d['times']>0:
            temp=d['to']
            for i in data['uands']:
                if i.alive==1 and isFriend(i,d['to'],d['from']) and i!=d['to']:
                    if temp==d['to']:
                        temp=i
                    else:
                        if temp.hp>i.hp:
                            temp=i
            if temp!=d['to']:
                if data['mode']==0:
                    my_print(data,"%s转火%s"%(d['from'].name,temp.name))
                d['times']+=2
                d['to']=temp
            else:
                d['flag'].append('break')

        #茨木伤害溢出
        if ('黑焰' in d['flag'] or '地狱之手' in d['flag']) and summonFlag==0 :
            if data['mode']==0:
                my_print(data,"%s触发了迁怒"%(d['from'].name))
            for i in data['uands']:
                if i.alive==1 and isFriend(i,d['to'],d['from']):
                    d['from'].sk2(i,溢出,data)
        #天罚aoe
        if '天罚' in d['flag'] and summonFlag==0 and 'aoe' not in d['flag']:
            if data['mode']==0:
                my_print(data,"%s天罚变成了AOE"%(d['from'].name))
            d['flag'].append('aoe')
        #玉藻前追击
        
        if '堕天' in d['flag'] and  '玉藻前追击' not in d['flag']:
            if data['mode']==0:
                my_print(data,"%s触发堕天追击"%(d['from'].name))
            temp=[]
            for i in data['uands']:
                if i.alive==1 and isFriend(i,to,d['from']):
                    temp.append(i)
            if temp:
                tg=sample(temp,1)[0]
                data['反击'].append({'to':tg,
                                    'from':d['from'],
                                    'flag':'堕天追击'
                                    })
                d['flag'].append('玉藻前追击')

        if '狐火' in d['flag'] and '玉藻前追击' not in d['flag']:
            if data['mode']==0:
                my_print(data,"%s触发狐火追击"%(d['from'].name))
            temp=[]
            for i in data['uands']:
                if i.alive==1 and isFriend(i,to,d['from']):
                    temp.append(i)
            if temp:
                tg=sample(temp,1)[0]
                data['反击'].append({'to':tg,
                                 'from':d['from'],
                                 'flag':'狐火追击'
                                 })
                d['flag'].append('玉藻前追击')
        #鬼使黑追击
        if '惩戒' in d['flag'] or '死亡宣判' in d['flag'] and canUsePassive(d['from'],data):
            gainExtraTurn(d['from'],data)
        #黑童子追击
        if '连斩' in d['flag']:
            tempFlag='连斩追击'
            check=1
            for i in data['反击']:
                if i['flag']==tempFlag:
                    check=0
                    break
            if check:
                if data['mode']==0:
                    my_print(data,'%s触发了连斩追击'%(d['from'].name))
                temp=[]
                for i in data['uands']:
                    if i.alive==1 and isFriend(i,to,d['from']):
                        temp.append(i)
                if temp:
                    tg=sample(temp,1)[0]
                    data['反击'].append({'to':tg,
                                     'from':d['from'],
                                     'flag':tempFlag,
                                     'td':d['td']*0.6
                                    })

        #白狼自拉条
        if '无我' in d['flag']:
            d['from'].po+=0.6
            if i.po>1:
               i.po=1
            data['action'].sort(key=lambda x:(x.po,x.sp,-x.id))
        #跳跳哥哥反击
        temp=0
        for i in data['units']:
            if i.alive and i.team==to.team and i.type=='跳跳哥哥':
                if data['mode']==0:
                    my_print(data,'%s触发了不弃反击'%(d['from'].name))
                data['反击'].append({'to':d['from'],
                                     'from':i,
                                     'flag':'不弃反击',})    
def damage(d,data):
    if not d['to']:
        return
    if 'times' not in d.keys():
        d['times']=1
    
    #先判定是否触发薙魂
    if 'aoe' not in d['flag'] and '特殊aoe' not in d['flag'] and '针女' not in d['flag'] and '分摊' not in d['flag']:
        tempFlag='已判定过薙魂'
        for thunit in data['units']:
            if tempFlag not in d['from'].buff.keys() and thunit.soul=='薙魂' and canUseSoul(thunit,data)  and thunit.alive==1 and thunit!=d['to'] and thunit.team==d['to'].team:
                b={'结算':-4,  #行动后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':0,
                                   '隐藏':1,
                                
                            }
                gainBuff(d['from'],tempFlag,b,data)
                if random()<0.5:
                    if data['mode']==0:
                        my_print(data,'%s触发了御魂%s'%(thunit.name,thunit.soul))
                    d['flag'].append('薙魂')
                break
    if 'aoe' not in d['flag'] and '特殊aoe' not in d['flag'] and '针女' not in d['flag'] and '分摊' not in d['flag']:
        tempFlag='已判定过金鱼挡刀'
        for thunit in data['summons']:
            if tempFlag not in d['from'].buff.keys() and thunit and canUsePassive(thunit,data)  and thunit.alive and thunit!=d['to'] and thunit.team==d['to'].team and thunit.type=='金鱼':
                b={'结算':-4,  #行动后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':0,
                                   '隐藏':1,
                                
                            }
                gainBuff(d['from'],tempFlag,b,data)
                if random()<0.5:
                    if data['mode']==0:
                        my_print(data,'%s触发了挡刀'%(thunit.name))
                    d['flag'].append('金鱼挡刀')
                break            
    if '普攻' in d['flag'] and '协战' not in d['flag'] and '多段分割' not in d['flag']:
        for i in data['uands']:
            if i.team==d['from'].team and i.alive and i.type in ('荒','姑获鸟','以津真天','番茄'):
                i.co_attack(d['to'],data)
    
    times=d['times']
    while d['times']!=0:
        d['times']-=1
        tempTarget=[]
        if 'aoe' in d['flag']:
            for unit in data['uands']:
                if unit.alive==1 and isFriend(d['to'],unit,d['from']):
                    tempTarget.append(unit)
        else:
            tempTarget.append(d['to'])
        if data['mode']==-1:
            data['animation'].atk=1
            data['animation'].atkf=d['from']
            data['animation'].atkt=tempTarget
            while data['animation'].atk:
                sleep(0.1)
        
        totalFlag=[]
        for to in tempTarget:    
            
                
            flag=[]
            #通用伤害值计算属性设置
            波动=1+random()/50-0.01
            防御=to.df
            大宝剑增伤=1+0.15*data['swords']
            造成伤害增加=1
            造成伤害减少=1
            受到伤害增加=1
            受到伤害减少=1
            增伤系数=1
            

            #计算buff增伤减伤
            for buff,buffInfo in to.buff.items():
                if '受到伤害增加' in buffInfo.keys():
                    受到伤害增加+=buffInfo['受到伤害增加']
                if '受到伤害减少' in buffInfo.keys():
                    受到伤害减少+=buffInfo['受到伤害减少']
                if '天罚' in buffInfo.keys():
                    增伤系数*=0.75
                if '鹿角冲撞' in buffInfo.keys():
                    增伤系数*=0.6
                if '心剑乱舞' in buffInfo.keys():
                    增伤系数*=0.5
            for buff,buffInfo in d['from'].buff.items():
                if '造成伤害增加' in buffInfo.keys():
                    造成伤害增加+=buffInfo['造成伤害增加']
                if '造成伤害减少' in buffInfo.keys():
                    造成伤害减少+=buffInfo['造成伤害减少']
               
                    
            #凤凰火普攻触发被动
            if '凤火' in d['flag']:
                d['from'].sk2(to,d,data)

            #骰子鬼增伤
            if '骰子鬼' in d['flag']:
                d['flag'].append('反击')
                造成伤害增加+=0.5


            #被服减伤
            if to.soul=='被服' and canUseSoul(to,data) :
                if data['mode']==0:
                        my_print(data,'%s触发了御魂%s'%(to.name,to.soul))
                受到伤害减少+=1.3
            #烟烟罗减伤
            if to.type=='烟烟罗':
                if data['mode']==0:
                   my_print(data,'%s触发了扑朔迷离'%(to.name))
                增伤系数*=0.7
            #薙魂减伤
            if '薙魂' in d['flag']:
                受到伤害减少+=0.2

            #玉藻前觉醒
            if d['from'].type=='玉藻前' and '分摊' not in d['flag']:
                防御-=100
            #姑获鸟普攻
            if '伞剑' in d['flag']:
                防御*=0.8
            if '一步一息' in d['flag']:
                防御*=0.6
            #网切
            if d['from'].soul=='网切' and canUseSoul(d['from'],data) and '分摊' not in d['flag'] and random()<0.5:
                防御*=0.55
                if data['mode']==0:
                    my_print(data,"%s触发了御魂网切"%d['from'].name)                
                
            #分摊伤害不增伤不计算防御不波动
            if '分摊' in d['flag']:
                波动=1
                防御=0
                造成伤害增加=1
                造成伤害减少=1
                受到伤害增加=1
                受到伤害减少=1
                增伤系数=1
                大宝剑增伤=1
            
            #针女伤害只吃大宝剑增伤不计算防御不波动
            if '针女' in d['flag']:
                造成伤害增加=1
                造成伤害减少=1
                受到伤害增加=1
                受到伤害减少=1
                波动=1
                防御=0
                增伤系数=1
            


            #计算伤害    
            伤害=d['td']*300/(300+防御)*波动*增伤系数
            伤害*=大宝剑增伤*造成伤害增加*受到伤害增加/造成伤害减少/受到伤害减少

        
            #计算暴击
            if '针女' not in d['flag'] and '分摊' not in d['flag'] and damageCritJudge(to,d,data):
                伤害*=d['from'].critDamage
                d['flag'].append('暴击')
                flag.append('暴击')
                if '暴击' not in totalFlag:
                    totalFlag.append('暴击')
                    
            if data['mode']==0:
                temp=''
                if '暴击' in flag:
                    my_print(data,"%s触发了暴击"%(d['from'].name))
            
            
            #判定技能增伤
            #青坊主对召唤物伤害翻倍
            if '禅心' in d['flag'] and (to in data['summons'] or to in data['summonsSpecial']):
                增伤系数*=2
            #荒川技能增伤
            if d['from'].type=='荒川之主' and '暴击' in flag:
                增伤系数*=1.2
                d['from'].sk2(data)
            #雪童子技能增伤
            if d['from'].type=='雪童子' and '冰冻' in to.buff.keys() and '针女' not in d['flag']:
                增伤系数*=3
                if data['mode']==0:
                    my_print(data,'%s对%s触发了霜天之织·破冰'%(d['from'].name,to.name))
                removeBuff(to,'冰冻',data)
                totalFlag.append('霜天之织·破冰')
           #玉藻前技能增伤 
            if '狐火' in d['flag']:
                if to.hp>0.8:
                    增伤系数*=0.85
                if to.hp<0.5:
                    增伤系数*=1.15
            if '堕天' in d['flag']:
                if to.hp>0.8:
                    增伤系数*=1.15
                if to.hp<0.5:
                    增伤系数*=0.85
            #鬼使黑技能
            if '死亡宣判' in d['flag']:
                if to.hp>0.4:
                    增伤系数*=1.5
                else:
                    增伤系数*=0.5
            #妖刀姬连斩
            if d['from'].type=='妖刀姬' and '分摊' not in d['flag'] and '针女' not in d['flag']:
                增伤系数*=d['from'].sk2(伤害,d,data)/伤害
            #吸血姬被动
            if '血袭' in d['flag']:
                增伤系数*=d['from'].sk2(伤害,d,data)/伤害
            #山风被动
            if d['from'].type=='山风'and '分摊' not in d['flag'] and '针女' not in d['flag']:
                增伤系数*=1+0.5*(to.maxhp-to.hp)/to.maxhp
            #络新妇大招
            if '噬心食髓' in d['flag'] and to.sp>d['from'].sp:
                增伤系数*=1+0.25+(to.sp-d['from'].sp)//10*0.025
            #判官被动
            if d['from'].type=='判官' and '复活过' in to.buff.keys():
                增伤系数*=1.2
            
            #盾的结算
            if '药汤' in d['flag']:
                临时存储伤害=伤害
                伤害=2*伤害
            #一目盾
            temp=[]
            for buffName,buffInfo in to.buff.items():
                if buffName=='风符·护':
                    if buffInfo['盾']>=伤害:
                        buffInfo['盾']-=伤害
                        伤害=0
                        if data['mode']==0:
                            my_print(data,"未击破%s的盾"%(to.name))
                        break
                    else:
                        伤害-=buffInfo['盾']
                        temp.append(buffName)  
            for i in temp:
                if data['mode']==0:
                    my_print(data,"%s单盾爆炸"%(to.name))
                newd={'flag':['aoe','风符·护']}
                newd['to']=d['from']
                newd['from']=to
                newd['td']=to.buff[i]['炸盾']
                damage(newd,data)
                removeBuff(to,i,data)
            #其他盾
            temp=[]
            for buffName,buffInfo in to.buff.items():
                if '盾' in buffInfo.keys():
                    if buffInfo['盾']>=伤害:
                        buffInfo['盾']-=伤害
                        伤害=0
                        if data['mode']==0:
                            my_print(data,"未击破%s的盾"%(to.name))
                        break
                    else:
                        伤害-=buffInfo['盾']
                        temp.append(buffName)  
            for i in temp:            
                removeBuff(to,i,data)

            if '药汤' in d['flag'] and 临时存储伤害<伤害:
                伤害=临时存储伤害
            #扣血
            if 伤害!=0:




                
                #心眼增伤
                if d['from'].soul=='心眼' and canUseSoul(d['from'],data) and to.hp<0.3*to.maxhp and '分摊' not in d['flag']:
                    伤害=伤害*1.5
                    if data['mode']==0:
                        my_print(data,'%s触发了御魂%s'%(d['from'].name,d['from'].soul))

                #破势增伤
                if d['from'].soul=='破势' and canUseSoul(d['from'],data) and (to.hp>0.7*to.maxhp or ('吞噬' in d['flag'] and d['from'].吞噬第一段触发御魂=='破势')) and '分摊' not in d['flag']:
                    伤害=伤害*1.4
                    if '吞噬' in d['flag']:
                        d['from'].吞噬第一段触发御魂='破势'
                    if data['mode']==0:
                        my_print(data,'%s触发了御魂%s'%(d['from'].name,d['from'].soul))

                #鸣屋增伤
                if d['from'].soul=='鸣屋' and canUseSoul(d['from'],data) and '分摊' not in d['flag']:
                    temp=0
                    for buff,buffInfo in to.buff.items():
                        if '眩晕' in buffInfo.keys():
                            temp=1
                            break
                    if temp:
                        伤害=伤害*1.3
                        if data['mode']==0:
                            my_print(data,'%s触发了御魂%s'%(d['from'].name,d['from'].soul))
                
                if '薙魂' in d['flag']:                   
                    newd={'flag':['分摊'],
                              'td':伤害/2,
                              'from':d['from'],
                              'to':thunit,
                    }
                    伤害/=2
                    damage(newd,data)
                if '金鱼挡刀' in d['flag']:                   
                    newd={'flag':['分摊'],
                              'td':伤害/2,
                              'from':d['from'],
                              'to':thunit,
                    }
                    伤害/=2
                    damage(newd,data)
                if '暴击' in flag:
                    label='暴击'
                else:
                    label=None
                hpChange(to,-伤害,data,label=label)
                



                #缩进3个tab，多段每一段对aoe单体生效，且需破盾
                #判定死亡
                if to.hp<=0:
                    if '回梦' in to.buff.keys():
                        removeBuff(to,'回梦',data)
                    else:
                        die(to,d,data)
                             #判定技能
                
                #狰
                tempFlag='狰'+to.name
                if '针女' in d['flag']:
                    tempFlag='针女狰'+to.name
                if '傀儡·追击' in d['flag']:
                   tempFlag='傀儡·追击狰'+to.name
                
                if to.soul=='狰' and canUseSoul(to,data) and random()<0.35 and '反击' not in d['flag'] and tempFlag not in d['from'].buff.keys():
                    if data['mode']==0:
                        my_print(data,'%s触发了御魂%s'%(to.name,to.soul))
                    data['反击'].append({'to':d['from'],
                                           'from':to,
                                           'flag':tempFlag
                            })
                    b={'结算':-4,  #行动后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':0,
                                   '隐藏':1,
                                
                            }
                    gainBuff(d['from'],tempFlag,b,data)  

                #陆生被动
                if to.type=='奴良陆生':
                    to.sk2(d,data)

                #镜姬
                if to.soul=='镜姬'and canUseSoul(to,data) and random()<0.3:
                    if data['mode']==0:
                        my_print(data,'%s触发了御魂%s'%(to.name,to.soul))
                    hpChange(d['from'],-伤害,data,'镜姬')
                #木魅
                for mmunit in data['units']:
                    tempFlag='木魅'+to.name
                    if  mmunit.alive==1 and mmunit.team==to.team and mmunit.soul=='木魅' and canUseSoul(mmunit,data)and tempFlag not in d['from'].buff.keys():
                        b={'结算':-4,  #行动后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':0,
                                   '隐藏':1,
                                
                            }
                        gainBuff(d['from'],tempFlag,b,data)    
                        if random()<0.25:
                            if data['mode']==0:
                                my_print(data,'%s触发了御魂%s'%(mmunit.name,mmunit.soul))
                            gainOrb(d['from'],-1,data,1)
                        
                #返魂香
                if to.soul=='返魂香'and canUseSoul(to,data):
                    tempFlag='返魂香'
                    if  to.alive==1 and tempFlag not in d['from'].buff.keys():
                        b={'结算':-4,  #行动后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':0,
                                   '隐藏':1,
                                
                            }
                        gainBuff(d['from'],tempFlag,b,data)
                        tempRandom=random()
                        if tempRandom<0.25*(1+to.hit):
                            if data['mode']==0:
                                my_print(data,'%s触发了御魂%s'%(to.name,to.soul))
                            if tempRandom<0.25*(1+to.hit)/(1+d['from'].resist):
                                b={'结算':-1,  #回合后结算
                                       '回合':1,
                                       '驱散':0,
                                       '有益':-1,
                                       '眩晕':1,
                                       '覆盖':['眩晕'],
                                       }
                                gainBuff(d['from'],'眩晕',b,data)
                    
                            else:
                                resisted(d['from'],to,data)
                

                #地藏像
                if to.soul=='地藏像'and canUseSoul(to,data)and '暴击' in flag:
                    if data['mode']==0:
                        my_print(data,'%s触发了御魂%s'%(to.name,to.soul))
                    盾值=to.maxhp*0.1
                    if random()<to.crit:
                        盾值*=to.critDamage
                    b={'结算':-1,  #回合后结算
                       '回合':1,
                       '驱散':1,
                       '有益':1,
                       '盾':盾值,
                       '覆盖':['地藏像'],
                        }
                    gainBuff(to,'地藏像',b,data)
                    for i in data['units']:
                        if i.alive==1 and i.team==to.team and random()<0.3 and i!=to:
                            盾值=to.maxhp*0.1
                            if random()<i.crit:
                                盾值*=i.critDamage
                            b={'结算':-1,  #回合后结算
                               '回合':1,
                               '驱散':1,
                               '有益':1,
                               '盾':盾值,
                               '覆盖':['地藏像'],
                                }
                            gainBuff(i,'地藏像',b,data)
            
                #针女
                if d['from'].soul=='针女'and canUseSoul(d['from'],data) and '暴击' in flag and random()<0.4 and '分摊' not in d['flag']:
                    newd={'flag':['针女'],
                       'from':d['from'],
                       'to':to,
                       'td':min(to.maxhp*0.1,d['from'].atk*1.2)
                       }
                    if data['mode']==0:
                        my_print(data,'%s触发了御魂针女'%(d['from'].name))
                    damage(newd,data)
                #傀儡师
                if d['from'].type=='傀儡师':
                    d['from'].sk2(to,d,data)
                #海坊主
                if d['from'].type=='海坊主':
                    d['from'].sk2(伤害,data)
                #钟灵
                if d['from'].soul=='钟灵'and canUseSoul(d['from'],data) and '分摊' not in d['flag']:
                    tempRandom=random()
                    if tempRandom<0.08*(1+d['from'].hit):
                        if data['mode']==0:
                            my_print(data,'%s触发了御魂%s'%(d['from'].name,d['from'].soul))
                        if tempRandom<0.08*(1+d['from'].hit)/(1+to.resist):
                            b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':-1,
                                   '眩晕':1,
                                   '覆盖':['眩晕'],
                                   }
                            gainBuff(to,'眩晕',b,data)
                
                        else:
                            resisted(to,d['from'],data)

                #雪幽魂
                if d['from'].soul=='雪幽魂'and canUseSoul(d['from'],data) and '分摊' not in d['flag']:
                    tempRandom=random()
                    if tempRandom<0.12*(1+d['from'].hit):
                        if data['mode']==0:
                            my_print(data,'%s触发了御魂%s'%(d['from'].name,d['from'].soul))
                        if tempRandom<0.12*(1+d['from'].hit)/(1+to.resist):
                            b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':-1,
                                   '冰冻':1,
                                   '覆盖':['冰冻'],
                                   }
                            gainBuff(to,'冰冻',b,data)
                
                        else:
                            resisted(to,d['from'],data)
                #媚妖
                if d['from'].soul=='媚妖'and canUseSoul(d['from'],data) and '分摊' not in d['flag']:
                    tempRandom=random()
                    if tempRandom<0.25*(1+d['from'].hit):
                        if data['mode']==0:
                            my_print(data,'%s触发了御魂%s'%(d['from'].name,d['from'].soul))
                        if tempRandom<0.25*(1+d['from'].hit)/(1+to.resist):
                            b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':-1,
                                   '混乱':1,
                                   '覆盖':['混乱'],
                                   }
                            gainBuff(to,'混乱',b,data)
                
                        else:
                            resisted(to,d['from'],data)
                #魍魉之匣
                if d['from'].soul=='魍魉之匣'and canUseSoul(d['from'],data) and '分摊' not in d['flag']:
                    tempRandom=random()
                    if tempRandom<0.25*(1+d['from'].hit):
                        if data['mode']==0:
                            my_print(data,'%s触发了御魂%s'%(d['from'].name,d['from'].soul))
                        if tempRandom<0.25*(1+d['from'].hit)/(1+to.resist):
                            temp=randint(1,4)
                            if temp==1:
                                b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':-1,
                                   '沉默':1,
                                   '覆盖':['沉默'],
                                   }
                                gainBuff(to,'沉默',b,data)
                            if temp==2:
                                b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':-1,
                                   '眩晕':1,
                                   '覆盖':['眩晕'],
                                   }
                                gainBuff(to,'眩晕',b,data)
                            if temp==3:
                                b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':-1,
                                   '混乱':1,
                                   '覆盖':['混乱'],
                                   }
                                gainBuff(to,'混乱',b,data)
                            if temp==4:
                                b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':-1,
                                   '减疗':0.5,
                                   '覆盖':['减疗'],
                                   }
                                gainBuff(to,'减疗',b,data)
                
                        else:
                            resisted(to,d['from'],data)
                #反枕
                if d['from'].soul=='反枕'and canUseSoul(d['from'],data) and '分摊' not in d['flag']:
                    tempRandom=random()
                    if tempRandom<0.23*(1+d['from'].hit):
                        if data['mode']==0:
                            my_print(data,'%s触发了御魂%s'%(d['from'].name,d['from'].soul))
                        if tempRandom<0.23*(1+d['from'].hit)/(1+to.resist):
                            b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':-1,
                                   '睡眠':1,
                                   '覆盖':['睡眠'],
                                   }
                            gainBuff(to,'睡眠',b,data)
                
                        else:
                            resisted(to,d['from'],data)
                #日女
                if d['from'].soul=='日女巳时' and canUseSoul(d['from'],data) and '分摊' not in d['flag']:
                    temp=0.3
                    for buff,buffInfo in to.buff.items():
                        if buffInfo['有益']==1:
                            temp=0.4
                            break
                    if random()<temp:
                        if data['mode']==0:
                            my_print(data,'%s触发了御魂%s'%(d['from'].name,d['from'].soul))
                        to.po-=0.3
                        data['action'].sort(key=lambda x:(x.po,x.sp,-x.id))
                        if to.po<0:
                            to.po=0
                        if data['mode']==0:
                            my_print(data,'%s目前在进度条的%.0f%%位置'%(to.name,to.po*100))


            #缩进2个tab，多段每一段对aoe单体生效，且不用破盾
            #匣中少女被动
            tempFlag='已触发溢彩'
            if to.type=='匣中少女' and tempFlag not in d['from'].buff.keys():
                to.sk2b(d['from'],data)
                b={'结算':-4,  #行动后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':0,
                                   '隐藏':1,
                                
                            }
                gainBuff(d['from'],tempFlag,b,data) 
            
            #荒大招减伤
            if '天罚' in d['flag']:
                for i in range(8):
                    tempFlag='天罚减伤'+str(i)
                    if tempFlag not in to.buff.keys():
                        break
                b={'结算':-4,  #行动后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':0,
                                   '隐藏':1,
                                   '天罚':0,
                            }
                gainBuff(to,tempFlag,b,data) 
            #犬神大招减伤
            if '心剑乱舞' in d['flag']:
                for i in range(5):
                    tempFlag='心剑乱舞减伤'+str(i)
                    if tempFlag not in to.buff.keys():
                        break
                b={'结算':-4,  #行动后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':0,
                                   '隐藏':1,
                                   '心剑乱舞':0,
                            }
                gainBuff(to,tempFlag,b,data)
            #犬神反击
            if '守护' in to.buff.keys():
                to.buff['守护']['守护'].sk2(d['from'],data)
            #万年竹反击
            if '竹叶守护' in to.buff.keys():
                to.buff['竹叶守护']['守护'].sk2(d['from'],to,data)
            #小小黑反击
            if to.type=='黑童子':
                to.sk2(d['from'],data)
            #犬神反击后加攻
            if '守护·反击' in d['flag']:
                d['from'].sk2b(to,data)
 
            #小鹿大招减伤、行动条、装晕人
            if '鹿角冲撞' in d['flag']:
                #减伤
                for i in range(3):
                    tempFlag='鹿角冲撞减伤'+str(i)
                    if tempFlag not in to.buff.keys():
                        break
                    b={'结算':-4,  #行动后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':0,
                                   '隐藏':1,
                                   '鹿角冲撞':0,
                            }
                    gainBuff(to,tempFlag,b,data)
                #行动条:
                d['from'].sk3c(to,data)
            #酒吞被动
            if to.type=='酒吞童子':
                to.sk2(2,data)
            #骨女被动
            if to.type=='骨女':
                to.sk2(data)
            #辉夜姬被动
            if to.type=='辉夜姬' and '已判定火鼠裘' not in d['from'].buff.keys():
                to.sk2(to,data)
                b={'结算':-4,  #行动后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':0,
                                   '隐藏':1,
                                
                            }
                gainBuff(d['from'],'已判定火鼠裘',b,data)   
            if '龙首之玉·加防加抗' in to.buff.keys() and '已判定火鼠裘' not in d['from'].buff.keys():
                for i in data['units']:
                    if '龙首之玉·幻境' in i.buff.keys() and i.team==to.team:
                        i.sk2(to,data)
                        b={'结算':-4,  #行动后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':0,
                                   '隐藏':1,
                                
                            }
                        gainBuff(d['from'],'已判定火鼠裘',b,data)   
                        break
            #惠比寿回火
            if to.type=='惠比寿':
                to.sk2(data)
            
            #山风撕裂
            if '斩' in d['flag']:
                d['from'].sk3b(to,data)
            #吸血姬大招
            if '鲜血之拥' in d['flag']:
                d['from'].sk3b(to,data)
            #鬼灯被动
            if d['from'].type=='鬼灯':
                d['from'].sk2(to,data)
            
            #雪童子被动
            if d['from'].type=='雪童子':
                d['from'].sk2(to,data)
            
            #凤凰火大招触发被动
            if '凤凰业火' in d['flag'] and '分摊' not in d['flag']:
                d['from'].sk2(to,d,data)
            
            #阎魔大招
            if '冤魂重压' in d['flag']:
                d['from'].sk3b(to,data)
                d['from'].sk2(to,data)
            
            
            
            #般若被动
            if '鬼袭' in d['flag'] or '鬼之假面' in d['flag']:
                d['from'].sk2(to,data)
            
            #凤凰火普攻触发偷暴击
            if '凤火' in d['flag']:
                d['from'].sk1b(to,data)
            #一目连普攻
            if '风符·破' in d['flag']:
                d['from'].sk1b(to,data)
            #雪女普攻
            if '雪球' in d['flag']:
                d['from'].sk1b(to,data)
            #雪女被动
            if to.type=='雪女':
                to.sk2b(d['from'],data)
            #雪女大招
            if '暴风雪' in d['flag']:
                d['from'].sk3c(to,data)
                d['from'].sk3b(to,data)
            #茨木普攻
            if '黑焰' in d['flag']:
                d['from'].sk1b(to,data)
            #金鱼姬普攻
            if '扇舞' in d['flag'] and data['summons'][d['from'].team] and data['summons'][d['from'].team].type=='金鱼':
                d['from'].sk1b(data['summons'][d['from'].team],data)
            #樱花妖大招
            if '樱吹雪' in d['flag']:
                d['from'].sk3b(to,data)
            #弈被动
            if '征子' in d['flag'] or '神之一手' in d['flag']:
                d['from'].sk2(to,data)
            #镰鼬普攻
            if '胖揍' in d['flag']:
                d['from'].sk1b(to,data)
            #追月普攻
            if '邀月' in d['flag']:
                d['from'].sk1b(data)
            #妖琴师大招
            if '疯魔琴心' in d['flag']:
                d['from'].sk3b(to,data)
                d['from'].sk3c(to,data)
            
            #妖狐被动
            if '风刃' in d['flag'] or '狂风刃卷' in d['flag']:
                d['from'].sk2(data)
            if d['from']=='夜叉':
                d['from'].sk2(data)
            #判官大招
            if '死亡宣告' in d['flag']:
                d['from'].sk3b(to,data)
            #跳哥反击
            if '不弃反击' in d['flag']:
                d['from'].sk1b(to,data)
            #红叶红枫娃娃
            if '死亡之舞' in d['flag'] or '红枫' in d['flag']:
                d['from'].sk1b(to,data)
            #孟婆
            if '汤盆冲撞' in d['flag']:
                d['from'].sk2b(to,data)                            
            if '天降之物' in d['flag']:
                d['from'].sk3b(to,data)                            
            if '天降之物·群体' in d['flag']:
                d['from'].sk3c(to,data)
                
            #鬼使白普攻
            if '活死人' in d['flag']:
                d['from'].sk1b(to,data)
            #鬼使白大招
            if '无常夺命' in d['flag']:
                d['from'].sk3b(to,data)
            #清姬毒
            if '蛇行击' in d['flag'] or '焚身之火' in d['flag']:
                d['from'].sk3b(to,data)  
            #卖药郎大招
            if '退魔' in d['flag'] and d['to'].alive:
                d['from'].sk3b(to,data) 
            #络新妇大招
            if '噬心食髓' in d['flag']:
                d['from'].sk3b(to,data)
            if '噬心食髓' in d['flag'] or '毒针' in d['flag']:
                d['from'].sk2(to,data)
            #御馔津普攻
            if '一矢·封魔' in d['flag']:
                 d['from'].sk1c(to,data)
            #小鹿男普攻
            if '森之力' in d['flag']:
                d['from'].sk1b(to,data)
                        
            #两面佛普攻
            if '风雷两生' in d['flag']:
                if random()<0.5:
                    d['from'].sk2(to,data)
                else:
                    d['from'].sk2b(to,data)

            #食梦貘普攻
            if '入眠' in d['flag']:
                d['from'].sk1b(d['to'],data)
            #玉藻前普攻
            if '灵击' in d['flag']:
                d['from'].sk1b(d['to'],data)
            #兵俑普攻
            if '挥斩' in d['flag']:
                d['from'].sk1b(d['to'],data)
            
            #睡眠打醒
            if '睡眠' in to.buff.keys() and '入眠' not in d['flag']:
                removeBuff(to,'睡眠',data)
            


            #蝠翼
            if d['from'].soul=='蝠翼' and canUsePassive(d['from'],data):
                hpChange(d['from'],伤害*0.2,data)
                if data['mode']==0:
                    my_print(data,"%s触发了御魂蝠翼"%d['from'].name)

            #吸血buff
            吸血=0
            for buff,buffInfo in d['from'].buff.items():
                if '吸血' in buffInfo.keys():
                    吸血+=buffInfo['吸血']
            if 吸血:
                hpChange(d['from'],伤害*吸血,data)


        #缩进1个tab，多段每一段对aoe整体生效                
        #凤凰火大招额外回合
        if '凤凰业火' in d['flag'] and '暴击' in totalFlag and random()<0.25:
            gainExtraTurn(d['from'],data)
        

        
        #青灯吸火
        if '吸魂灯' in d['flag'] or '幽光' in d['flag']:
            for _ in range(len(tempTarget)):
                if random()<0.3:
                    gainOrb(d['to'],-1,data,1)
                    gainOrb(d['from'],1,data,1)
            

        #对面全死光的时候中断多段技能
        if 'break' in d['flag']:
            break
        
    #多段完毕后结算
        #两面佛大招
    if '神罪连击' in d['flag']:
        d['from'].sk2(to,data)
        d['from'].sk2b(to,data)
        #花鸟普攻
    if '归鸟' in d['flag']:
        for i in range(times):
            tg=None
            to_select=[]
            for i in data['units']:
                if i.alive and d['from'].team==i.team:
                    to_select.append(i)
            to_select.sort(key=lambda x:x.hp/x.maxhp)
            if to_select and to_select[0].hp==to_select[0].maxhp:
                tg=sample(to_select,1)[0]
            elif to_select:
                tg=to_select[0] 
            if tg:
                d['from'].sk1b(tg,data) 
        #百目鬼被动
    for i in data['units']:
        if i.type=='百目鬼':
            if '暴击' in totalFlag and random()<0.8:
                i.sk2(data)
                
def heal(h,data):        
    flag=[]
    状态减疗=1
    for buff,buffInfo in h['to'].buff.items():
        if '减疗' in buffInfo.keys():
            状态减疗-=h['to'].buff[buff]['减疗']
    if 状态减疗<=0:
        状态减疗==0
    系统减疗=max(1-data['swords']*0.1,0.2)
    治疗量=h['heal']*系统减疗*状态减疗
    if h['from'].soul=='树妖'and canUsePassive(h['from'],data):
        治疗量*=1.2
        if data['mode']==0:
            my_print(data,'%s触发了御魂树妖'%(h['from']))
    if random()<h['from'].crit:
        治疗量*=h['from'].critDamage
        flag.append('暴击')
    if 治疗量==0:
        治疗量=1
    if data['mode']==-1:
        data['animation'].heal=1
        data['animation'].healf=h['from']
        data['animation'].healt=[h['to']]
        while data['animation'].heal:
            sleep(0.1)
        
    hpChange(h['to'],治疗量,data)
   
    #判定珍珠
    if h['from'].soul=='珍珠'and canUsePassive(h['from'],data):
        if data['mode']==0:
            my_print(data,'%s触发了御魂树妖'%(h['from']))
        盾值=治疗量*0.25
        b={'结算':-1,  #回合后结算
        '回合':1,
        '驱散':0,
        '有益':1,
        '盾':盾值,
        '覆盖':['珍珠'],
                }
        gainBuff(h['to'],'珍珠',b,data)
    #判定桃花的治疗暴击
    if "花之馨香" in h['flag'] and "暴击" in flag:
        for i in data['uands']:
            if i.alive==1 and i.team==h['to'].team and  i!=h['to']:
                newh={'flag':[]}
                newh['to']=i
                newh['from']=h['from']
                newh['heal']=治疗量*0.3
                heal(newh,data)
                
############################################
def removeBuff(tg,buff,data):
    if data['mode']==0 and '隐藏' not in tg.buff[buff].keys():
        temp=''.join(list(filter(lambda x:x not in '0123456789',buff)))
        if temp=='气合':
            tempbw='·黑'
            if tg.buff[buff]['气合']:
                tempbw='·白'
            temp+=tempbw
        my_print(data,"%s的%sbuff消失了"%(tg.name,temp))

    if buff=='回梦':
        if tg.hp<tg.buff[buff]['特殊']:
            tg.hp=tg.buff[buff]['特殊']
            if data['mode']==0:
                my_print(data,"%s触发回梦，生命回复到了%.0f"%(tg.name,tg.buff[buff]['特殊']))
    
    if buff=='龙首之玉·幻境':
        for i in data['uands']:
            if i.team==tg.team and '龙首之玉·加防加抗' in i.buff.keys():
                removeBuff(i,'龙首之玉·加防加抗',data)
    if buff=='清辉月华·幻境':
        for i in data['uands']:
            if i.team==tg.team and '月之祝福·加攻加速' in i.buff.keys():
                removeBuff(i,'月之祝福·加攻加速',data)
    if buff=='守护他人':
        for i in data['uands']:
            if i.team==tg.team and '守护' in i.buff.keys():
                removeBuff(i,'守护',data)
    if buff=='竹叶守护他人':
        my_print(data,'1')
        for i in data['uands']:
            if i.team==tg.team and '竹叶守护' in i.buff.keys():
                removeBuff(i,'竹叶守护',data)
    if buff=='狐狩界·幻境':
        for i in data['uands']:
            if i.team==tg.team: 
                if '狐狩界·加防加伤加速0' in i.buff.keys():
                    removeBuff(i,'狐狩界·加防加伤加速0',data)    
                if '狐狩界·加防加伤加速0' in i.buff.keys():
                    removeBuff(i,'狐狩界·加防加伤加速0',data)
                if '狐狩界·加防加伤加速0' in i.buff.keys():
                    removeBuff(i,'狐狩界·加防加伤加速0',data)                    
    if buff=='狂啸·吸血' and '狂气' in tg.buff.keys():
        removeBuff(tg,'狂气',data)

    for buffInfoName,buffInfoNum in tg.buff[buff].items():
        if '攻击' == buffInfoName:
            tg.atk-=tg.atki*buffInfoNum
            if data['mode']==0:
                my_print(data,"%s的攻击变为了%.0f"%(tg.name,tg.atk))
        if '防御' == buffInfoName:
            tg.df-=tg.dfi*buffInfoNum
            if data['mode']==0:
                my_print(data,"%s的防御变为了%.0f"%(tg.name,tg.df))
        if '速度' == buffInfoName:
            temp=1
            for ttbuff,ttbuffInfo in tg.buff.items():
                if '速度比' in ttbuffInfo.keys():
                    temp+=ttbuffInfo['速度比']
            tg.sp/=temp
            tg.sp-=buffInfoNum
            tg.sp*=temp
            if data['mode']==0:
                my_print(data,"%s的速度变为了%.0f"%(tg.name,tg.sp))
        if '速度比' == buffInfoName:
            temp=1
            for ttbuff,ttbuffInfo in tg.buff.items():
                if '速度比' in ttbuffInfo.keys():
                    temp+=ttbuffInfo['速度比']
            tg.sp/=temp
            temp-=buffInfoNum
            tg.sp*=temp
            if data['mode']==0:
                my_print(data,"%s的速度变为了%.0f"%(tg.name,tg.sp))
        if '命中' == buffInfoName:
            tg.hit-=buffInfoNum
            if data['mode']==0:
                my_print(data,"%s的命中变为了%.0f%%"%(tg.name,tg.hit*100))
        if '抵抗' == buffInfoName:
            tg.resist-=buffInfoNum
            if data['mode']==0:
                my_print(data,"%s的抵抗变为了%.0f%%"%(tg.name,tg.resist*100))
        if '暴伤' == buffInfoName:
            tg.critDamage-=buffInfoNum
            if data['mode']==0:
                my_print(data,"%s的暴伤变为了%.0f%%"%(tg.name,tg.critDamage*100))
        if '暴击' == buffInfoName:
            tg.crit-=buffInfoNum
            if data['mode']==0:
                my_print(data,"%s的暴击变为了%.0f%%"%(tg.name,tg.crit*100))
        if '特殊·兵俑' == buffInfoName:
            temp=1
            for i in data['units']:
                if i.alive==1 and i!=tg and '嘲讽' in i.buff.keys() and '特殊·兵俑' in i.buff['嘲讽'].keys():
                    temp=0
                    break
            if temp:
                removeBuff(buffInfoNum,'坚不可破·石化',data)
        if buffInfoName in ('眩晕','睡眠','冰冻','混乱','沉默','嘲讽','变形'):
            if tg.type=='山风':
                tg.sk2(data)
        if '撕裂' == buffInfoName:
            b={'结算':-1,  #回合后结算
                                           '回合':1,
                                           '驱散':1,
                                           '有益':-1,
                                           '减疗':1,
                                           '覆盖':['禁疗']
                                           }
        
            gainBuff(tg,'禁疗',b,data)
        if buffInfoName=='封印被动':
            if tg.type=='青坊主':
                temp=0

                for qfzBuff,qfzBuffInfo in tg.buff.items():
                    print(qfzBuffInfo.keys())
                    if '封印被动' in qfzBuffInfo.keys():
                        temp+=1
                print(temp==1)
                if temp==1:
                    tg.sk2(data,1)
                
    del tg.buff[buff]

#buff 结算类型:
#普通： 1回合前结算，-1经历过一个回合前阶段后回合后结算，0回合后结算，2行动前结算
#特殊： -2自己和其他人回合后结算 -3 不结算 -4自己和其他人行动后结算
def gainBuff(tg,buff,buffInfo,data):
    for buffInfoName,buffInfoNum in buffInfo.items():
        if buffInfoName=='有益' and buffInfoNum==-1 and '免异' in tg.buff.keys():
            if data['mode']==0:
                my_print(data,"免疫")
            return False

    for buffInfoName,buffInfoNum in buffInfo.items():
        if buffInfoName in ('眩晕','睡眠','冰冻','混乱','沉默','嘲讽','变形'):
            temp=[]
            for tbuff,tbuffInfo in tg.buff.items():
                if '免控' in tbuffInfo.keys():
                    tg.buff[tbuff]['免控']-=1
                    b={'结算':-4,  #其他人行动后结算
                       '回合':1,
                       '驱散':0,
                       '有益':0,
                       '隐藏':1,
                       '免控':-1,
                       }
                    gainBuff(tg,'触发过免控',b,data)
                    if data['mode']==0:
                        my_print(data,"%s因为%s而免疫了一次控制"%(tg.name,tbuff))
                    if tg.buff[tbuff]['免控']==0:
                        temp.append(tbuff)
                    break
            for i in temp:
                removeBuff(tg,i,data)
            if '触发过免控' in tg.buff.keys():    
                return False
            for i in data['units']:
                if i.type=='花鸟卷' and i.sk2(tg,data):
                    b={'结算':-4,  #其他人行动后结算
                       '回合':1,
                       '驱散':0,
                       '有益':0,
                       '隐藏':1,
                       '免控':-1,
                       }
                    gainBuff(tg,'触发过免控',b,data)
                    if data['mode']==0:
                        my_print(data,"%s因为%s的画境而免疫了一次控制"%(tg.name,i.name))
                    return False
            if tg.type=='小鹿男' and random()<0.2:
                tg.sk2b(buff,buffInfo,data)
                return False
        if buffInfoName in ('封印御魂','封印被动','冰冻'):
            temp=[]
            for tbuff,tbuffInfo in tg.buff.items():
                if '霜天之织' in tbuffInfo.keys():
                    tg.buff[tbuff]['霜天之织']-=1
                    b={'结算':-4,  #其他人行动后结算
                       '回合':1,
                       '驱散':0,
                       '有益':0,
                       '隐藏':1,
                       '免控':-1,
                       }
                    gainBuff(tg,'触发过霜天之织',b,data)
                    if data['mode']==0:
                        my_print(data,"%s因为%s而免疫了一次%s"%(tg.name,tbuff,buff))
                    if tg.buff[tbuff]['霜天之织']==0:
                        temp.append(tbuff)
                    break
            for i in temp:
                removeBuff(tg,i,data)
            if '触发过霜天之织' in tg.buff.keys():    
                return False
        

    #去除不可叠加的buff                        
    for buffInfoName,buffInfoNum in buffInfo.items():
        if '覆盖' == buffInfoName:
            for iBuff in buffInfoNum:
                if iBuff in tg.buff.keys():
                    removeBuff(tg,iBuff,data)

    #获得新buff
    if buff in tg.buff.keys():
        tg.buff[buff]['回合']+=buffInfo['回合']
        if data['mode']==0 and '隐藏' not in tg.buff[buff].keys():
            temp=''.join(list(filter(lambda x:x not in '0123456789',buff)))
            my_print(data,"%s的%sbuff延长至%d回合"%(tg.name,temp,tg.buff[buff]['回合']))
    else:
        tg.buff[buff]=buffInfo
        if data['mode']==0 and '隐藏' not in tg.buff[buff].keys():
            temp=''.join(list(filter(lambda x:x not in '0123456789',buff)))
            if temp=='气合':
                tempbw='·黑'
                if buffInfo['气合']:
                    tempbw='·白'
                temp+=tempbw
            my_print(data,"%s获得了%sbuff"%(tg.name,temp))
        for buffInfoName,buffInfoNum in buffInfo.items():                
            if '攻击' == buffInfoName:
                tg.atk+=tg.atki*buffInfoNum
                if data['mode']==0:
                    my_print(data,"%s的攻击变为了%.0f"%(tg.name,tg.atk))
            if '防御' == buffInfoName:
                tg.df+=tg.dfi*buffInfoNum
                if data['mode']==0:
                    my_print(data,"%s的防御变为了%.0f"%(tg.name,tg.df))
            if '速度' == buffInfoName:
                temp=1
                for ttbuff,ttbuffInfo in tg.buff.items():
                    if '速度比' in ttbuffInfo.keys():
                        temp+=ttbuffInfo['速度比']
                tg.sp/=temp
                tg.sp+=buffInfoNum
                tg.sp*=temp
                if data['mode']==0:
                    my_print(data,"%s的速度变为了%.0f"%(tg.name,tg.sp))
            if '速度比' == buffInfoName:
                temp=1
                for ttbuff,ttbuffInfo in tg.buff.items():
                    if '速度比' in ttbuffInfo.keys() and ttbuff!=buff:
                        temp+=ttbuffInfo['速度比']
                tg.sp/=temp
                temp+=buffInfoNum
                tg.sp*=temp
                if data['mode']==0:
                    my_print(data,"%s的速度变为了%.0f"%(tg.name,tg.sp))
            if '命中' == buffInfoName:
                tg.hit+=buffInfoNum
                if data['mode']==0:
                    my_print(data,"%s的命中变为了%.0f%%"%(tg.name,tg.hit*100))
            if '抵抗' == buffInfoName:
                tg.resist+=buffInfoNum
                if data['mode']==0:
                    my_print(data,"%s的抵抗变为了%.0f%%"%(tg.name,tg.resist*100))
            if '暴伤' == buffInfoName:
                tg.critDamage+=buffInfoNum
                if data['mode']==0:
                    my_print(data,"%s的暴伤变为了%.0f%%"%(tg.name,tg.critDamage*100))
            if '暴击' == buffInfoName:
                tg.crit+=buffInfoNum
                if data['mode']==0:
                    my_print(data,"%s的暴击变为了%.0f%%"%(tg.name,tg.crit*100))

    #食梦貘沉睡
    if buff=='睡眠':
        for i in data['units']:
            if i.alive==1 and i.type=='食梦貘':
                i.sk2(data)

    #三味
    for buffInfoName,buffInfoNum in buffInfo.items():
        if buffInfoName in ('眩晕','睡眠','冰冻','混乱','沉默','变形'): 
            for i in range(len(data['units'])):
                temp="三味·加速"+str(i)
                unit=data['units'][i]
                if unit.alive==1 and unit.team==tg.team and unit.soul=='三味' and canUseSoul(unit,data)and temp not in tg.buff.keys():
                    if data['mode']==0:
                        my_print(data,unit.name+'触发了御魂三味')
                    b={'结算':-1,  #回合后结算
                                           '回合':1,
                                           '驱散':0,
                                           '有益':1,
                                           '速度':30,
                                           '覆盖':[temp]
                                           }
                    gainBuff(tg,temp,b,data)
            for i,unit in enumerate(data['units']):
                if unit.alive and unit.team==tg.team and unit.type=='青坊主' and canUsePassive(unit,data):
                    unit.sk2(data)
        if buffInfoName=='封印被动':
            if tg.type=='青坊主':
                temp=0
                for qfzBuff,qfzBuffInfo in tg.buff.items():
                    if '封印被动' in qfzBuffInfo.keys():
                        temp+=1
                if temp==1:
                    for i,unit in enumerate(data['units']):
                        if unit.alive and unit.team==tg.team:
                            removeBuff(unit,'佛光',data)
    
    return True

    


############################################
############################################
def showBuff(toMove,data):
    temp=[]
    if data['swords']:
        temp.append('大宝剑·%d层'%(data['swords']))
    for buff,buffInfo in toMove.buff.items():
        if data['debug']==0:
            buffShowName=''.join(list(filter(lambda x:x not in '0123456789',buff)))
            if '隐藏' in buffInfo.keys():
                continue
            if '气合' in buffInfo.keys():
                tempbw='黑'
                if buffInfo['气合']:
                    tempbw='白'
                buffShowName='气合·'+tempbw
        else:
            buffShowName=buff
        
        if '层数' in buffInfo.keys():    
            temp.append('%s·%d层'%(buffShowName,toMove.buff[buff]['层数']))
        else:
            temp.append(buffShowName)
    if not temp:
        temp.append('无')
    return temp

def newTurn(data,flag=None):
        toMove=data['action'][-1]
        if data['mode']==-1:
            data['animation'].turn=toMove
        if data['mode']==0:
            my_print(data,'*Buff*  '+'||'.join(showBuff(toMove,data)))
        if data['mode']==0:
            #my_print(data,data['units'])
            my_print(data,'%s的回合'%toMove.name)
#        if toMove.team!=-1:
#            my_print(data,'→'.join([i.name for i in data['action'][::-1]]))
            
#行动条动一下

        for i in range(len(data['action'])):
            data['action'][i].po+=(1-toMove.po)/toMove.sp*data['action'][i].sp
            if data['action'][i].po>=1:
               data['action'][i].po=1 
        data['action'][-1].po=0
        data['action'].sort(key=lambda x:(x.po,x.sp,-x.id))

#回合前
        turnStartCheck(toMove,data)

#式神行动
        if canMove(toMove,data):
            move(toMove,data)

#回合后
        turnOverCheck(toMove,data)
    


#下次行动判定
    #如果有多个式神同时到终点    
        if data['action'][-1].po==1:
            if data['mode']==0:       
                my_print(data,'*Buff*  '+'||'.join(showBuff(toMove,data))+'\n'+'-'*20)
        else:
    #如果没有多个式神同时到终点
            data['action'].sort(key=lambda x:(-((1-x.po)/x.sp),x.sp,-x.id))
            if data['mode']==0:
                my_print(data,'*Buff*  '+'||'.join(showBuff(toMove,data))+'\n'+'-'*20)
        if data['mode']==-1:
            data['animation'].action=None

############################################
############################################

def gameStartCheck(data):
  
    flag=[]
    for i in data['units']:
        if i.type=='辉夜姬':
            actionStartCheck(i,data)
            i.sk2b(data)
            actionOverCheck(i,data)
        if i.type=='追月神':
            actionStartCheck(i,data)
            i.sk2b(data)
            actionOverCheck(i,data)
        if i.type=='犬神':
            i.sk2c(data)
        if i.type=='青坊主':
            i.sk2(data)
        if i.type=='二口女':
            i.sk2b(data)
        if i.type=='跳跳哥哥':
            temp='不弃'
            b={'结算':-1,  #回合后结算
                                   '回合':-1,
                                   '驱散':0,
                                   '有益':1,
                                   '抵抗':0.4,
                                   '隐藏':1
                                   }

            gainBuff(i,temp,b,data)
        if i.type=='大天狗':
            i.sk2(data)
        if i.type=='酒吞童子':
            temp='减伤·觉醒'
            b={'结算':-1,  #回合后结算
                                   '回合':-1,
                                   '驱散':0,
                                   '有益':0,
                                   '受到伤害减少':0.1,
                                   '隐藏':1
                                   }

            gainBuff(i,temp,b,data)
        if i.type in ('两面佛','姑获鸟'):
            temp='增伤·觉醒'
            b={'结算':-1,  #回合后结算
                                   '回合':-1,
                                   '驱散':0,
                                   '有益':0,
                                   '造成伤害增加':0.1,
                                   '隐藏':1
                                   }

            gainBuff(i,temp,b,data)
                        
        if '火灵' not in flag and i.soul=='火灵':
            if data['mode']==0:
                my_print(data,'%s触发了御魂%s'%(i.name,i.soul))
            gainOrb(i,3,data,1)
            flag.append('火灵')
        if '蚌精' not in flag and i.soul=='蚌精':
            if data['mode']==0:
                my_print(data,'%s触发了御魂%s'%(i.name,i.soul))
            盾值=i.maxhp*0.1
            if random()<i.crit:
                盾值*=i.critDamage
            flag.append('蚌精')
            for j in data['units']:
                if j.team==i.team:
                    盾值=i.maxhp*0.1
                    if random()<i.crit:
                        盾值*=i.critDamage
                    b={'结算':-1,  #回合后结算
                    '回合':1,
                    '驱散':0,
                    '有益':1,
                    '盾':盾值,
                    '覆盖':['蚌精'],
                    }
                    gainBuff(j,'蚌精',b,data)
    if data['mode']==0:
        my_print(data,'--------------------')

    



def actionStartCheck(toMove,data):
    #惠比寿鲤鱼旗治疗
    for i in data['summons']:
        if i and i.type=='鲤鱼旗' and i!=toMove and i.team==toMove.team:
            if data['mode']==0:
                my_print(data,'%s触发了鲤鱼旗治疗'%toMove.name)
            i.sk2(toMove,data)
    #花鸟后续治疗
    if '芬芳' in toMove.buff.keys():
        if data['mode']==0:
            my_print(data,'%s触发了芬芳'%toMove.name)
        h={'flag':['芬芳']}
        h['to']=toMove
        h['from']=toMove.buff['芬芳']['来源']
        h['heal']=toMove.buff['芬芳']['来源'].maxhp*toMove.buff['芬芳']['hot']
        toMove.buff['芬芳']['hot']=0.1
        heal(h,data)
    if canUseSoul(toMove,data) and toMove.soul=='招财猫' and random()<0.5:
        if data['mode']==0:
            my_print(data,'%s触发了御魂%s'%(toMove.name,toMove.soul))
        gainOrb(toMove,2,data,1)

def actionOverCheck(toMove,data):
    #去除各种不重复计算的标记
    for unit in data['uands']:
        
        temp=[]
        for buff,buffData in unit.buff.items():
            if  buffData['结算']==-4:
                buffData['回合']-=1
                temp.append(buff)
        for i in temp:
            if unit.buff[i]['回合']==0:
                removeBuff(unit,i,data)
    #花鸟用完鸟
    for i in data['units']:
        if i.alive==1 and i.type=='花鸟卷' and i.birds==0:
            if data['mode']==0:
                my_print(data,'%s因为用完飞鸟而获得一只'%(i.name))
            i.changeBirds(1,data)
            
    #御馔津射箭判定
    for i in data['units']:
        if i.alive and i.team!=toMove.team and i.type=='御馔津' and '已打出一矢·封魔' not in i.buff.keys():
            if '狐狩界·幻境' in i.buff.keys():
                temp=0.4
            else:
                temp=0.05
            if random()<temp:
                tempFlag='已打出一矢·封魔'
                data['反击'].append({'to':toMove,
                                           'from':i,
                                           'flag':'一矢·封魔',
                            })
                b={'结算':-4,  #行动后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':0,
                                   '隐藏':1,
                                
                            }
                gainBuff(i,tempFlag,b,data)
    #金鱼计数
    for i in data['summons']:
        if i and i.alive and i.team!=toMove.team and i.type=='金鱼':
            i.计数+=1
            if i.计数==8:
                i.计数=0
                data['反击'].append({'to':toMove,
                                           'from':i,
                                           'flag':"金鱼反击",
                            })
    #卖药郎看破                
    for i in data['units']:
        if i.alive==1 and i.team!=toMove.team:
            if i.type=='卖药郎':
                i.sk2b(toMove,data)  
                break
    #卖药郎观察                
    for i in data['units']:
        if i.alive==1 and i.team!=toMove.team:
            if i.type=='卖药郎':
                i.sk2(toMove,data)  
                break
    #匣子的盾                
    for i in data['units']:
        if i.alive==1 and i.team==toMove.team:
            if i.type=='匣中少女':
                i.sk2(toMove,data)
    #雪女的盾
    if toMove.type=='雪女':
        toMove.sk2(data)

    #酒吞狂气
    if toMove.type=='酒吞童子':
        toMove.sk2(1,data)
    
    #小鹿男变身buff
    if toMove.type=='小鹿男':
        toMove.sk3b(data)

    #花鸟画卷
    if toMove.type=='花鸟卷':
        toMove.sk2b(data)

def 邪光(self,frm,data):
    gainOrb(self,-3,data)
    if data['mode']==0:
        my_print(data,"%s使用了邪光"%(self.name))
        
    d={'flag':['邪光']}
    d['to']=self
    d['from']=frm
    d['td']=frm.atk*2.11*1.15
    damage(d,data)
    for i in data['uands']:
        if i.team==self.team and i.alive and '凝视' in i.buff.keys():
            removeBuff(i,'凝视',data)
    
        
def move(toMove,data):
    if data['mode']==-1:
        data['animation'].action=toMove
    
    if toMove.team==-1:
        toMove.move(data)
        return

    actionStartCheck(toMove,data)
    
    if canMove(toMove,data):    
        if '凝视' in toMove.buff.keys() and canUseOrb(toMove,3,data) and canUseSkill(toMove,data):
            邪光(toMove,toMove.buff['凝视']['from'],data)    
        else:
            toMove.move(data)

    actionOverCheck(toMove,data)
    if data['mode']==-1:
        data['animation'].action=None
    


def turnOverCheck(toMove,data):
    if toMove.team==-1:
        return
    if data['orbPo'][toMove.team]==5:
        data['orbPo'][toMove.team]=0
        data['orb'][toMove.team]+=data['getOrb'][toMove.team]
        if data['orb'][toMove.team]>8:
            data['orb'][toMove.team]=8
        if data['mode']==0:
            my_print(data,'%d队获得%d点系统回火，现在鬼火数为%d'%(toMove.team+1,data['getOrb'][toMove.team],data['orb'][toMove.team]))
        if data['getOrb'][toMove.team]!=5:
            data['getOrb'][toMove.team]+=1
    
    if '追月·幻境·加攻加速' in toMove.buff.keys():
        data['orbPo'][toMove.team]+=1
    
    if data['orbPo'][toMove.team]==5:
        data['orbPo'][toMove.team]=0
        data['orb'][toMove.team]+=data['getOrb'][toMove.team]
        if data['orb'][toMove.team]>8:
            data['orb'][toMove.team]=8
        if data['mode']==0:
            my_print(data,'%d队获得%d点系统回火，现在鬼火数为%d'%(toMove.team+1,data['getOrb'][toMove.team],data['orb'][toMove.team]))
        if data['getOrb'][toMove.team]!=5:
            data['getOrb'][toMove.team]+=1
    
    #樱花被动
    for i in data['units']:
        if i.alive==1 and i.team==toMove.team:
            if i.type=='樱花妖':
                i.sk2(toMove,data)

    
    #撕裂伤害
    if '撕裂' in toMove.buff.keys():
        if data['mode']==0:
            my_print(data,'%s受到%s的撕裂伤害'%(toMove.name,toMove.buff['撕裂']['撕裂'].name))
        d={'flag':['dot','撕裂'],
        'from':toMove.buff['撕裂']['撕裂'],
        'to':toMove,
        'td':min(toMove.buff['撕裂']['撕裂'].atk*1.2,toMove.hp*0.1+toMove.buff['撕裂']['撕裂'].atk*0.36),
        }
        damage(d,data)
        
    if '用了鬼火' in toMove.buff.keys():     
        for i in data['units']:
            if i.type=='小鹿男' and i.alive and i.team!=toMove.team:
                i.sk2(data)
        if '蜘蛛印记' in toMove.buff.keys():
            toMove.buff['蜘蛛印记']['from'].sk2b(toMove,data)
    else:
        temp=[]
        for i in range(4):
            tempName='气合'+str(i)
            if '气合'+str(i) in toMove.buff.keys():
                temp.append(tempName)
        if temp:
            tempBuff=sample(temp,1)[0]
            removeBuff(toMove,tempBuff,data)
 
    #结算toMove的状态
    temp=[]
    for buff,buffData in toMove.buff.items():
        if  buffData['结算']==0:
            buffData['回合']-=1
            temp.append(buff)
    for i in temp:
        if i in toMove.buff.keys() and toMove.buff[i]['回合']==0:
            removeBuff(toMove,i,data)

    #结算全体的状态
    for unit in data['uands']:
        temp=[]
        for buff,buffData in unit.buff.items():
            if  buffData['结算']==-2:
                buffData['回合']-=1
                temp.append(buff)
        for i in temp:
            if unit.buff[i]['回合']==0:
                removeBuff(unit,i,data)
    #青坊主失去一层佛光
    if toMove.type=='青坊主':
        toMove.佛光-=1
        if toMove.佛光<1:
            toMove.佛光=1
    #犬神被动
    if toMove.type=='犬神':
        toMove.sk2c(data)
    #万年竹被动    
    if toMove.type=='万年竹':
        toMove.sk2b(data)
    #大天狗的钢铁之羽
    if toMove.type=='大天狗':
        toMove.sk2(data)
    #白狼冥想
    if toMove.type=='白狼':
        toMove.sk2(data)
    #追月免控
    if toMove.type=='追月神':
        toMove.sk2(data)
    #雪童子的霜天之织
    if toMove.type=='雪童子':
        toMove.sk2b(data)                 
    #涅槃之火
    if toMove.soul=='涅槃之火'and canUsePassive(toMove,data) and toMove.hp<0.3*toMove.maxhp:
        if data['mode']==0:
            my_print(data,'%s触发了御魂%s'%(toMove.name,toMove.soul))
        hpChange(toMove,toMove.maxhp*0.15,data)
    
    #轮入道
    if toMove.soul=='轮入道' and canUsePassive(toMove,data) and '轮入道' not in toMove.buff.keys():
        if random()<0.2:
            if data['mode']==0:
                my_print(data,'%s触发了御魂%s'%(toMove.name,toMove.soul))
            gainExtraTurn(toMove,data)
            b={'结算':-2,  #回合后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':1,
                                   '隐藏':0,
                                   }
            gainBuff(toMove,'轮入道',b,data)
    
    while data['反击']:
        f=data['反击'].pop()
 
        if f['flag']=='堕天追击':
            if data['mode']==0:
                my_print(data,'%s进行追击'%(f['from'].name))
            if f['to'].alive==0:
                temp=[]
                for fjunit in data['uands']:
                    if isFriend(fjunit,f['to'],f['from']) and fjunit.alive==1:
                        temp.append(fjunit)
                if temp:
                    f['to']=sample(temp,1)[0]
            actionStartCheck(f['from'],data)        
            f['from'].sk2b(f['to'],data)
            actionOverCheck(f['from'],data)
        elif f['flag']=='狐火追击':
            if data['mode']==0:
                my_print(data,'%s进行追击'%(f['from'].name))
            if f['to'].alive==0:
                temp=[]
                for fjunit in data['uands']:
                    if isFriend(fjunit,f['to'],f['from']) and fjunit.alive==1:
                        temp.append(fjunit)
                if temp:
                    f['to']=sample(temp,1)[0]
            actionStartCheck(f['from'],data)        
            f['from'].sk3b(f['to'],data)
            actionOverCheck(f['from'],data)
        elif f['flag']=='一矢·封魔':
            if data['mode']==0:
                my_print(data,'%s进行反击'%(f['from'].name))
            if f['to'].alive==0:
                temp=[]
                for fjunit in data['uands']:
                    if isFriend(fjunit,f['to'],f['from']) and fjunit.alive==1:
                        temp.append(fjunit)
                if temp:
                    f['to']=sample(temp,1)[0]    
            actionStartCheck(f['from'],data)        
            f['from'].sk1b(f['to'],data)
            actionOverCheck(f['from'],data)
        elif f['flag']=='魂之怒火':
            if data['mode']==0:
                my_print(data,'%s进行连斩反击'%(f['from'].name))
            if f['to'].alive==0:
                temp=[]
                for fjunit in data['uands']:
                    if isFriend(fjunit,f['to'],f['from']) and fjunit.alive==1:
                        temp.append(fjunit)
                if temp:
                    f['to']=sample(temp,1)[0]    
            actionStartCheck(f['from'],data)        
            f['from'].sk3b(f['to'],data)
            actionOverCheck(f['from'],data)   
        elif f['flag']=='连斩追击':
            if data['mode']==0:
                my_print(data,'%s进行追击'%(f['from'].name))
            if f['to'].alive==0:
                temp=[]
                for fjunit in data['uands']:
                    if isFriend(fjunit,f['to'],f['from']) and fjunit.alive==1:
                        temp.append(fjunit)
                if temp:
                    f['to']=sample(temp,1)[0]    
            actionStartCheck(f['from'],data)        
            f['from'].sk3b(f['to'],data,td=f['td'])
            actionOverCheck(f['from'],data)   
        else:
            if data['mode']==0:
                my_print(data,'%s进行反击'%(f['from'].name))
            tempFlag='反击'
            if f['flag']=='骰子鬼':
                tempFlag='骰子鬼'
            if f['flag']=='守护·反击':
                tempFlag='守护·反击'
            if f['flag']=='不弃反击':
                tempFlag='不弃反击'
            if f['to'].alive==0:
                temp=[]
                for fjunit in data['uands']:
                    if isFriend(fjunit,f['to'],f['from']) and fjunit.alive==1:
                        temp.append(fjunit)
                if temp:
                    f['to']=sample(temp,1)[0]
                    
            actionStartCheck(f['from'],data)        
            f['from'].sk1(f['to'],data,tempFlag)
            actionOverCheck(f['from'],data)
    #百目鬼被动
    for i in data['units']:
        if i.type=='百目鬼':
            i.sk2b(data)
        
def turnStartCheck(toMove,data):
	
    if toMove.team==-1:
        return
    
    #系统鬼火条
    if toMove not in data['extra']:
        if toMove not in data['summons'] and toMove not in data['summonsSpecial']:
            data['orbPo'][toMove.team]+=1
            if data['mode']==0:
                my_print(data,'%d队目前鬼火%d个，鬼火条位于%d格'%(toMove.team+1,data['orb'][toMove.team],data['orbPo'][toMove.team]))
        data['extra']=[]
    else:
        data['extra'].remove(toMove)
    
    #辉夜姬主动回火
    if '龙首之玉·加防加抗' in toMove.buff.keys() and random()<0.67:
        if data['mode']==0:
            my_print(data,'%s触发了龙首之玉幻境的回火'%(toMove.name))
        gainOrb(toMove,1,data)
        


    #青灯被动
    for i in data['units']:
        if i.type=='青行灯':
            i.sk2(toMove,data)
    #二口女被动
    for i in data['units']:
        if i.alive and i.type=='二口女' and i.team==toMove.team:
            i.sk2(data)
    #天狗增伤buff
    if toMove.type=='大天狗':
        toMove.sk2b(data)
    #白狼冥想
    if toMove.type=='白狼':
        toMove.sk2b(data)
    
    #清状态
    temp=[]
    for buff,buffData in toMove.buff.items():
        if  buffData['结算']==1:
            buffData['回合']-=1
            temp.append(buff)
        if  buffData['结算']==-1:
            buffData['结算']=0
    for i in temp:
        if i in toMove.buff.keys() and toMove.buff[i]['回合']==0:
            removeBuff(toMove,i,data)

    #荒开幻境
    if toMove.type=='荒':
        toMove.sk2(data)
    
    #小白毒伤害
    for i in range(3):
        tempName='无常夺命·毒'+str(i)
        if tempName in toMove.buff.keys():
            if data['mode']==0:
                my_print(data,'%s受到%s的无常夺命·毒伤害'%(toMove.name,toMove.buff[tempName]['毒'].name))
            d={'flag':['dot','无常夺命·毒'],
            'from':toMove.buff[tempName]['毒'],
            'to':toMove,
            'td':toMove.buff[tempName]['毒'].atk*0.53,
            }
            damage(d,data)
    #清姬毒伤害
    for i in range(3):
        tempName='焚身之火·毒'+str(i)
        if tempName in toMove.buff.keys():
            if data['mode']==0:
                my_print(data,'%s受到%s的焚身之火·毒伤害'%(toMove.name,toMove.buff[tempName]['毒'].name))
            d={'flag':['dot','焚身之火·毒'],
            'from':toMove.buff[tempName]['毒'],
            'to':toMove,
            'td':toMove.buff[tempName]['毒'].atk*0.32,
            }
            damage(d,data)
    #判官dot伤害
    if '死亡宣告·爆炸' in toMove.buff.keys():
        if random()<0.5*(1+toMove.buff['死亡宣告·爆炸']['from'].hit):
            if data['mode']==0:
                my_print(data,'%s受到%s的死亡宣告·爆炸伤害'%(toMove.name,toMove.buff['死亡宣告·爆炸']['from'].name))
            d={'flag':['dot','死亡宣告·爆炸'],
                'from':toMove.buff['死亡宣告·爆炸']['from'],
                'to':toMove,
                'td':toMove.buff['死亡宣告·爆炸']['from'].atk*1.58,
                }
            damage(d,data)
    #吸血姬毒伤害
    if '鲜血之拥·毒' in toMove.buff.keys():
        if data['mode']==0:
            my_print(data,'%s受到鲜血之拥·毒伤害'%(toMove.name,toMove.buff['鲜血之拥·毒']['毒'].name))
        d={'flag':['dot','鲜血之拥·毒'],
            'from':toMove.buff['鲜血之拥·毒']['毒'],
            'to':toMove,
            'td':toMove.hp*0.05,
            }
        damage(d,data)    
    #彼岸花造成伤害
    for i in data['units']:
        if i.alive and i.team!=toMove.team and i.type=='彼岸花':
            i.sk2(toMove,data)
            break
    #白色小鬼爆炸
    if toMove.type=='白色小鬼':
        toMove.sk1(data)
    #棺材死亡
    if toMove.type=='棺材':
        toMove.sk1(data)


def canMove(toMove,data,show=1):
    if toMove.team==-1:
        return True
    for buff,buffData in toMove.buff.items():
        if '眩晕' in buffData.keys():
            if data['mode']==0 and show:
                my_print(data,"%s被眩晕，无法行动"%(toMove.name))
            return False
        if '冰冻' in buffData.keys():
            if data['mode']==0 and show:
                my_print(data,"%s被冰冻，无法行动"%(toMove.name))
            return False
        if '睡眠' in buffData.keys():
            if data['mode']==0 and show:
                my_print(data,"%s被睡眠，无法行动"%(toMove.name))
            return False
        if '变形' in buffData.keys():
            if data['mode']==0 and show:
                my_print(data,"%s被变形，无法行动"%(toMove.name))
            return False
    return True

def damageCritJudge(to,d,data):
    tempRandom=random()
    #白狼大招
    if '无我' in d['flag'] and tempRandom<d['from'].crit+0.3:
        return True
    #山风大招
    if '斩' in d['flag']:
        return True
    #鬼灯
    if ('眩晕' in to.buff.keys() and d['from'].type=='鬼灯' and canUsePassive(d['from'],data)):
        return True
    #判官
    if (d['from'].type=='判官' and to.hp/to.maxhp<0.3):
        return True
        
    #其余情况
    if tempRandom<d['from'].crit:
        return True
    
    return False
    
def canUseOrb(toMove,n,data):
    if data['orb'][toMove.team]>=n:
        return True
    if '明灯·增伤' in toMove.buff.keys():
        return True
    return False

def canUsePassive(toMove,data):
    if toMove.team==-1:
        return True
    for buff,buffData in toMove.buff.items():
        if '封印被动' in buffData.keys():
            return False
        if '变形' in buffData.keys():
            return False
    return True
    
def canUseSoul(toMove,data):
    if toMove.team==-1:
        return True
    for buff,buffData in toMove.buff.items():
        if '封印御魂' in buffData.keys():
            return False
    return True
def canUseSkill(toMove,data):
    if data['win']:
        return False
    if toMove.team==-1:
        return True
    for buff,buffData in toMove.buff.items():
        if buff=='嘲讽':
            return False
        if '混乱' ==buff:
            return False
        if '沉默' in buffData.keys():
            return False
        if '牢笼' in buffData.keys():
            return False
        if '凝视' in buffData.keys():
            return True
    return True

def canNormalAttack(toMove,data):
    if data['win']:
        return False
     
    if toMove.team==-1:
        return True

    for buff,buffData in toMove.buff.items():
        if '嘲讽' in buffData.keys():
            return True
    return True
        
############################################
#以攻击为例，self.atk0是才开始的总攻击;self.atki是面板攻击，i取initial之意;self.atk是此时加上buff的攻击。
############################################

class 裁判旗():
    def __init__(self):
        self.sp=130
        self.po=0
        self.team=-1
        self.id=0
        self.name='裁判旗'
        self.buff={}
        self.type='裁判旗'
    def move(self,data):
        data['swords']+=1
        if data['mode']==0:
            my_print(data,"裁判旗行动，现有大宝剑%d个"%(data['swords']))

class 达摩():
    def __init__(self,info):

        self.atki=2412
        self.dfi=397
        self.maxhpi=10254
        self.spi=100
        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']



    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断合理的选择目标
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and isEnemy(self,i,self):
                to_select.append(i)
        if to_select:
            tg=sample(to_select,1)[0]
        if tg:
            self.sk1(tg,data)


    def sk1(self,tg,data,fj=None):
        if data['mode']==0:
            my_print(data,"%s对%s使用了摇摇晃晃"%(self.name,tg.name))
        d={'flag':[]}
        d['to']=tg
        d['from']=self
        d['td']=self.atk
        if fj:
            d['flag'].append(fj)
        damage(d,data)

############################################  
class 匣中少女():     
    def __init__(self,info):
        
        self.atki=2439
        self.dfi=392
        self.maxhpi=13671
        self.spi=119
        
        self.type='匣中少女'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']


    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,3,data) and 'cd' not in self.buff.keys():
            to_select=[]
            for i in data['units']:
                if i.alive and self.team==i.team:
                    to_select.append(i) 
            if to_select:
                self.sk3(to_select,data)
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)

    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了流光"%(self.name,tg.name))
        d={'flag':['普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk2(self,tg,data):
        if not canUsePassive(self,data):
            return
        if random()<0.2:
            return 
        if data['mode']==0:
            my_print(data,"%s触发了%s的溢彩"%(tg.name,self.name))

        盾值=self.maxhp*0.08
        if random()<self.crit:
            盾值*=self.critDamage
        
        b={'结算':-1,  #回合后结算
            '回合':1,
            '驱散':1,
            '有益':1,
            '盾':盾值,
            '覆盖':['溢彩'],
            }
        gainBuff(tg,'溢彩',b,data)
        temp=randint(1,5)
        if temp==1:
            b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':1,
                                   '攻击':0.1,
                                   '覆盖':['溢彩·加攻','溢彩·加防','溢彩·加抗','溢彩·加速','溢彩·加爆'],
                                   }
            gainBuff(tg,'溢彩·加攻',b,data)
        if temp==2:
            b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':1,
                                   '防御':0.1,
                                   '覆盖':['溢彩·加攻','溢彩·加防','溢彩·加抗','溢彩·加速','溢彩·加爆'],
                                   }
            gainBuff(tg,'溢彩·加防',b,data)
        if temp==3:
            b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':1,
                                   '抵抗':0.1,
                                   '覆盖':['溢彩·加攻','溢彩·加防','溢彩·加抗','溢彩·加速','溢彩·加爆'],
                                   }
            gainBuff(tg,'溢彩·加抗',b,data)
        if temp==4:
            b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':1,
                                   '速度':10,
                                   '覆盖':['溢彩·加攻','溢彩·加防','溢彩·加抗','溢彩·加速','溢彩·加爆'],
                                   }
            gainBuff(tg,'溢彩·加速',b,data)
        if temp==5:
            b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':1,
                                   '暴伤':0.1,
                                   '覆盖':['溢彩·加攻','溢彩·加防','溢彩·加抗','溢彩·加速','溢彩·加爆'],
                                   }
            gainBuff(tg,'溢彩·加爆',b,data)
                                
    def sk2b(self,tg,data):
        if not canUsePassive(self,data):
            return
        if '溢彩·重复' in tg.buff.keys():
            return
        temp=0
        tempRandom=random()
        if tempRandom<(1+self.hit)/(1+tg.resist):
            temp=randint(1,5)
            b={'结算':-4,  #行动后结算
               '回合':1,
               '驱散':0,
               '有益':0,
               '溢彩·重复':1,
               '隐藏':1,
                                
                            }
            gainBuff(tg,'溢彩·重复',b,data)
        else:
            resisted(tg,self,data)
        if temp==1:
            d={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':-1,
                                   '攻击':-0.1,
                                   '覆盖':['溢彩·减攻','溢彩·减防','溢彩·减爆','溢彩·减速','溢彩·减抗'],
                                   }
            gainBuff(tg,'溢彩·减攻',d,data)
        if temp==2:
            d={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':-1,
                                   '防御':-0.1,
                                   '覆盖':['溢彩·减攻','溢彩·减防','溢彩·减爆','溢彩·减速','溢彩·减抗'],
                                   }
            gainBuff(tg,'溢彩·减防',d,data)
        if temp==3:
            d={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':-1,
                                   '抵抗':-0.1,
               '覆盖':['溢彩·减攻','溢彩·减防','溢彩·减爆','溢彩·减速','溢彩·减抗'],
                                   }
            gainBuff(tg,'溢彩·减抗',d,data)
        if temp==4:
            d={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':-1,
                                   '速度':-10,
               '覆盖':['溢彩·减攻','溢彩·减防','溢彩·减爆','溢彩·减速','溢彩·减抗'],
                                   }
            gainBuff(tg,'溢彩·减速',d,data)
        if temp==5:
            d={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':-1,
                                   '暴伤':-0.1,
               '覆盖':['溢彩·减攻','溢彩·减防','溢彩·减爆','溢彩·减速','溢彩·减抗'],
                                   }
            gainBuff(tg,'溢彩·减爆',d,data)
            
        
    def sk3(self,tgs,data):
        if data['mode']==0:
           my_print(data,"%s使用了回梦"%(self.name))    
        b={'结算':-1,  #回合后结算
                                   '回合':2,
                                   '驱散':0,
                                   '有益':0,
                                   '隐藏':0,
                                   }
        gainBuff(self,'cd',b,data)
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        for i in tgs:
            d={'结算':1,  #回合前结算
                                '回合':2,
                                '驱散':0,
                                '有益':1,
                                '特殊':i.hp*0.6,
                                '覆盖':['回梦']
                                }
            gainBuff(i,'回梦',d,data)

class 桃花妖():     
    def __init__(self,info):
        
        self.atki=2385
        self.dfi=490
        self.maxhpi=11383
        self.spi=100
 
        self.type='桃花妖'

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']


    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断是否使用三技能
        if 'cd' not in self.buff.keys() and canUseSkill(self,data) and canUseOrb(self,3,data):
            temp=[]
            for i in data['units']:
                if i.alive==0 and i.team==self.team and not data['summonsSpecial'][data['units'].index(i)]:
                    temp.append(i)
            if temp:
                tg=sample(temp,1)[0]
                self.sk3(tg,data)
                return
        #判断是否使用二技能
        if canUseSkill(self,data) and canUseOrb(self,2,data):
            temp=None
            for i in data['units']:
                if i.alive==1 and i.team==self.team:
                    if i.hp<i.maxhp*0.7:
                        if not temp or temp.hp/temp.maxhp>i.hp/i.maxhp:
                            temp=i
            if temp:
                self.sk2(temp,data)              
                return
        if canNormalAttack(self,data):
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)                                         
            
    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了花舞"%(self.name,tg.name))
        d={'flag':['普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk2(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-2,data)
        if data['mode']==0:
            my_print(data,"%s对%s使用了花之馨香"%(self.name,tg.name))
        h={'flag':['花之馨香']}
        h['to']=tg
        h['from']=self
        h['heal']=self.maxhp*0.25
        heal(h,data)
        
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)

        if data['mode']==0:
            my_print(data,"%s对%s使用了桃之灼灼"%(self.name,tg.name))

        tg.alive=1
        data['action'].append(tg)
        data['action'].sort(key=lambda x:(x.po,x.sp,-x.id))
        if data['mode']==0:
            my_print(data,"%s复活"%(tg.name))
            
        h={'flag':[]}
        h['to']=tg
        h['from']=self
        h['heal']=self.maxhp*0.25        
        b={'结算':-1,  #回合后结算
                                   '回合':2,
                                   '驱散':0,
                                   '有益':0,
                                   '隐藏':0,
                                   }
        gainBuff(self,'cd',b,data)
        heal(h,data)
        temp='复活过'
        b={'结算':-1,  #回合后结算
                                   '回合':-1,
                                   '驱散':0,
                                   '有益':0,
                                   '隐藏':1
                                   }
        gainBuff(tg,temp,b,data)

class 妖刀姬():   
    def __init__(self,info):
        
        self.atki=3270
        self.dfi=397
        self.maxhpi=10026
        self.spi=111

        self.type='妖刀姬'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']


    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,3,data):
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and self.team!=i.team:
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk3(tg,data)
            return
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)   


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了不祥之刃"%(self.name,tg.name))
        d={'flag':['普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.2
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk2(self,damage,d,data):
        if not canUsePassive(self,data):
            return
        if random()<0.2:
            if data['mode']==0:
                my_print(data,"%s触发了连斩"%(self.name))
            return damage*1.4
        else:
            return damage
    
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s对%s使用了杀戮"%(self.name,tg.name))
        d={'flag':['杀戮']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.58
        d['times']=6
        damage(d,data)

class 凤凰火():
    def __init__(self,info):
        self.atki=2669
        self.dfi=439
        self.maxhpi=11460
        self.spi=108
        
        self.type='凤凰火'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']
        self.sk1times=0

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,3,data):
            to_select=[]
            for i in data['uands']:
                if i.alive and self.team!=i.team:
                    to_select.append(i)
            tg=sample(to_select,1)[0]
            self.sk3(tg,data)
            
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了凤火"%(self.name,tg.name))
        
        d={'flag':['凤火','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk1b(self,tg,data):
        tempRandom=random()
        if tempRandom<0.5*(1+self.hit):
            if tempRandom<0.5*(1+self.hit)/(1+tg.resist):
                self.sk1times+=1
                tempMinus=str(self.id)+'凤火·减暴'+str(self.sk1times)
                tempPlus=str(self.id)+'凤火·加暴'+str(self.sk1times)
                b1={'结算':-1,  #回合后结算
                                   '回合':2,
                                   '驱散':1,
                                   '有益':-1,
                                   '暴击':-0.1,
                                   }
                b2={'结算':-1,  #回合后结算
                                   '回合':2,
                                   '驱散':1,
                                   '有益':1,
                                   '暴击':0.1,
                                   }
                gainBuff(tg,tempMinus,b1,data)
                gainBuff(self,tempPlus,b2,data)
            else:
                resisted(tg,self,data)

    def sk2(self,tg,d,data):
        if not canUsePassive(self,data):
            return
        temp=0
        for buff,buffInfo in tg.buff.items():
            if buffInfo['有益']==-1:
                temp=1
                break
        if not temp:
            return
        tempRandom=random()
        if tempRandom<0.5*(1+self.hit):
            if tempRandom<0.5*(1+self.hit)/(1+tg.resist):
                if data['mode']==0:
                    my_print(data,"%s触发%s被动烈焰"%(tg.name,self.name))
                b={'结算':-1,  #回合后结算
                                       '回合':1,
                                       '驱散':0,
                                       '有益':-1,
                                       '眩晕':0,
                                       '覆盖':['眩晕']
                                       }
                gainBuff(tg,'眩晕',b,data)
            else:
                resisted(tg,self,data)
    
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了凤凰业火"%(self.name))
        d={'flag':['aoe','凤凰业火']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.99*1.2
        damage(d,data)

class 大天狗():
    def __init__(self,info):
        self.atki=3136
        self.dfi=419
        self.maxhpi=10026
        self.spi=110

        self.type='大天狗'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,3,data):
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and self.team!=i.team:
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk3(tg,data)
            
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and self.team!=i.team:
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了风袭"%(self.name,tg.name))
        
        d={'flag':['普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk2(self,data):
        if not canUsePassive(self,data):
            return
        b={'结算':1,  #回合前结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':1,
                                   '免控':1,
                                   }
        gainBuff(self,'钢铁之羽·免控',b,data)
    def sk2b(self,data):
        if not canUsePassive(self,data):
            return
        b1={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':1,
                                   '攻击':0.15,
                                   }
        b2={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':1,
                                   '暴伤':0.15,
                                   }
        gainBuff(self,'钢铁之羽·加攻',b1,data)
        gainBuff(self,'钢铁之羽·加爆',b2,data)
        
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了羽刃风暴"%(self.name))
        d={'flag':['aoe']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.37*1.2
        d['times']=4
        damage(d,data)

class 茨木童子():
    def __init__(self,info):
        self.atki=3216
        self.dfi=397
        self.maxhpi=10254
        self.spi=112
        
        self.type='茨木童子'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']


    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,3,data):
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            to_select.sort(key=lambda x:x.hp/x.maxhp)
            if to_select and to_select[0].hp==to_select[0].maxhp:
                tg=sample(to_select,1)[0]
            elif to_select:
                tg=to_select[0]
            if tg:
                self.sk3(tg,data)
            
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            to_select.sort(key=lambda x:x.hp/x.maxhp)
            if to_select and to_select[0].hp==to_select[0].maxhp:
                tg=sample(to_select,1)[0]
            elif to_select:
                tg=to_select[0]
            if tg:
                self.sk1(tg,data)

    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了黑焰"%(self.name,tg.name))
        
        d={'flag':['黑焰','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk1b(self,tg,data):
        tempRandom=random()
        if tempRandom<0.3*(1+self.hit):
            if tempRandom<0.3*(1+self.hit)/(1+tg.resist):
                tempMinus='黑焰·增伤'
                b={'结算':-1,  #回合后结算
                                   '回合':2,
                                   '驱散':1,
                                   '有益':-1,
                                   '受到伤害增加':0.2
                                   }

                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)
    def sk2(self,tg,num,data):
        if not canUsePassive(self,data):
            return
        if data['mode']==0:
            my_print(data,"%s对%s迁怒"%(self.name,tg.name))
        d={'flag':['迁怒','针女'],
           'to':tg,
           'from':self,
           'td':num,
            }
        damage(d,data)
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s对%s使用了地狱之手"%(self.name,tg.name))
        d={'flag':['地狱之手']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*2.63*1.2
        damage(d,data)

class 酒吞童子():
    def __init__(self,info):
        self.atki=3136
        self.dfi=375
        self.maxhpi=11165
        self.spi=113

        self.type='酒吞童子'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']


    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,3,data) and self.hp/self.maxhp<=0.3 and '狂啸·吸血' not in self.buff.keys() and '狂气' in self.buff.keys():
            self.sk3(data)
            
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            if not to_select:
                return
            to_select.sort(key=lambda x:x.hp/x.maxhp)
            temp=[to_select.pop()]
            tempUnit=None
            if to_select:
                tempUnit=to_select.pop()
            while tempUnit and tempUnit.hp==tempUnit.maxhp:
                temp.append(tempUnit)
                if to_select:
                    tempUnit=to_select.pop()
                else:
                    break
            if temp:
                tg=sample(temp,1)[0]
            if tg:
                self.sk1(tg,data)

    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了鬼葫芦"%(self.name,tg.name))
        
        d={'flag':['鬼葫芦','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        d['times']=1
        if '狂气' in self.buff.keys() and not fj:
            d['times']+=self.buff['狂气']['层数']
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk2(self,tp,data):
        if not canUsePassive(self,data):
            return
        if  '狂气' in self.buff.keys() and self.buff['狂气']['层数']==4:
            return
        temp=0
        if tp==1 and random()<0.5:
            temp+=1
        if tp==2 and random()<0.25:
            temp+=1
        if temp:
            if data['mode']==0:
                my_print(data,'%s触发了狂气'%(self.name))
            if '狂气' not in self.buff.keys():
                b={'结算':-1,  #回合后结算
                                   '回合':-1,
                                   '驱散':1,
                                   '有益':1,
                                   '层数':temp,
                                   }
                gainBuff(self,'狂气',b,data)
            else:
                if self.buff['狂气']['层数']==4:
                    temp=0
                self.buff['狂气']['层数']+=temp
            if data['mode']==0:
                my_print(data,'%s现有%d层狂气'%(self.name,self.buff['狂气']['层数']))

            
    def sk3(self,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了狂啸"%(self.name))
        h={'flag':['狂啸']}
        h['to']=self
        h['from']=self
        h['heal']=self.maxhp*0.5
        heal(h,data)
        self.po+=0.3
        data['action'].sort(key=lambda x:(x.po,x.sp,-x.id))
        b={'结算':-1,  #回合后结算
                                   '回合':self.buff['狂气']['层数'],
                                   '驱散':0,
                                   '有益':1,
                                   '吸血':0.3,
                                   '免控':-1,
                                   }

        gainBuff(self,'狂啸·吸血',b,data)

class 一目连():
    def __init__(self,info):
        self.atki=2385
        self.dfi=392
        self.maxhpi=13899
        self.spi=117

        self.type='一目连'

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']


    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,3,data):
            temp=None
            for i in data['units']:
                if i.alive==1 and i.team==self.team:
                    if i.hp<i.maxhp*0.3:
                        if not temp or temp.hp/temp.maxhp>i.hp/i.maxhp:
                            temp=i
            if temp:
                self.sk2(temp,data)              
            else:
                to_select=[]
                for i in data['units']:
                    if i.alive and self.team==i.team:
                        to_select.append(i)
                if to_select:
                    self.sk3(to_select,data)
        elif canNormalAttack(self,data):
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive==1 and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)

    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了风符·破"%(self.name,tg.name))
        
        d={'flag':['风符·破','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk1b(self,tg,data):
        tempRandom=random()
        if tempRandom<1*(1+self.hit):
            if tempRandom<1*(1+self.hit)/(1+tg.resist):
                tempMinus='风符·破·降攻'
                b={'结算':-1,  #回合后结算
                                   '回合':2,
                                   '驱散':1,
                                   '有益':-1,
                                   '攻击':-0.2,
                                   '覆盖':['风符·破·降攻']
                                   }

                gainBuff(tg,tempMinus,b,data)
                b={'结算':-1,  #回合后结算
                                   '回合':2,
                                   '驱散':1,
                                   '有益':-1,
                                   '攻击':0.2,
                                   '覆盖':['风符·破·加攻']
                                   }
                gainBuff(self,'风符·破·加攻',b,data)                                   
            else:
                resisted(tg,self,data)
    def sk2(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s对%s使用了风符·护"%(tg.name,self.name))
        盾值=self.maxhp*0.18
        if random()<self.crit:
            盾值*=self.critDamage
        
        b={'结算':-1,  #回合后结算
            '回合':2,
            '驱散':0,
            '有益':1,
            '盾':盾值,
            '覆盖':['风符·护'],
           '炸盾':self.maxhp*0.12
            }
        gainBuff(tg,'风符·护',b,data)
    def sk3(self,tgs,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了风神之佑"%(self.name))
        盾值=self.maxhp*0.16
        if random()<self.crit:
            盾值*=self.critDamage
        for tg in tgs:
            b={'结算':-1,  #回合后结算
            '回合':1,
            '驱散':0,
            '有益':1,
            '盾':盾值,
            '覆盖':['风神之佑'],
            '攻击':0.1,
            '抵抗':0.15,
            }
            gainBuff(tg,'风神之佑',b,data)

class 两面佛():
    def __init__(self,info):
        self.atki=3136
        self.dfi=401
        self.maxhpi=10482
        self.spi=109
        
        self.type='两面佛'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']


    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,3,data):
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive==1 and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk3(tg,data)
            
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive==1 and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了风雷两生"%(self.name,tg.name))
        
        d={'flag':['风雷两生','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25*1.1
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk2(self,tg,data):
        if not canUsePassive(self,data):
            return
        b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':-1,
                                   '防御':-0.18,
                                   '覆盖':['怒目·减防']
                                   }
        gainBuff(tg,'怒目·减防',b,data)
    def sk2b(self,tg,data):
        if not canUsePassive(self,data):
            return
        b1={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':-1,
                                   '攻击':-0.18,
                                   '覆盖':['怒目·减攻'],
                                   }
        gainBuff(tg,'怒目·减攻',b1,data)
        
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了神罪连击"%(self.name))
        d={'flag':['aoe','神罪连击']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.4*1.2*1.1
        d['times']=3
        damage(d,data)

class 花鸟卷():
    def __init__(self,info):
        self.atki=3136
        self.dfi=401
        self.maxhpi=10482
        self.spi=109
        
        self.type='花鸟卷'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']


        self.birds=1

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        self.changeBirds(1,data)
        if canUseSkill(self,data) and canUseOrb(self,3,data):
            temp=None
            for i in data['units']:
                if i.alive==1 and i.team==self.team:
                    if i.hp<i.maxhp*0.7:
                        if not temp or temp.hp/temp.maxhp>i.hp/i.maxhp:
                            temp=i
            if temp:
                tgs=[]
                for j in data['uands']:
                    if j.alive==1 and j.team==self.team:
                        tgs.append(j)
                if tgs:
                    self.sk3(tgs,data)              
                    return 
        if canNormalAttack(self,data):
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive==1 and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)                                     

    def changeBirds(self,n,data):
        self.birds+=n
        if self.birds<0:
            self.birds=0
        if self.birds>3:
            self.birds=3
        if data['mode']==0:
            my_print(data,'%s现在有飞鸟%d个'%(self.name,self.birds))


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了归鸟"%(self.name,tg.name))
        
        d={'flag':['归鸟','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.4
        d['times']=self.birds
        if fj:
            d['times']=1
            self.changeBirds(-1,data)
            d['flag'].append(fj)
        damage(d,data)

    def sk1b(self,tg,data):
        if random()<0.8:
            if data['mode']==0:
                my_print(data,"%s鸟回归到了%s"%(self.name,tg.name))
            h={'flag':['归鸟']}
            h['to']=tg
            h['from']=self
            h['heal']=self.maxhp*0.1
            heal(h,data)
    
    def sk2(self,tg,data):
        if not canUsePassive(self,data):
            return
        if self.birds>0 and random()<0.3 and self.team==tg.team and self.alive==1:
            self.changeBirds(-1,data)
            return True
        else:
            return False
    def sk2b(self,data):
        if not canUsePassive(self,data):
            return
        if random()<0.3:
            self.po+=0.3
            data['action'].sort(key=lambda x:(x.po,x.sp,-x.id))
            if data['mode']==0:
                my_print(data,"%s遁入画境"%(self.name))
        
    def sk3(self,tgs,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了花鸟相闻"%(self.name))
        for tg in tgs:
            h={'flag':['花鸟相闻']}
            h['to']=tg
            h['from']=self
            h['heal']=self.maxhp*0.12
            heal(h,data)
            b={'结算':-1,  #回合后结算
                                       '回合':2,
                                       '驱散':0,
                                       '有益':1,
                                       'hot':0.11,
                                       '覆盖':['芬芳'],
                                       '来源':self
                                       }
            gainBuff(tg,'芬芳',b,data)

class 青行灯():
    def __init__(self,info):
        self.atki=2439
        self.dfi=479
        self.maxhpi=11621
        self.spi=119
        
        self.type='青行灯'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,3,data):
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive==1 and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk3(tg,data)
            
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive==1 and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了幽光"%(self.name,tg.name))
        
        d={'flag':['幽光','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.20
        if fj:
            d['flag'].append(fj)
        damage(d,data)


    def sk2(self,tg,data):
        if not canUsePassive(self,data):
            return
        if tg!=self and self.team==tg.team and random()<0.4-0.03*data['orb'][self.team]:
            temp='明灯·增伤'
            b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':1,
                                   '造成伤害增加':0.05*data['orb'][self.team],
                                   }

            gainBuff(tg,temp,b,data)
    
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了吸魂灯"%(self.name))
        d={'flag':['aoe','吸魂灯']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.58*1.2
        damage(d,data)
  
class 食梦貘():
    def __init__(self,info):
        self.atki=2412
        self.dfi=463
        self.maxhpi=11963
        self.spi=119
 
        self.type='食梦貘' 

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']


    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,3,data):
            to_select=[]
            for i in data['uands']:
                if i.alive==1 and self.team!=i.team:
                    to_select.append(i)
            if to_select:
                self.sk3(to_select,data)
            
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive==1 and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)
            
    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了入眠"%(self.name,tg.name))
        
        d={'flag':['入眠','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.8*1.24
        if fj:
            d['flag'].append(fj)
        damage(d,data)
        
    def sk1b(self,tg,data):
        tempRandom=random()
        if tempRandom<0.2*(1+self.hit):
            if tempRandom<0.2*(1+self.hit)/(1+tg.resist):
                tempMinus='睡眠'
                b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':-1,
                                   '睡眠':1,
                                   '覆盖':['睡眠'],
                                   }

                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)
        tempRandom=random()
        if tempRandom<0.2:
            dispel(tg,-1,self,data)
    def sk2(self,data):
        if not canUsePassive(self,data):
            return
        to_select=[]
        for i in data['units']:
            if i.alive and i.team==self.team:
                to_select.append(i)
        to_select.sort(key=lambda x:x.hp/x.maxhp)
        if to_select[0].hp==to_select[0].maxhp:
            tg=sample(to_select,1)[0]
        else:
            tg=to_select[0]
        if data['mode']==0:
            my_print(data,"%s触发了沉睡，治疗了%s"%(self.name,tg.name))
        h={'flag':['沉睡']}
        h['to']=tg
        h['from']=self
        h['heal']=self.maxhp*0.05
        heal(h,data)
    
    
    def sk3(self,tgs,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        for tg in tgs:
            if data['mode']==0:
                my_print(data,"%s对%s使用了食梦者"%(self.name,tg.name))
            tempTurn=randint(1,2)
            tempRandom=random()
            if tempRandom<0.5*(1+self.hit):
                if tempRandom<0.5*(1+self.hit)/(1+tg.resist):
                    tempMinus='睡眠'
                    b={'结算':-1,  #回合后结算
                                       '回合':tempTurn,
                                       '驱散':1,
                                       '有益':-1,
                                       '睡眠':1,
                                       '覆盖':['睡眠'],
                                       }


                    gainBuff(tg,tempMinus,b,data)
                else:
                    resisted(tg,self,data)

class 兵俑():
    def __init__(self,info):
        self.atki=2385
        self.dfi=415
        self.maxhpi=13330
        self.spi=116
        
        self.type='兵俑'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']


    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,2,data):
            to_select=[]
            for i in data['uands']:
                if i.alive==1 and self.team!=i.team:
                    to_select.append(i)
            if to_select:
                self.sk3(to_select,data)
            
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive==1 and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)
            
    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了挥斩"%(self.name,tg.name))
        
        d={'flag':['挥斩','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.df*1.6*2.0
        temp='挥斩·增伤'
        if temp not in self.buff.keys():
            b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':0,
                                   '隐藏':1,
                                   '对象':tg,
                                   }
            gainBuff(tg,temp,b,data)
        else:
            if self.buff[temp]['对象']==tg:
                d['td']*=1.5
            removeBuff(self,'挥斩',data)
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk1b(self,tg,data):
        tempRandom=random()
        if tempRandom<0.3*(1+self.hit):
            if tempRandom<0.3*(1+self.hit)/(1+tg.resist):
                tempMinus='嘲讽'
                b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':-1,
                                   '嘲讽':self,
                                   '覆盖':['嘲讽']
                                   }

                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)
        tempRandom=random()
        if tempRandom<0.2:
            dispel(tg,-1,self,data)
    def sk2(self,data):
        if not canUsePassive(self,data):
            return
        if self.hp/self.maxhp>0.8 and '坚甲1' in self.buff.keys():
            removeBuff(self,'坚甲1',data)
        if self.hp/self.maxhp<=0.8 and '坚甲1' not in self.buff.keys():
            temp='坚甲1'
            if data['mode']==0:
                my_print(data,'%s触发了坚甲'%self.name)
            b={'结算':-1,
               '回合':-1,
               '有益':0,
               '驱散':0,
               '覆盖':[temp],
               '防御':0.11
                }
            gainBuff(self,temp,b,data)
        if self.hp/self.maxhp>0.6 and '坚甲2' in self.buff.keys():
            removeBuff(self,'坚甲2',data)
        if self.hp/self.maxhp<=0.6 and '坚甲2' not in self.buff.keys():
            temp='坚甲2'
            if data['mode']==0:
                my_print(data,'%s触发了坚甲'%self.name)
            b={'结算':-1,
               '回合':-1,
               '有益':0,
               '驱散':0,
               '覆盖':[temp],
               '防御':0.11
                }
            gainBuff(self,temp,b,data)
        if self.hp/self.maxhp>0.4 and '坚甲3' in self.buff.keys():
            removeBuff(self,'坚甲3',data)
        if self.hp/self.maxhp<=0.4 and '坚甲3' not in self.buff.keys():
            temp='坚甲3'
            if data['mode']==0:
                my_print(data,'%s触发了坚甲'%self.name)
            b={'结算':-1,
               '回合':-1,
               '有益':0,
               '驱散':0,
               '覆盖':[temp],
               '防御':0.11
                }
            gainBuff(self,temp,b,data)
        if self.hp/self.maxhp>0.2 and '坚甲4' in self.buff.keys():
            removeBuff(self,'坚甲4',data)
        if self.hp/self.maxhp<=0.2 and '坚甲4' not in self.buff.keys():
            temp='坚甲4'
            if data['mode']==0:
                my_print(data,'%s触发了坚甲'%self.name)
            b={'结算':-1,
               '回合':-1,
               '有益':0,
               '驱散':0,
               '覆盖':[temp],
               '防御':0.11
                }
            gainBuff(self,temp,b,data)
    def sk3(self,tgs,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-2,data)
        temp=0
        for tg in tgs:
            if data['mode']==0:
                my_print(data,"%s对%s使用了坚不可破"%(self.name,tg.name))
            tempRandom=random()
            if tempRandom<0.5*(1+self.hit):
                if tempRandom<0.5*(1+self.hit)/(1+tg.resist):
                    tempMinus='嘲讽'
                    b={'结算':-1,  #回合后结算
                                       '回合':1,
                                       '驱散':1,
                                       '有益':-1,
                                       '嘲讽':self,
                                       '覆盖':['嘲讽'],
                                       '特殊·兵俑':self,
                                       }
                    

                    if gainBuff(tg,tempMinus,b,data):
                        temp+=1
                else:
                    resisted(tg,self,data) 
        if temp:
            tempMinus='坚不可破·石化'
            b={'结算':-1,  #回合后结算
                                           '回合':-1,
                                           '驱散':0,
                                           '有益':-1,
                                           '速度比':-0.4,
                                           '降低受到伤害':0.8,
                                           '覆盖':['坚不可破·石化']
                                           }
            gainBuff(self,tempMinus,b,data)

class 鲤鱼旗():
    def __init__(self,info):
        self.atki=info['攻击']
        self.dfi=info['防御']
        self.maxhpi=info['生命']
        self.spi=info['速度']
        
        self.type='鲤鱼旗'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']


    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)


    def move(self,data):
        self.sk1(data)
            
    def sk1(self,data):

        temp=[]
        for i in data['units']:
            if isFriend(i,self,self) and i.alive:
                for j in i.buff.keys():
                    if i.buff[j]['有益']==-1:
                        temp.append((i,j))
        if not temp:
            return
        elif len(temp)==1:
            if temp[0][0].buff[temp[0][1]]['驱散']==1:
                if data['mode']==0:
                    my_print(data,"%s对%s的%s进行驱散"%(self.name,temp[0][0].name,temp[0][1]))
                removeBuff(temp[0][0],temp[0][1],data)
        else:
            temp1,temp2=sample(temp,2)
            if temp1[0].buff[temp1[1]]['驱散']==1:
                if data['mode']==0:
                    my_print(data,"%s驱散了%s的%s"%(self.name,temp1[0].name,temp1[1]))
                removeBuff(temp1[0],temp1[1],data)
            if temp2[0].buff[temp2[1]]['驱散']==1:
                if data['mode']==0:
                    my_print(data,"%s驱散了%s的%s"%(self.name,temp2[0].name,temp2[1]))
                removeBuff(temp2[0],temp2[1],data)

    def sk2(self,tg,data):
        if not canUsePassive(self,data):
            return
        h={'flag':['鲤鱼旗']}
        h['to']=tg
        h['from']=self
        h['heal']=self.maxhp*0.4
        heal(h,data)

class 惠比寿():
    def __init__(self,info):
        self.atki=2358
        self.dfi=437
        self.maxhpi=12874
        self.spi=107
        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.type='惠比寿'
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']
        

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,2,data) and not data['summons'][self.team]:
            self.sk3(data)
            
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive==1 and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)
            
    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        
        if data['mode']==0:
            my_print(data,"%s对%s使用了赐福"%(self.name,tg.name))
        
        d={'flag':['赐福','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk2(self,data):
        if not canUsePassive(self,data):
            return
        if random()<0.3:
            if data['mode']==0:
                my_print(data,"%s触发了转祸为福"%(self.name))
            gainOrb(self,1,data)
    def sk3(self,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-2,data)
        if data['mode']==0:
            my_print(data,'%s召唤鲤鱼旗'%self.name)
        data['ids']+=1
        data['summons'][self.team]=鲤鱼旗({
        'id':data['ids'],
        '名字':self.name+'的鲤鱼旗',
        '速度':self.sp,
        '位置':0,
        '队伍':self.team,
        '生命':self.maxhp*0.6,
        '攻击':0,
        '防御':self.df,
        '暴击':0,
        '暴击伤害':1.50,
        '效果命中':0.00,
        '效果抵抗':0.00,
        '御魂':''
            })
        
        b={'结算':-1,  #回合后结算
                                   '回合':-1,
                                   '驱散':0,
                                   '有益':0,
                                   '免异':-1,
                                   }
        gainBuff(data['summons'][self.team],'免异',b,data)
        data['uands'].append(data['summons'][self.team])
        data['action'].insert(1,data['summons'][self.team])

class 百目鬼():
    def __init__(self,info):
        self.atki=2734
        self.dfi=507
        self.maxhpi=9456
        self.spi=118
        
        self.type='百目鬼'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']
        

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,2,data):
            to_select=[]
            for i in data['uands']:
                if i.alive==1 and self.team!=i.team:
                    to_select.append(i)
            if to_select:
                self.sk3(to_select,data)
            
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive==1 and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)
 
    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了瞳炎"%(self.name,tg.name))
        
        d={'flag':['瞳炎','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1*1.2
        if fj:
            d['flag'].append(fj)
        damage(d,data)
        
    def sk1b(self,tg,data):
        if '凝视' in tg.buff.keys():
            tg.buff['凝视']['回合']+=1
        
        
    def sk2(self,data):
        if not canUsePassive(self,data):
            return
        if random()<0.2:
            return
        if '鬼眸' not in self.buff.keys():
            tempMinus='鬼眸'
            b={'结算':-3,  #回合后结算
                                       '回合':-1,
                                       '驱散':0,
                                       '有益':0,
                                       '层数':1,
                                       '覆盖':[],
                                       }
            gainBuff(self,tempMinus,b,data)        
        else:
            self.buff['鬼眸']['层数']+=1
            if self.buff['鬼眸']['层数']>5:
                self.buff['鬼眸']['层数']=5
        if data['mode']==0:
            my_print(data,'%s触发了鬼眸，现有%d层鬼眸'%(self.name,self.buff['鬼眸']['层数']))
    
    def sk2b(self,data):
        if not canUsePassive(self,data):
            return
        if canUseSkill(self,data) and '鬼眸' in self.buff.keys() and self.buff['鬼眸']['层数']==5:
            to_select=[]
            for i in data['uands']:
                if i.alive==1 and self.team!=i.team:
                    to_select.append(i)
            removeBuff(self,'鬼眸',data)
            actionStartCheck(self,data)
            self.sk3(to_select,data)
            actionOverCheck(self,data)
    
    def sk3(self,tgs,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-2,data)
        for tg in tgs:
            if data['mode']==0:
                my_print(data,"%s对%s使用了诅咒之眼"%(self.name,tg.name))
            tempRandom=random()
            if tempRandom<1*(1+self.hit):
                if tempRandom<1*(1+self.hit)/(1+tg.resist):
                    tempMinus='凝视'
                    b={'结算':-1,  #回合后结算
                                       '回合':1,
                                       '驱散':1,
                                       '有益':-1,
                                       '凝视':1,
                                       'from':self,
                                       '覆盖':['凝视'],
                                       }


                    gainBuff(tg,tempMinus,b,data)
                else:
                    resisted(tg,self,data)
                    
class 般若():
    def __init__(self,info):
        self.atki=3136
        self.dfi=397
        self.maxhpi=10596
        self.spi=114
        
        self.type='般若'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,3,data) and 'cd' not in self.buff.keys():
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive==1 and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk3(tg,data)
            
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive==1 and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了鬼之假面"%(self.name,tg.name))
        
        d={'flag':['鬼之假面','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.20
        if '狂暴' in self.buff.keys():
            d['times']=2
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk2(self,tg,data):
        if not canUsePassive(self,data):
            return
        tempRandom=random()
        if tempRandom<0.4*(1+self.hit):
            if tempRandom<0.4*(1+self.hit)/(1+tg.resist):
                if data['mode']==0:
                    my_print(data,"%s触发%s被动嫉恨之心"%(tg.name,self.name))
                b={'结算':-1,  #回合后结算
                                       '回合':2,
                                       '驱散':0,
                                       '有益':-1,
                                       '封印御魂':0,
                                       '封印被动':0,
                                       '覆盖':['封印']
                                       }
                gainBuff(tg,'封印',b,data)
            else:
                resisted(tg,self,data)
    
    def sk3(self,tg,data):     
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
           my_print(data,"%s使用了鬼袭"%(self.name))    
        b={'结算':-1,  #回合后结算
                                   '回合':2,
                                   '驱散':0,
                                   '有益':0,
                                   '隐藏':0,
                                   }
        b2={'结算':-1,  #回合后结算
                                   '回合':2,
                                   '驱散':0,
                                   '有益':0,
                                   }
        gainBuff(self,'cd',b,data)
        gainBuff(self,'狂暴',b2,data)
        d={'flag':['aoe','鬼袭']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.1*1.2
        damage(d,data)  
        
class 荒():
    def __init__(self,info):
        self.atki=3323
        self.dfi=490
        self.maxhpi=10254
        self.spi=104
        
        self.type='荒'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        if canUseSkill(self,data) and canUseOrb(self,1,data) and '星辰之境' in self.buff.keys():
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            to_select.sort(key=lambda x:x.hp/x.maxhp)
            if to_select and to_select[0].hp==to_select[0].maxhp:
                tg=sample(to_select,1)[0]
            elif to_select:
                tg=to_select[0]
            if tg:
                self.sk4(tg,data)
        elif canUseSkill(self,data) and canUseOrb(self,3,data):
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            to_select.sort(key=lambda x:x.hp/x.maxhp)
            if to_select and to_select[0].hp==to_select[0].maxhp:
                tg=sample(to_select,1)[0]
            elif to_select:
                tg=to_select[0]
            if tg:
                self.sk3(tg,data)
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            to_select.sort(key=lambda x:x.hp/x.maxhp)
            if to_select and to_select[0].hp==to_select[0].maxhp:
                tg=sample(to_select,1)[0]
            elif to_select:
                tg=to_select[0]
            if tg:
                self.sk1(tg,data)


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了星轨"%(self.name,tg.name))
        
        d={'flag':['星轨','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk2(self,data):
        if not canUsePassive(self,data):
            return
        if data['orb'][self.team]>=6 or random()<0.6:
            if data['mode']==0:
                my_print(data,'%s遁入星辰之境的幻境中'%self.name)
            b={'结算':1,  #回合前结算
                                       '回合':1,
                                       '驱散':0,
                                       '有益':0,
                                       }
            gainBuff(self,'星辰之境',b,data)
        
    def co_attack(self,tg,data):
        if not canUsePassive(self,data):
            return
        if random()>=0.5 or '星辰之境' not in self.buff.keys():
            return
        if isEnemy(self,tg,self):
            self.sk1(tg,data,'协战')
        else:
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            tg=sample(to_select,1)[0]
            self.sk1(tg,data)
            
    def sk3(self,tg,data):     
        temp=3
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-temp,data)
        if data['mode']==0:
           my_print(data,"%s使用了天罚·星"%(self.name))    

        d={'flag':['天罚']}
        d['to']=tg
        d['from']=self
        d['times']=temp
        d['td']=self.atk*1.04*1.15
        damage(d,data)     
        
    def sk4(self,tg,data):
        temp=data['orb'][self.team]
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-temp,data)
        if data['mode']==0:
           my_print(data,"%s使用了天罚·月"%(self.name))    

        d={'flag':['天罚']}
        d['to']=tg
        d['from']=self
        d['times']=temp
        d['td']=self.atk*1.04*1.15
        damage(d,data)    
        
class 小鹿男():
    def __init__(self,info):
        self.atki=2814
        self.dfi=428
        self.maxhpi=11165
        self.spi=120
        
        self.type='小鹿男'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,3,data) and '变身' in self.buff.keys():            
            tg=None
            to_select=[]
            for i in data['units']:
                if i.alive and self.team!=i.team:
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk3(tg,data)
            
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['units']:
                if i.alive and self.team!=i.team:
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了森之力"%(self.name,tg.name))
        
        d={'flag':['森之力','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.20
        if '狂暴' in self.buff.keys():
            d['times']=2
        if fj:
            d['flag'].append(fj)
        damage(d,data)
    
    def sk1b(self,tg,data):
        tempRandom=random()
        if tempRandom<0.5*(1+self.hit):
            if tempRandom<0.5*(1+self.hit)/(1+tg.resist):
                tempMinus='森之力·减抗'
                b={'结算':-1,  #回合后结算
                                   '回合':2,
                                   '驱散':1,
                                   '有益':-1,
                                   '抵抗':-0.3,
                                   '覆盖':['森之力·减抗']
                                   }

                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)
                
    def sk2(self,data):
        if not canUsePassive(self,data):
            return

        self.po+=0.2
        data['action'].sort(key=lambda x:(x.po,x.sp,-x.id))
        if self.po>=1:
            self.po=1
        if data['mode']==0:
            my_print(data,'%s触发了生生不息，现在行动条位置在%.2f'%(self.name,self.po))
    def sk2b(self,buff,buffInfo,data):
        if not canUsePassive(self,data):
            return
        if data['mode']==0:
            my_print(data,'%s触发了生生不息，反弹了buff'%(self.name))
        
        to_select=[]
        for i in data['units']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        tg=sample(to_select,1)[0]
        if random()<(1+self.hit)/(1+tg.resist):    
            gainBuff(tg,buff,buffInfo,data)
        else:
            resisted(tg,self,data)
                        
        
    def sk3(self,tg,data):     
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了鹿角冲撞"%(self.name))    
        temp=[]
        for i in data['action']:
            if i.team==tg.team and i.alive:
                temp.append(i)
        d={'flag':['鹿角冲撞']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.58*1.2
        damage(d,data)  
        if '变身' in self.buff.keys() and self.buff['变身']['层数']>=2:
            tg0=temp.index(tg)
            temp2=[]
            if self.buff['变身']['层数']==2:
                if len(temp)==1:
                    temp2.append(tg)
                else:
                    if tg0==0:
                        temp2.append(temp[1])
                    else:
                        temp2.append(temp[tg0-1])
            if self.buff['变身']['层数']==3:
                if len(temp)>=3:
                    if tg0==0:
                        temp2.append(temp[2])
                        temp2.append(temp[1])
                    elif tg0==1:
                        temp2.append(temp[2])
                        temp2.append(temp[0])
                    else:
                        temp2.append(temp[tg0-2])
                        temp2.append(temp[tg0-1])
                elif len(temp)==2:
                    if tg0==0:
                        temp2.append(temp[0])
                        temp2.append(temp[1])
                    else:
                        temp2.append(temp[1])
                        temp2.append(temp[0])
                else:
                    temp2.append(tg)
                    temp2.append(tg)
            while temp2:
                tg=temp2.pop()
                d={'flag':['鹿角冲撞','特殊aoe'],
                'to':tg,
                'from':self,
                'td':self.atk*1.58*1.2,
                }
                damage(d,data)

    def sk3b(self,data):
        if '小鹿撞晕了人' not in self.buff.keys():
            temp=1
            if '变身' not in self.buff.keys():
                b={'结算':-1,  #回合后结算
                                   '回合':-1,
                                   '驱散':1,
                                   '限制驱散':1,
                                   '有益':1,
                                   '层数':temp,
                                   }
                gainBuff(self,'变身',b,data)
            else:
                if self.buff['变身']['层数']==3:
                    temp=0
                self.buff['变身']['层数']+=temp
            if data['mode']==0:
                my_print(data,'%s现有%d层变身'%(self.name,self.buff['变身']['层数']))
        elif '变身' in self.buff.keys(): 
            if self.buff['变身']['层数']==1:
                removeBuff(self,'变身',data)
            else:
                self.buff['变身']['层数']-=1
    def sk3c(self,to,data):
        to.po-=0.4
        data['action'].sort(key=lambda x:(x.po,x.sp,-x.id))
        if to.po<=0:
            to.po=0
            if data['mode']==0:
                my_print(data,'%s行动条推迟，现在位置在%.2f'%(to.name,to.po))
            b1={'结算':-4,  #行动后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':0,
                                   '隐藏':1,
                            }
            gainBuff(self,'小鹿撞晕了人',b1,data)
            if random()<(1+self.hit)/(1+to.resist):    
                b2={'结算':-1,  #回合后结算
                                       '回合':1,
                                       '驱散':0,
                                       '有益':-1,
                                       '眩晕':0,
                                       '覆盖':['眩晕']
                                       }
                gainBuff(to,'眩晕',b2,data)
            else:
                resisted(to,self,data)
        else:
            if data['mode']==0:
                my_print(data,'%s行动条推迟，现在位置在%.2f'%(to.name,to.po))
                
class 阎魔():
    def __init__(self,info):
        self.atki=2466
        self.dfi=454
        self.maxhpi=11963
        self.spi=117
        
        self.type='阎魔'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,3,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['units']:
                if i.alive and self.team!=i.team:
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk3(tg,data)
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['units']:
                if i.alive and self.team!=i.team:
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了鬼面"%(self.name,tg.name))
        
        d={'flag':['鬼面','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk2(self,tg,data):
        if not canUsePassive(self,data):
            return
        tempRandom=random()
        if tempRandom<0.7*(1+self.hit):
            if tempRandom<0.7*(1+self.hit)/(1+tg.resist):
                tempMinus='变形·黑色小鬼'
                b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':-1,
                                   '变形':1,
                                   '封印被动':1,
                                   '覆盖':[],
                                   }
                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)
    def sk2b(self,tg,data):
        #召唤召唤物时，先建立对应的class，然后再把相应的位置(summons或summonsSpecial)加入，再在uands加入，再在行动条里加入。
        if not canUsePassive(self,data):
            return
        if data['mode']==0:
            my_print(data,'%s召唤白色小鬼'%self.name)
        data['ids']+=1
        data['summonsSpecial'][data['units'].index(tg)]=白色小鬼({
        'id':data['ids'],
        '名字':self.name+'的白色小鬼',
        '速度':self.sp,
        '位置':0,
        '队伍':self.team,
        '生命':self.maxhp*0.6,
        '攻击':self.atk,
        '防御':self.df,
        '暴击':0,
        '暴击伤害':1.50,
        '效果命中':0.00,
        '效果抵抗':0.00,
        '御魂':''
            })
            
        data['uands'].append(data['summonsSpecial'][data['units'].index(tg)])
        data['action'].insert(0,data['summonsSpecial'][data['units'].index(tg)])
        #(死亡召唤白色小鬼)
    def sk3(self,tg,data):     
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
           my_print(data,"%s使用了冤魂重压"%(self.name))    

        d={'flag':['冤魂重压']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*2.11*1.2
        damage(d,data)
    def sk3b(self,tg,data):
        tempRandom=random()
        if tempRandom<1*(1+self.hit):
            if tempRandom<1*(1+self.hit)/(1+tg.resist):
                tempMinus='沉默'
                b={'结算':-1,  #回合后结算
                                   '回合':2,
                                   '驱散':1,
                                   '有益':-1,
                                   '沉默':1,
                                   '覆盖':['沉默'],
                                   }

                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)
                tempRandom=random()

class 白色小鬼():
    def __init__(self,info):
        self.atki=0
        self.dfi=0
        self.maxhpi=0
        self.spi=0
        
        self.type='白色小鬼'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']


    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)


    def move(self,data):
        pass
            
    def sk1(self,data):
        self.hp=0
        die(self,'白色小鬼自杀',data)

    def sk2(self,data):
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if to_select:
            tg=sample(to_select,1)[0]     
        if tg:
            if data['mode']==0:
                my_print(data,"%s爆炸"%(self.name))
            d={'flag':['aoe','白色小鬼自杀']}
            d['to']=tg
            d['from']=self
            d['td']=self.atk
            damage(d,data)

class 荒川之主():
    def __init__(self,info):
        self.atki=3002
        self.dfi=401
        self.maxhpi=11051
        self.spi=111
        
        self.type='荒川之主'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']
        self.减防次数=0
        self.吞噬第一段触发御魂=None
        
    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,3,data):
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            to_select.sort(key=lambda x:x.hp/x.maxhp)
            if to_select and to_select[0].hp==to_select[0].maxhp:
                tg=sample(to_select,1)[0]
            elif to_select:
                tg=to_select[0]
            if tg:
                self.sk3(tg,data)
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            to_select.sort(key=lambda x:x.hp/x.maxhp)
            if to_select and to_select[0].hp==to_select[0].maxhp:
                tg=sample(to_select,1)[0]
            elif to_select:
                tg=to_select[0]
            if tg:
                self.sk1(tg,data)


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了游鱼"%(self.name,tg.name))
        
        d={'flag':['游鱼','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk2(self,data):
        if not canUsePassive(self,data):
            return
        tempRandom=random()
        tempMinus='逐流·减防'+str(self.减防次数)
        b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':-1,
                                   '防御':-0.2,
                                   }
        self.减防次数+=1
        gainBuff(self,tempMinus,b,data)

    def sk3(self,tg,data):     
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
           my_print(data,"%s对%s使用了吞噬"%(self.name,tg.name))    

        d={'flag':['吞噬']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.32*1.2
        damage(d,data)
        tempFlag=d['flag']
        tempFlag.append('多段分割')
        buffEatenNum=0
        if random()>0.2:        
            temp=[]
            for buff,buffInfo in tg.buff.items():
                if buffInfo['驱散']==1 and buffInfo['有益']==1:
                    temp.append(buff)
            if len(temp)==1:
                buffEatenNum=1
            if len(temp)>=2:
                buffEatenNum=randint(1,2)
        if buffEatenNum:
            dispel(tg,buffEatenNum,self,data,'吞噬')

        
        d={'flag':tempFlag}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.32*1.2*(1+0.05*buffEatenNum)
        damage(d,data)        
        self.吞噬第一段触发御魂=None

class 辉夜姬():
    def __init__(self,info):
        self.atki=3002
        self.dfi=401
        self.maxhpi=11051
        self.spi=111
        
        self.type='辉夜姬'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

        
    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,2,data) and ('龙首之玉·幻境' not in self.buff.keys() or self.buff['龙首之玉·幻境']['回合']==1):
            self.sk3(data)
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了蓬莱玉枝"%(self.name,tg.name))
        
        d={'flag':['蓬莱玉枝','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk2(self,tg,data):
        if not canUsePassive(self,data):
            return
        if random()<0.4:
            if data['mode']==0:
                my_print(data,'%s触发了%s火鼠裘'%(tg.name,self.name))
            gainOrb(self,1,data)
    def sk2b(self,data):     
        b={'结算':-1,  #回合后结算
                                       '回合':2,
                                       '驱散':0,
                                       '有益':1,
                                       '覆盖':['龙首之玉·幻境']
                                       }
        gainBuff(self,'龙首之玉·幻境',b,data)
        for i in data['uands']:
            if i.team==self.team:
                b1={'结算':-3, #不结算
                    '回合':-1,
                    '驱散':0,
                    '有益':1,
                    '防御':0.25,
                    '抵抗':0.2,
                    '覆盖':['龙首之玉·加防加抗']
                    }
                gainBuff(i,'龙首之玉·加防加抗',b1,data)  

    def sk3(self,data):     
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-2,data)
        b={'结算':-1,  #回合后结算
                                       '回合':2,
                                       '驱散':0,
                                       '有益':1,
                                       '覆盖':['龙首之玉·幻境']
                                       }
        gainBuff(self,'龙首之玉·幻境',b,data)
        for i in data['uands']:
            if i.team==self.team:
                b1={'结算':-3, #不结算
                    '回合':-1,
                    '驱散':0,
                    '有益':1,
                    '防御':0.25,
                    '抵抗':0.2,
                    '覆盖':['龙首之玉·加防加抗']
                    }
                gainBuff(i,'龙首之玉·加防加抗',b1,data)

class 彼岸花():
    def __init__(self,info):
        self.atki=3002
        self.dfi=388
        self.maxhpi=11393
        self.spi=107
        
        self.type='彼岸花'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']
        self.花海=3
        self.花盾=0
        
    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,3,data):
            self.sk3(data)
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了死亡之花"%(self.name,tg.name))
        
        d={'flag':['死亡之花','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk2(self,tg,data):
        if not canUsePassive(self,data):
            return
        my_print(data,'%s触发了%s的赤团华'%(tg.name,self.name))
        d={'flag':['赤团华']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.39*1.25*(self.花海+self.花盾)
        damage(d,data)
  
    def sk2b(self,data):
        temp=4-ceil(self.hp/self.maxhp/0.25)
        if temp<=self.花盾:
            self.花盾=temp
            return
        self.花盾=temp
        if self.hp/self.maxhp<0.75:
            盾值=(self.maxhp-self.hp)*0.28
            if random()<self.crit:
                盾值*=self.critDamage
            b={'结算':-1,  #回合后结算
            '回合':2,
            '驱散':0,
            '有益':1,
            '盾':盾值,
            '覆盖':['血之花海'],
            }
            gainBuff(self,'血之花海',b,data)
            
    def sk3(self,data):     
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        self.花海+=2
        if self.花海>=3:
            self.花海=3
        if data['mode']==0:
            my_print(data,'%s召唤了花海，现在花海层数为%d'%(self.name,(self.花海+self.花盾)))
        if self.hp/self.maxhp<0.75:
            盾值=(self.maxhp-self.hp)*0.28
            if random()<self.crit:
                盾值*=self.critDamage
            b={'结算':-1,  #回合后结算
            '回合':2,
            '驱散':0,
            '有益':1,
            '盾':盾值,
            '覆盖':['血之花海'],
            }
            gainBuff(self,'血之花海',b,data)

class 玉藻前():
    def __init__(self,info):
        self.atki=3350
        self.dfi=353
        self.maxhpi=12532
        self.spi=110
        
        self.type='玉藻前'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        #判断使用哪个技能
        if not to_select:
            return
        if canUseSkill(self,data) and canUseOrb(self,3,data) and len(to_select)>=2:
            tg=sample(to_select,1)[0]
            self.sk3(tg,data)
        elif canUseSkill(self,data) and canUseOrb(self,3,data) and len(to_select)==1:
            tg=to_select[0]
            self.sk2(tg,data)
        elif canNormalAttack(self,data):
            tg=sample(to_select,1)[0]
            self.sk1(tg,data)


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了灵击"%(self.name,tg.name))
        
        d={'flag':['灵击','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)
    
    def sk1b(self,tg,data):
        tempRandom=random()
        if tempRandom<0.1*(1+self.hit):
            if tempRandom<0.1*(1+self.hit)/(1+tg.resist):
                tempMinus='混乱'
                b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':-1,
                                   '混乱':1,
                                   '覆盖':['混乱'],
                                   }

                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)

    def sk2(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了狐火"%(self.name))
        d={'flag':['狐火']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*2.63*1.1
        damage(d,data)            
    def sk2b(self,tg,data):
        if data['mode']==0:
            my_print(data,"%s使用了狐火"%(self.name))
        d={'flag':['狐火','玉藻前追击','反击']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*2.63*1.1
        damage(d,data)         
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了堕天"%(self.name))
        d={'flag':['aoe','堕天']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.31*1.1
        damage(d,data)
    def sk3b(self,tg,data):
        if data['mode']==0:
            my_print(data,"%s使用了堕天"%(self.name))
        d={'flag':['aoe','堕天','玉藻前追击','反击']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.31*1.1
        damage(d,data) 
        
class 雪童子():
    def __init__(self,info):
        self.atki=3323
        self.dfi=388
        self.maxhpi=10026
        self.spi=121
        
        self.type='雪童子'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

        
    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,3,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk3(tg,data)
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了雪走"%(self.name,tg.name))
        
        d={'flag':['雪走','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.8*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk2(self,tg,data):
        if not canUsePassive(self,data):
            return

        tempint=sample([1,2,2,2],1)[0]
        tempRandom=random()
        if tempRandom<0.45*(1+self.hit):
            if tempRandom<0.45*(1+self.hit)/(1+tg.resist): 
                if data['mode']==0:
                    my_print(data,'%s触发了霜天之织·冰冻'%(self.name))
                tempMinus='冰冻'
                b={'结算':-1,  #回合后结算
                                           '回合':tempint,
                                           '驱散':1,
                                           '有益':-1,
                                           '冰冻':1,
                                           }
              
                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)
                
    def sk2b(self,data):
        if not canUsePassive(self,data):
            return
        b={'结算':1,  #回合前结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':1,
                                   '霜天之织':1,
                                   }
        gainBuff(self,'霜天之织·免封免冻',b,data)
    def sk3(self,tg,data):     
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
           my_print(data,"%s对%s使用了胧月雪华斩"%(self.name,tg.name))    

        d={'flag':['胧月雪华斩']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.8*1.2
        d['times']=3
        temp=deepcopy(self.hit)
        b={'结算':0,  #回合后结算
                                       '回合':1,
                                       '驱散':1,
                                       '有益':1,
                                       '命中':temp
                                       }
        gainBuff(self,'胧月雪华斩·加命中',b,data)   
        damage(d,data)

class 山风():
    def __init__(self,info):
        self.atki=3404
        self.dfi=388
        self.maxhpi=11393
        self.spi=115
        
        self.type='山风'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

        
    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        if canUseSkill(self,data) and canUseOrb(self,0,data):
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            to_select.sort(key=lambda x:x.hp/x.maxhp)
            if to_select and to_select[0].hp==to_select[0].maxhp:
                tg=sample(to_select,1)[0]
            elif to_select:
                tg=to_select[0]
            if tg:
                self.sk3(tg,data)
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了风"%(self.name,tg.name))
        
        d={'flag':['风','普攻']}
        d['to']=tg
        d['from']=self
        d['times']=2
        d['td']=self.atk*0.72*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk2(self,data):
        if not canUsePassive(self,data):
            return
        temp=0.35
        for i in data['units']:
            if i.alive and i.team!=self.team and i.hp/i.maxhp<0.35:
                temp+=0.35
                break
        self.po+=temp
        data['action'].sort(key=lambda x:(x.po,x.sp,-x.id))
        if self.po>=1:
            self.po=1
        if data['mode']==0:
            my_print(data,'%s触发了烈，现在行动条位置在%.2f'%(self.name,self.po))
        if '烈·加攻' not in self.buff.keys():
            b={'结算':-1,  #回合后结算
                                       '回合':1,
                                       '驱散':1,
                                       '有益':1,
                                       '攻击':0.25,
                                       '覆盖':['烈·加攻']
                                       }
            gainBuff(self,'烈·加攻',b,data)                

    def sk3(self,tg,data):     
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
           my_print(data,"%s对%s使用了斩"%(self.name,tg.name))    

        d={'flag':['斩']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.32*1.2
        damage(d,data)
        to_select=[]
        for i in data['uands']:
            if i.alive and isEnemy(self,i,self) and i!=tg:
                to_select.append(i)
        if not to_select:
            return
        to_select.sort(key=lambda x:x.hp/x.maxhp)
        if to_select[0].hp==to_select[0].maxhp:
            tg=sample(to_select,1)[0]
        else:
            tg=to_select[0]        
        if data['mode']==0:
           my_print(data,"%s对%s使用了斩"%(self.name,tg.name))    
        d={'flag':['斩','特殊aoe']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.32*1.15
        damage(d,data)
    def sk3b(self,tg,data):
        tempRandom=random()
        if tempRandom<(1+self.hit):
            if tempRandom<(1+self.hit)/(1+tg.resist): 
                tempMinus='撕裂'
                b={'结算':-1,  #回合后结算
                                           '回合':1,
                                           '驱散':1,
                                           '有益':-1,
                                           '撕裂':self,
                                           '覆盖':['撕裂']
                                           }
              
                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)
                
class 奴良陆生():
    def __init__(self,info):
        self.atki=3028
        self.dfi=384
        self.maxhpi=11393
        self.spi=111
        
        self.type='奴良陆生'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']
        self.畏=[]
        
    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,3,data):
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk3(tg,data)
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了弥弥切丸"%(self.name,tg.name))
        
        d={'flag':['弥弥切丸','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.8*1.15
        if fj:
            d['flag'].append(fj)
        damage(d,data)
        if random()<0.2:
            helpers=[]
            temp=[]
            tempInt=randint(1,2)
            for i in data['units']:
                if i.alive and i.team==self.team and i!=self:
                    temp.append(i)
            if len(temp)==0:
                return
            elif len(temp)==1:
                helpers.append(temp[0])
            elif len(temp)>=2:
                helpers=sample(temp,tempInt)
            if helpers:
                for helper in helpers:
                    my_print(data,'%s协同作战'%helper.name)
                    helper.sk1(tg,data)

    def sk2(self,d,data):
        if not canUsePassive(self,data):
            return
        if random()<0.35:
            tempFlag='镜花水月'+self.name
            if '针女' in d['flag']:
                tempFlag='针女'+tempFlag
            if '傀儡·追击' in d['flag']:
                tempFlag='傀儡·追击'+tempFlag
            if '反击' not in d['flag'] and tempFlag not in d['from'].buff.keys():
                if data['mode']==0:
                    my_print(data,'%s触发了镜花水月'%(self.name))
                满畏=1
                for i in range(4):
                    temp='畏'+str(i)
                    if temp not in self.buff.keys():
                        满畏=0
                        break
                if 满畏:
                    ttemp=['畏0','畏1','畏2','畏3']
                    ttemp.sort(key=lambda x:self.buff[x]['回合'])
                    temp=ttemp[0]
                nb={'结算':-1,  #回合后结算
                                   '回合':4,
                                   '驱散':0,
                                   '有益':0,
                                   '造成伤害增加':0.75,
                                   '覆盖':[temp]
                                   }

                gainBuff(self,temp,nb,data)
                data['反击'].append({'to':d['from'],
                                           'from':self,
                                           'flag':tempFlag,
                            })
                b={'结算':-4,  #行动后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':0,
                                   '隐藏':1,
                                
                            }
                gainBuff(d['from'],tempFlag,b,data)
    def sk2b(self,tg,data):
        if not canUsePassive(self,data):
            return
        if random()<0.35:
            if data['mode']==0:
                my_print(data,self.name+'触发了镜花水月')
            满畏=1
            for i in range(4):
                temp='畏'+str(i)
                if temp not in self.buff.keys():
                    满畏=0
                    break
            if 满畏:
                ttemp=['畏0','畏1','畏2','畏3']
                ttemp.sort(key=lambda x:self.buff[x]['回合'])
                temp=ttemp[0]
            nb={'结算':-1,  #回合后结算
                                   '回合':4,
                                   '驱散':0,
                                   '有益':0,
                                   '造成伤害增加':0.75,
                                   '覆盖':[temp]
                                   }

            gainBuff(self,temp,nb,data)
            tempFlag='镜花水月·抵抗'+self.name
            data['反击'].append({'to':tg,
                                'from':self,
                                'flag':tempFlag
                                })
    def sk3(self,tg,data):     
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
           my_print(data,"%s对%s使用了百鬼夜行"%(self.name,tg.name))    

        d={'flag':['百鬼夜行']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.2*1.25
        damage(d,data)
        满畏=1
        for i in range(4):
            temp='畏'+str(i)
            if temp not in self.buff.keys():
                满畏=0
                break
        if 满畏:
            ttemp=['畏0','畏1','畏2','畏3']
            ttemp.sort(key=lambda x:self.buff[x]['回合'])
            temp=ttemp[0]
        nb={'结算':-1,  #回合后结算
                                   '回合':4,
                                   '驱散':0,
                                   '有益':0,
                                   '造成伤害增加':0.75,
                                   '覆盖':[temp]
                                   }

        gainBuff(self,temp,nb,data)

class 御馔津():
    def __init__(self,info):
        self.atki=3002
        self.dfi=450
        self.maxhpi=12646
        self.spi=119
        
        self.type='御馔津'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']
        self.符咒=0
    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,3,data) and self.符咒!=3:
            self.sk2(data)
        elif canUseSkill(self,data) and canUseOrb(self,3,data) and self.符咒!=3:
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk3(tg,data)
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了一矢"%(self.name,tg.name))
        
        d={'flag':['一矢','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.8*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)
    
    def sk1b(self,tg,data,fj='反击'):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了一矢·封魔"%(self.name,tg.name))
        d={'flag':['一矢·封魔','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.8*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)
        if self.符咒!=3:
            for i in data['units']:
                if i.team==self.team:
                    temp='狐狩界·加防加伤加速'+str(self.符咒)
                    b={'结算':-3, #不结算
                    '回合':-1,
                    '驱散':0,
                    '有益':1,
                    '防御':0.12,
                    '速度':4,
                    '造成伤害增加':0.08,
                    '覆盖':[temp]
                    }
                    gainBuff(i,temp,b,data)
            self.符咒+=1
    def sk1c(self,tg,data):
        tempRandom=random()
        if tempRandom<(1+self.hit):
            if tempRandom<(1+self.hit)/(1+tg.resist):
                tempMinus='一矢·减疗'
                b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':-1,
                                   '减疗':0.75,
                                   '覆盖':['一矢·减疗'],
                                   }

                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)
        tempRandom=random()
        if tempRandom<(1+self.hit):
            if tempRandom<(1+self.hit)/(1+tg.resist):
                tempMinus='一矢·沉默'
                b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':-1,
                                   '沉默':1,
                                   '覆盖':['一矢·沉默'],
                                   }

                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)
        tempRandom=random()
        if tempRandom<(1+self.hit):
            if tempRandom<(1+self.hit)/(1+tg.resist):
                tempMinus='一矢·封印被动'
                b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':-1,
                                   '封印被动':1,
                                   '覆盖':['一矢·封印被动'],
                                   }

                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)    
        tempRandom=random()
        if tempRandom<(1+self.hit):
            if tempRandom<(1+self.hit)/(1+tg.resist):
                tempMinus='一矢·封印御魂'
                b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':-1,
                                   '封印御魂':1,
                                   '覆盖':['一矢·封印御魂'],
                                   }

                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)

    def sk2(self,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,'%s使用了狐狩界，现在符咒数为%d'%(self.name,(self.符咒*4)))
        b={'结算':1,  #回合前结算
                                       '回合':1,
                                       '驱散':0,
                                       '有益':1,
                                       '覆盖':['狐狩界·幻境']
                                       }
        gainBuff(self,'狐狩界·幻境',b,data)
        for i in data['uands']:
            if i.team==self.team:
                for h in range(self.符咒):
                    temp='狐狩界·加防加伤加速'+str(i)
                    b={'结算':-3, #不结算
                    '回合':-1,
                    '驱散':0,
                    '有益':1,
                    '防御':0.12,
                    '速度':4,
                    '造成伤害增加':0.08,
                    '覆盖':[temp]
                    }
                    gainBuff(i,temp,b,data)  
  
    def sk2b(self,data):
        if data['mode']==0:
            my_print(data,'%s使用了狐狩界，现在符咒数为%d'%(self.name,(self.符咒*4)))
        b={'结算':1,  #回合前结算
                                       '回合':1,
                                       '驱散':0,
                                       '有益':1,
                                       '覆盖':['狐狩界·幻境']
                                       }
        gainBuff(self,'狐狩界·幻境',b,data)

            
    def sk3(self,data):     
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
           my_print(data,"%s对%s使用了燃爆·破魔箭"%(self.name,tg.name))    

        d={'flag':['燃爆·破魔箭']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*(1.95+self.符咒*0.8)*1.2
        damage(d,data)
        self.符咒=0

class 鬼灯():
    def __init__(self,info):
        self.atki=3189
        self.dfi=441
        self.maxhpi=9229
        self.spi=110
        
        self.type='鬼灯'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

        
    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,3,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk3(tg,data)
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了锤击"%(self.name,tg.name))
        
        d={'flag':['锤击','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.3*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)
        tempFlag=d['flag']
        tempFlag.append('多段分割')
        d={'flag':tempFlag}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.7*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk2(self,tg,data):
        if not canUsePassive(self,data):
            return

        tempint=sample([1,2,2,2],1)[0]
        tempRandom=random()
        if tempRandom<0.22*(1+self.hit):
            if tempRandom<0.22*(1+self.hit)/(1+tg.resist): 
                if data['mode']==0:
                    my_print(data,'%s触发了掌控'%(self.name))
                tempMinus='眩晕'
                b={'结算':-1,  #回合后结算
                                           '回合':1,
                                           '驱散':0,
                                           '有益':-1,
                                           '眩晕':1,
                                           '覆盖':['眩晕']
                                           }
                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)
                
    def sk3(self,tg,data):     
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
           my_print(data,"%s对%s使用了地狱之鬼"%(self.name,tg.name))    

        d={'flag':['地狱之鬼']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.44*1.25
        damage(d,data)
        tempFlag=d['flag']
        tempFlag.append('多段分割')
        d={'flag':tempFlag}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.88*1.25
        damage(d,data)
        tempFlag=d['flag']
        tempFlag.append('多段分割')
        d={'flag':tempFlag}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.32*1.25
        damage(d,data)

class 卖药郎():
    def __init__(self,info):
        self.atki=3350
        self.dfi=392
        self.maxhpi=10254
        self.spi=112
        
        self.type='卖药郎'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']
        self.畏=[]
        
    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,3,data):
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk3(tg,data)
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了释物之形"%(self.name,tg.name))
        
        d={'flag':['释物之形','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1*1.15
        if fj:
            d['flag'].append(fj)
        damage(d,data)
        
    def sk2(self,tg,data):
        if not canUsePassive(self,data):
            return
        if random()<0.5:
            temp=1
            if '天平' not in tg.buff.keys():
                b={'结算':-1,  #回合后结算
                                   '回合':-1,
                                   '驱散':0,
                                   '有益':0,
                                   '层数':temp,
                                   }
                gainBuff(tg,'天平',b,data)
            else:
                if tg.buff['天平']['层数']==3:
                    temp=0
                tg.buff['天平']['层数']+=temp
            if data['mode']==0:
                my_print(data,'%s触发了%s的道物之真理，现有%d个天平'%(tg.name,self.name,tg.buff['天平']['层数']))
    def sk2b(self,tg,data):
        if not canUsePassive(self,data):
            return
        if '天平' not in tg.buff.keys():
            temp=0
        elif  tg.buff['天平']['层数']==1:
            temp=0.3
        elif tg.buff['天平']['层数']==2:
            temp=0.4
        elif tg.buff['天平']['层数']==3:
            temp=0.6
        if tg.hp/tg.maxhp<temp:
            b={'结算':-1,  #回合后结算
                                   '回合':2,
                                   '驱散':0,
                                   '有益':0,
                                   '覆盖':['看破','天平']
                                   }
            gainBuff(tg,'看破',b,data)
    def sk3(self,tg,data):     
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
           my_print(data,"%s对%s使用了退魔"%(self.name,tg.name))    
        if '看破' not in tg.buff.keys():
            d={'flag':['退魔']}
            d['to']=tg
            d['from']=self
            d['td']=self.atk*2.63*1.25
            damage(d,data)
        else:
            d={'flag':['退魔','退魔·看破']}
            d['to']=tg
            d['from']=self
            d['td']=min(self.atk*5,tg.hp)
            damage(d,data)
    def sk3b(self,tg,data):
        if random()<0.75:
            temp=1
            if '天平' not in tg.buff.keys():
                b={'结算':-1,  #回合后结算
                                   '回合':-1,
                                   '驱散':0,
                                   '有益':0,
                                   '层数':temp,
                                   }
                gainBuff(tg,'天平',b,data)
            else:
                if tg.buff['天平']['层数']==3:
                    temp=0
                tg.buff['天平']['层数']+=temp
            if data['mode']==0:
                my_print(data,'%s现有%d个天平'%(tg.name,tg.buff['天平']['层数']))

class 雪女():
    def __init__(self,info):
        self.atki=3048
        self.dfi=413
        self.maxhpi=10634
        self.spi=109

        self.type='雪女'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if canUseSkill(self,data) and canUseOrb(self,3,data) and len(to_select)>1:
            tg=sample(to_select,1)[0]
            self.sk3(tg,data)
            
        elif canNormalAttack(self,data):
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了雪球"%(self.name,tg.name))
        
        d={'flag':['雪球','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.20
        if fj:
            d['flag'].append(fj)
        damage(d,data)
    
    def sk1b(self,tg,data):
        tempRandom=random()
        if tempRandom<0.5*(1+self.hit):
            if tempRandom<0.5*(1+self.hit)/(1+tg.resist):
                tempMinus='雪女·减速'
                b={'结算':-1,  #回合后结算
                                   '回合':2,
                                   '驱散':1,
                                   '有益':-1,
                                   '速度':-10,
                                   '覆盖':['雪女·减速']
                                   }
                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)

    def sk2(self,data):
        if not canUsePassive(self,data):
            return
        盾值=self.maxhp*0.06*1.3
        if random()<self.crit:
            盾值*=self.critDamage
        b={'结算':-1,  #回合后结算
            '回合':1,
            '驱散':1,
            '有益':1,
            '盾':盾值,
            '覆盖':['冰甲术·盾'],
            }
        gainBuff(self,'冰甲术·盾',b,data)
    def sk2b(self,tg,data):
        if not canUsePassive(self,data):
            return
        tempRandom=random()
        if tempRandom<0.5*(1+self.hit):
            if tempRandom<0.5*(1+self.hit)/(1+tg.resist):
                tempMinus='雪女·减速'
                b={'结算':-1,  #回合后结算
                                   '回合':2,
                                   '驱散':1,
                                   '有益':-1,
                                   '速度':-10,
                                   '覆盖':['雪女·减速'],
                                   }
                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)
        
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了暴风雪"%(self.name))
        d={'flag':['aoe','暴风雪']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.3*1.2
        d['times']=3
        damage(d,data)
    def sk3b(self,tg,data):
        temp=0.08
        for buff,buffInfo in tg.buff.items():
            if (buffInfo=='速度' and buffInfo[速度]<0) or (buffInfo=='速度比' and buffInfo[速度比]<0):
                temp=0.18
        tempRandom=random()
        if tempRandom<temp*(1+self.hit):
            if tempRandom<temp*(1+self.hit)/(1+tg.resist):
                tempMinus='冰冻'
                b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':-1,
                                   '冰冻':1,
                                   '覆盖':['冰冻'],
                                   }
                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)
    def sk3c(self,tg,data):
        tempRandom=random()
        if tempRandom<0.16*(1+self.hit):
            if tempRandom<0.16*(1+self.hit)/(1+tg.resist):
                tempMinus='雪女·减速'
                b={'结算':-1,  #回合后结算
                                   '回合':2,
                                   '驱散':1,
                                   '有益':-1,
                                   '速度':-10,
                                   '覆盖':['雪女·减速'],
                                   }
                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)

class 鬼使白():
    def __init__(self,info):
        self.atki=3055
        self.dfi=423
        self.maxhpi=10254
        self.spi=116

        self.type='鬼使白'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if canUseSkill(self,data) and canUseOrb(self,3,data) and len(to_select)>1:
            tg=sample(to_select,1)[0]
            self.sk3(tg,data)
        elif canUseSkill(self,data) and canUseOrb(self,1,data) and len(to_select)==1:
            self.sk2(data)
        elif canNormalAttack(self,data):
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了活死人"%(self.name,tg.name))
        
        d={'flag':['活死人','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.20
        if fj:
            d['flag'].append(fj)
        damage(d,data)
    
    def sk1b(self,tg,data):
        tempRandom=random()
        if tempRandom<0.5*(1+self.hit):
            if tempRandom<0.5*(1+self.hit)/(1+tg.resist):
                tempMinus='活死人·减疗'
                b={'结算':-1,  #回合后结算
                                   '回合':2,
                                   '驱散':1,
                                   '有益':-1,
                                   '减疗':40,
                                   '覆盖':['活死人·减疗']
                                   }
                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)

    def sk2(self,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-1,data)
        for i,unit in enumerate(data['units']):
            if unit.alive==0 and unit.team!=self.team and not data['summonsSpecial'][i]:
                if data['mode']==0:
                    my_print(data,'%s召唤白色小鬼'%self.name)
                data['ids']+=1
                data['summonsSpecial'][i]=白色小鬼({
                'id':data['ids'],
                '名字':self.name+'的白色小鬼',
                '速度':self.sp,
                '位置':0,
                '队伍':self.team,
                '生命':self.maxhp*0.3,
                '攻击':self.atk*0.9,
                '防御':self.df,
                '暴击':0,
                '暴击伤害':1.50,
                '效果命中':0.00,
                '效果抵抗':0.00,
                '御魂':''
                    })
                    
                data['uands'].append(data['summonsSpecial'][i])
                data['action'].insert(0,data['summonsSpecial'][i])
        
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了无常夺命"%(self.name))
        d={'flag':['aoe','无常夺命']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.24*1.32
        d['times']=3
        damage(d,data)
    
    def sk3b(self,tg,data):
        temp=1
        for i in range(3):
            tempMinus='无常夺命·毒'+str(i)
            if tempMinus not in tg.buff.keys():
                temp=0
                break
        if temp:
            return 
        tempRandom=random()
        if tempRandom<0.6*(1+self.hit):
            if tempRandom<0.6*(1+self.hit)/(1+tg.resist): 
                b={'结算':-1,  #回合后结算
                                           '回合':2,
                                           '驱散':0,
                                           '有益':-1,
                                           '毒':self,
                                           '覆盖':[tempMinus]
                                           }
              
                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)

class 鬼使黑():
    def __init__(self,info):
        self.atki=3055
        self.dfi=423
        self.maxhpi=10254
        self.spi=116

        self.type='鬼使黑'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        to_select.sort(key=lambda x:x.hp/x.maxhp)
        if to_select:
            tg=to_select[0]
        if tg and tg.hp==tg.maxhp:
            tg=sample(to_select,1)[0]
        if tg and canUseSkill(self,data) and canUseOrb(self,3,data) and len(to_select)>1 and tg.hp/tg.maxhp>0.6:
            self.sk3(tg,data)
        elif tg and canNormalAttack(self,data):
            self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了惩戒"%(self.name,tg.name))
        
        d={'flag':['惩戒','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)
    
        
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了死亡宣判"%(self.name))
        d={'flag':['aoe','死亡宣判']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.28
        damage(d,data)

class 傀儡师():   
    def __init__(self,info):
        
        self.atki=2841
        self.dfi=401
        self.maxhpi=11735
        self.spi=108

        self.type='傀儡师'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']


    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,3,data):
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and self.team!=i.team:
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk3(tg,data)
            return
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)   


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了傀儡·出击"%(self.name,tg.name))
        d={'flag':['傀儡·出击','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk2(self,to,d,data):
        if not canUsePassive(self,data):
            return
        if random()<0.2 and '分摊' not in d['flag']:
            if data['mode']==0:
                my_print(data,"%s触发了傀儡·追击"%(self.name))
                newd={'flag':['傀儡·追击','针女'],
                       'from':self,
                       'to':to,
                       'td':min(to.maxhp*0.1,self.atk*1.2)
                       }
                damage(newd,data)         
    
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s对%s使用了傀儡·爆发"%(self.name,tg.name))
        d={'flag':['傀儡·爆发','杀戮']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.67
        d['times']=5
        damage(d,data) 
        
class 孟婆():
    def __init__(self,info):
        self.atki=2921
        self.dfi=428
        self.maxhpi=10709
        self.spi=115

        self.type='孟婆'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if to_select:
            tg=sample(to_select,1)[0]
        if tg and canUseSkill(self,data) and canUseOrb(self,3,data) and len(to_select)>1:
            self.sk3(tg,to_select,data)
        elif tg and canUseSkill(self,data) and canUseOrb(self,1,data) and random()<0.5:
            self.sk2(tg,data)
        elif tg and canNormalAttack(self,data):
            self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了药汤"%(self.name,tg.name))
        
        d={'flag':['药汤','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.2
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk2(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-1,data)
        if data['mode']==0:
            my_print(data,"%s对%s使用了汤盆冲撞"%(self.name,tg.name))
        d={'flag':['aoe','死亡宣判']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.3*1.2
        damage(d,data)  
    
    def sk2b(self,tg,data):
        tempRandom=random()
        if tempRandom<0.5*(1+self.hit):
            if tempRandom<0.5*(1+self.hit)/(1+tg.resist):
                tempMinus='沉默'
                b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':-1,
                                   '沉默':1,
                                   '覆盖':['沉默']
                                   }
                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)
    
    def sk3(self,tg,tgs,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s对%s使用了天降之物"%(self.name,tg.name))
        d={'flag':['天降之物']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*2.11*1.2
        damage(d,data)  
        for i in tgs:
            if i!=tg:
                d={'flag':['特殊aoe','天降之物·群体']}
                d['to']=i
                d['from']=self
                d['td']=self.atk*0.27*1.2
                damage(d,data)
    def sk3b(self,tg,data):
        tempRandom=random()
        if tempRandom<0.9*(1+self.hit):
            if tempRandom<0.9*(1+self.hit)/(1+tg.resist):
                tempMinus='沉默'
                b={'结算':-1,  #回合后结算
                                   '回合':2,
                                   '驱散':1,
                                   '有益':-1,
                                   '沉默':1,
                                   '覆盖':['沉默']
                                   }
                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)
    def sk3c(self,tg,data):
        tempRandom=random()
        if tempRandom<0.25*(1+self.hit):
            if tempRandom<0.25*(1+self.hit)/(1+tg.resist):
                tempMinus='沉默'
                b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':-1,
                                   '沉默':1,
                                   '覆盖':['沉默']
                                   }
                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)

class 犬神():
    def __init__(self,info):
        self.atki=3002
        self.dfi=432
        self.maxhpi=10254
        self.spi=109

        self.type='犬神'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']
        self.守护加攻=0

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if to_select:
            tg=sample(to_select,1)[0]
        if to_select and canUseSkill(self,data) and canUseOrb(self,3,data):
            self.sk3(to_select,data)
        elif tg and canNormalAttack(self,data):
            self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了心斩"%(self.name,tg.name))
        
        d={'flag':['心斩','普攻']}
        d['to']=tg
        d['from']=self
        if fj=='守护·反击':
            d['td']=self.atk*1.1*1.25
            d['flag'].append('反击')
        else:
            d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)


    def sk2(self,tg,data):
        tempFlag='守护·反击'
        if tempFlag not in self.buff.keys():
            if data['mode']==0:
                my_print(data,'%s触发了%s的守护反击'%(tg.name,self.name))
            data['反击'].append({'to':tg,
                                 'from':self,
                                 'flag':tempFlag,
                                })
            b={'结算':-4,  #行动后结算
                                       '回合':1,
                                       '驱散':0,
                                       '有益':0,
                                       '隐藏':1,                               
                                }
            gainBuff(self,tempFlag,b,data)
    
    def sk2b(self,tg,data):
        if self.守护加攻>=2.1:
            return
        for i in range(10000):
            tempMinus='守护·加攻'+str(i)
            if tempMinus not in self.buff.keys():
                break
        temp=tg.atk*0.3/self.atki
        self.守护加攻+=temp
        if self.守护加攻>=2.1:
            temp-=self.守护加攻-2.1
            self.守护加攻=2.1
        b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':1,
                                   '攻击':temp
                                   }
                   
        gainBuff(self,tempMinus,b,data)
    def sk2c(self,data):
        if not canUsePassive(self,data):
            return
        temp=[]
        for i in data['units']:
            if i.alive and i.team==self.team and i!=self:
                temp.append(i)
        temp.sort(key=lambda x:x.hp/x.maxhp)
        t=len(temp)//2
        for i in range(t):
            b={'结算':-3,  #不结算
                                   '回合':-1,
                                   '驱散':0,
                                   '有益':0,
                                   '守护':self
                                   }
                   
            gainBuff(temp[i],'守护',b,data)
        b={'结算':1,  #回合前结算
                                       '回合':1,
                                       '驱散':0,
                                       '有益':0,
                                       '隐藏':0,
                                       }
        gainBuff(self,'守护他人',b,data)
    def sk3(self,tgs,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了心剑乱舞"%(self.name))
        for i in range(5):
            if len(tgs)==0:
                break
            j=i%len(tgs)
            d={'flag':['特殊aoe','心剑乱舞']}
            d['to']=tgs[j]
            d['from']=self
            d['td']=self.atk*0.92*1.2
            damage(d,data)
            if tgs[j].alive==0:
                del tgs[j]

class 吸血姬():
    def __init__(self,info):
        self.atki=3002
        self.dfi=406
        self.maxhpi=10937
        self.spi=115

        self.type='吸血姬'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if to_select:
            tg=sample(to_select,1)[0]
        if canUseSkill(self,data) and canUseOrb(self,3,data) and tg and self.hp/self.maxhp<0.5:
            self.sk3(tg,data)
            
        elif canNormalAttack(self,data):
            self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了血袭"%(self.name,tg.name))
        
        hpChange(self,-self.hp*0.1,data)
        d={'flag':['血袭','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.20*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)
    

    def sk2(self,damage,d,data):
        if not canUsePassive(self,data):
            return damage
        if '血袭' in d['flag']:
            if data['mode']==0:
                my_print(data,"%s触发了血怒"%(self.name))
            return damage+damage*4*(self.maxhp-self.hp)/self.maxhp
        else:
            return damage
        
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了鲜血之拥"%(self.name))
        hpChange(self,self.maxhp*0.3,data)
        d={'flag':['鲜血之拥']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.31*1.2
        damage(d,data)
    def sk3b(self,tg,data):
        tempRandom=random()
        if tempRandom<(1+self.hit):
            if tempRandom<(1+self.hit)/(1+tg.resist):
                tempMinus='鲜血之拥·毒'
                b={'结算':-1,  #回合后结算
                                   '回合':2,
                                   '驱散':1,
                                   '有益':-1,
                                   '毒':self,
                                   '覆盖':['鲜血之拥·毒'],
                                   }
                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)

class 姑获鸟():
    def __init__(self,info):
        self.atki=3002
        self.dfi=406
        self.maxhpi=10937
        self.spi=115

        self.type='姑获鸟'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if to_select:
            tg=sample(to_select,1)[0]
        if canUseSkill(self,data) and canUseOrb(self,3,data) and tg:
            self.sk3(tg,data)
            
        elif canNormalAttack(self,data) and tg:
            self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了伞剑"%(self.name,tg.name))
        
        d={'flag':['伞剑','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.80*1.2
        if fj:
            d['flag'].append(fj)
        damage(d,data)
    

    def co_attack(self,tg,data):
        if not canUsePassive(self,data):
            return
        if random()>=0.3:
            return
        if isEnemy(self,tg,self):
            self.sk1(tg,data,'协战')
        else:
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)
        
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了天翔鹤斩"%(self.name))
        d={'flag':['天翔鹤斩','aoe']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.33*1.24
        d['times']=3
        damage(d,data)
        temp=d['flag']
        temp.remove('aoe')
        temp.append('多段分割')
        d={'flag':temp}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.88*1.24
        damage(d,data)

class 络新妇():
    def __init__(self,info):
        self.atki=3216
        self.dfi=397
        self.maxhpi=10254
        self.spi=112

        self.type='络新妇'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if to_select:
            tg=sample(to_select,1)[0]
        if canUseSkill(self,data) and canUseOrb(self,3,data) and len(to_select)>=2:
            self.sk3(tg,data)
            
        elif canNormalAttack(self,data) and tg:
            self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了毒针"%(self.name,tg.name))
        
        d={'flag':['毒针','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)
    

    def sk2(self,tg,data):
        if not canUsePassive(self,data):
            return
        tempRandom=random()
        if tempRandom<0.4*(1+self.hit):
            if tempRandom<0.4*(1+self.hit)/(1+tg.resist):
                tempMinus='蜘蛛印记'
                b={'结算':-1,  #回合后结算
                                   '回合':2,
                                   '驱散':1,
                                   '有益':-1,
                                   'from':self,
                                   '覆盖':['蜘蛛印记'],
                                   }
                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)        
    def sk2b(self,tg,data):
        if data['mode']==0:
            my_print(data,"%s对%s造成了蜘蛛印记伤害"%(self.name,tg.name))
        
        d={'flag':['蜘蛛印记伤害']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk
        damage(d,data)
        
        
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了噬心食髓"%(self.name))
        d={'flag':['噬心食髓','aoe']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.27*1.2
        damage(d,data)
    
    def sk3b(self,tg,data):
        if self.sp<=tg.sp:
            return
        tempRandom=random()
        temp=0.2
        if self.sp>tg.sp:
            temp+=(self.sp-tg.sp)//5*0.01
        if tempRandom<temp*(1+self.hit):
            if tempRandom<temp*(1+self.hit)/(1+tg.resist):
                tempMinus='眩晕'
                b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':-1,
                                   '覆盖':['眩晕'],
                                   }
                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)        

class 骨女():
    def __init__(self,info):
        self.atki=2948
        self.dfi=454
        self.maxhpi=9912
        self.spi=107

        self.type='骨女'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if to_select:
            tg=sample(to_select,1)[0]
        if canUseSkill(self,data) and canUseOrb(self,3,data) and tg:
            self.sk3(tg,data)
            
        elif canNormalAttack(self,data) and tg:
            self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了骨刃"%(self.name,tg.name))
        
        d={'flag':['骨刃','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)
    

    def sk2(self,data):
        if '触发过怨气' in self.buff.keys() or not canUsePassive(self,data):
            return
        temp=0
        for i in range(6):
            tempName='怨气'+str(i)
            if tempName not in self.buff.keys():
                temp=1
                break
        if temp:
            b={'结算':-1,  #回合后结算
                                   '回合':-1,
                                   '驱散':1,
                                   '有益':1,
                                   '攻击':0.05
                                   }
            gainBuff(self,tempName,b,data)
            tempFlag='触发过怨气'
            b={'结算':-4,  #行动后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':0,
                                   '隐藏':1,
                                
                            }
            gainBuff(self,tempFlag,b,data)
            if data['mode']==0:
                my_print(data,'%s触发了怨生'%(self.name))
        
    def sk2b(self,data):
        if 'cd' in self.buff.keys() and not canUsePassive(self,data):
            return
        temp=0
        for i in range(6):
            tempName='怨气'+str(i)
            if tempName in self.buff.keys():
                temp+=1
        if temp<4:
            return
        if data['mode']==0:
            my_print(data,'%s触发怨生·复活'%self.name)
        
        self.alive=1
        data['action'].append(self)
        data['action'].sort(key=lambda x:(x.po,x.sp,-x.id))
        
        b={'结算':-1,  #回合后结算
                                   '回合':3,
                                   '驱散':0,
                                   '有益':0,
                                   '隐藏':0,
                                   }
        gainBuff(self,'cd',b,data)
        h={'flag':[]}
        h['to']=self
        h['from']=self
        h['heal']=self.maxhp*0.2        
        heal(h,data)
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了一步一息"%(self.name))
        d={'flag':['一步一息']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.78*1.2
        d['times']=3
        damage(d,data)
    
class 鬼女红叶():
    def __init__(self,info):
        self.atki=2967
        self.dfi=432
        self.maxhpi=10291
        self.spi=114

        self.type='鬼女红叶'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if canUseSkill(self,data) and canUseOrb(self,3,data) and len(to_select)>1:
            tg=sample(to_select,1)[0]
            self.sk3(tg,data)
            
        elif canNormalAttack(self,data):
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了红枫"%(self.name,tg.name))
        
        d={'flag':['红枫','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.20
        if fj:
            d['flag'].append(fj)
        damage(d,data)
    
    def sk1b(self,tg,data):
        tempRandom=random()
        if '红枫娃娃' in tg.buff.keys():
            return 
        if tempRandom<0.3*(1+self.hit):
            if tempRandom<0.3*(1+self.hit)/(1+tg.resist):
                tempMinus='红枫娃娃'
                b={'结算':-1,  #回合后结算
                                   '回合':-1,
                                   '驱散':1,
                                   '有益':-1,
                                   'from':self,
                                   '覆盖':['红枫娃娃']
                                   }
                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)

    def sk2(self,data):
        if not canUsePassive(self,data):
            return
        d={}
        d['times']=0
        for i in data['units']:
            if i.team!=self.team and i.alive and '红枫娃娃' in i.buff.keys():
                removeBuff(i,'红枫娃娃',data)
                d['times']+=1
        if d['times']:
            my_print(data,'%s触发了爆炸之咒'%self.name)
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and self.team!=i.team:
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                d['from']=self
                d['to']=tg
                d['flag']=['aoe','爆炸之咒']
                d['td']=self.atk*0.6
                damage(d,data)
        
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了死亡之舞"%(self.name))
        d={'flag':['aoe','死亡之舞']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.32*1.2
        damage(d,data)

class 黑童子():
    def __init__(self,info):
        self.atki=3377
        self.dfi=384
        self.maxhpi=9912
        self.spi=109

        self.type='黑童子'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if canUseSkill(self,data) and canUseOrb(self,3,data):
            tg=sample(to_select,1)[0]
            self.sk3(tg,data)
            
        elif canNormalAttack(self,data):
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了罪罚·黑"%(self.name,tg.name))
        
        d={'flag':['罪罚·黑','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)
    
    def sk2(self,tg,data):
        if not canUsePassive(self,data) or random()>0.2:
            return
        tempFlag='魂之怒火'
        if tempFlag not in self.buff.keys():
            if data['mode']==0:
                my_print(data,'%s触发了魂之怒火'%(self.name))
            data['反击'].append({'to':tg,
                                 'from':self,
                                 'flag':tempFlag,
                                })
            b={'结算':-4,  #行动后结算
                                       '回合':1,
                                       '驱散':0,
                                       '有益':0,
                                       '隐藏':1,                               
                                }
            gainBuff(self,tempFlag,b,data)
        
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了连斩"%(self.name))
        d={'flag':['aoe','连斩']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.83*1.2
        d['times']=floor((1-self.hp/self.maxhp)/0.3)+1
        damage(d,data)
    def sk3b(self,tg,data,td=0):
        if data['mode']==0:
            my_print(data,"%s使用了连斩"%(self.name))
        d={'flag':['aoe','连斩']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.83*1.2
        if td:
            d['td']=td
        d['times']=floor((1-self.hp/self.maxhp)/0.3)+1
        damage(d,data)

class 棺材():
    def __init__(self,info):
        self.atki=0
        self.dfi=0
        self.maxhpi=0
        self.spi=0
        
        self.type='棺材'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']
        self.index=info['index']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)


    def move(self,data):
        pass
            
    def sk1(self,data):
        self.hp=0
        die(self,'棺材自杀',data)

    def sk2(self,data):
        tg=data['units'][self.index]
        tg.alive=1
        tg.hp=tg.maxhp
        data['action'].append(tg)
        data['action'].sort(key=lambda x:(x.po,x.sp,-x.id))
        if data['mode']==0:
            my_print(data,"%s满血复活"%(tg.name))    
        temp='复活过'
        b={'结算':-1,  #回合后结算
                                   '回合':-1,
                                   '驱散':0,
                                   '有益':0,
                                   '隐藏':1
                                   }
        gainBuff(tg,temp,b,data)            
        
class 跳跳哥哥():
    def __init__(self,info):
        self.atki=3055
        self.dfi=406
        self.maxhpi=10709
        self.spi=119

        self.type='跳跳哥哥'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        to_select=[]
        for i,unit in enumerate(data['uands']):
            if not unit.alive and self.team==unit.team and not data['summonsSpecial'][i]:
                to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
        if canUseSkill(self,data) and canUseOrb(self,3,data) and tg:
            self.sk3(data)
        elif canNormalAttack(self,data):
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and self.team!=i.team:
                    to_select.append(i)
            if to_select:
                    tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了棺击"%(self.name,tg.name))
        
        d={'flag':['棺击','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        if fj=='不弃反击':
            d['flag'].append('反击')
        damage(d,data)
    
    def sk1b(self,tg,data):
        tempRandom=random()
        if tempRandom<1*(1+self.hit):
            if tempRandom<1*(1+self.hit)/(1+tg.resist):
                if data['mode']==0:
                    my_print(data,"%s触发%s被动不弃"%(tg.name,self.name))
                b={'结算':-1,  #回合后结算
                                       '回合':1,
                                       '驱散':0,
                                       '有益':-1,
                                       '眩晕':0,
                                       '覆盖':['眩晕']
                                       }
                gainBuff(tg,'眩晕',b,data)
            else:
                resisted(tg,self,data)
        
    def sk3(self,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        temp=[]
        for i,unit in enumerate(data['units']):
            if unit.alive==0 and unit.team==self.team and not data['summonsSpecial'][i]:
                temp.append((i,unit))
        if temp:
            tempTotal=len(temp)
            my_print(data,'%s召唤了%d个棺材'%(self.name,tempTotal))
            for i,unit in temp:
                if data['mode']==0:
                    my_print(data,'%s在%s的位置上召唤棺材'%(self.name,unit.name))
                data['ids']+=1
                data['summonsSpecial'][i]=棺材({
                'id':data['ids'],
                '名字':self.name+'为'+unit.name+'准备的棺材',
                '速度':unit.sp,
                '位置':0,
                '队伍':self.team,
                '生命':unit.maxhp*0.3+self.maxhp*0.3/tempTotal,
                '攻击':unit.atk,
                '防御':unit.df,
                '暴击':0,
                '暴击伤害':1.50,
                '效果命中':0.00,
                '效果抵抗':0.00,
                '御魂':'',
                'index':i,
                    })
                    
                data['uands'].append(data['summonsSpecial'][i])
                data['action'].insert(0,data['summonsSpecial'][i])

class 海坊主():
    def __init__(self,info):
        self.atki=3055
        self.dfi=428
        self.maxhpi=10140
        self.spi=109

        self.type='海坊主'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if canUseSkill(self,data) and canUseOrb(self,3,data) and len(to_select)>1:
            tg=sample(to_select,1)[0]
            self.sk3(tg,data)
            
        elif canNormalAttack(self,data):
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了水龙卷"%(self.name,tg.name))
        
        d={'flag':['水龙卷','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk2(self,dmg,data):
        if not canUsePassive(self,data):
            return
        tg=None
        to_select=[]
        for i in data['units']:
            if i.alive and self.team==i.team:
                to_select.append(i)
        to_select.sort(key=lambda x:x.hp/x.maxhp)
        if to_select and to_select[0].hp==to_select[0].maxhp:
            tg=sample(to_select,1)[0]
        elif to_select:
            tg=to_select[0] 
        if tg:
            if data['mode']==0:
                my_print(data,"%s触发了对%s的祝福之水"%(self.name,tg.name))
            h={'flag':['祝福之水']}
            h['to']=tg
            h['from']=self
            h['heal']=dmg
            heal(h,data)
        
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了巨浪"%(self.name))
        d={'flag':['aoe','巨浪']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.31*1.24
        d['times']=3
        damage(d,data)
  
class 判官():
    def __init__(self,info):
        self.atki=3028
        self.dfi=419
        self.maxhpi=10482
        self.spi=118
        
        self.type='判官'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']
        self.sk1times=0

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,3,data):
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk3(tg,data)
            
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了墨笔夺魂"%(self.name,tg.name))
        
        d={'flag':['墨笔夺魂','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)
    
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了死亡宣告"%(self.name))
        d={'flag':['aoe','死亡宣告']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        damage(d,data)
    
    def sk3b(self,tg,data):
        if not canUsePassive(self,data):
            return
        tempRandom=random()
        if tempRandom<1*(1+self.hit):
            if tempRandom<1*(1+self.hit)/(1+tg.resist):
                b={'结算':-1,  #回合后结算
                                       '回合':1,
                                       '驱散':0,
                                       '有益':-1,
                                       'from':self,
                                       '覆盖':['死亡宣告·爆炸']
                                       }
                gainBuff(tg,'死亡宣告·爆炸',b,data)
            else:
                resisted(tg,self,data)

class 妖狐():
    def __init__(self,info):
        self.atki=3055
        self.dfi=419
        self.maxhpi=10368
        self.spi=115

        self.type='妖狐'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if to_select:
            tg=sample(to_select,1)[0]
        if canUseSkill(self,data) and canUseOrb(self,3,data) and tg:
            self.sk3(tg,data)
            
        elif canNormalAttack(self,data) and tg:
            self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了风刃"%(self.name,tg.name))
        
        d={'flag':['风刃','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)
    

    def sk2(self,data):
        if not canUsePassive(self,data):
            return
        temp=0
        for i in range(5):
            tempName='聚气'+str(i)
            if tempName not in self.buff.keys():
                temp=1
                break
        if temp:
            b={'结算':-1,  #回合后结算
                                   '回合':-1,
                                   '驱散':1,
                                   '有益':1,
                                   '攻击':0.06
                                   }
            gainBuff(self,tempName,b,data)
        
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了狂风刃卷"%(self.name))

        d={'flag':['狂风刃卷']}
        d['to']=tg
        d['from']=self
        d['times']=2
        while random()<0.5:
            d['times']+=2
        d['td']=self.atk*0.66*1.2
        damage(d,data)

class 妖琴师():
    def __init__(self,info):
        self.atki=2573
        self.dfi=410
        self.maxhpi=12646
        self.spi=120

        self.type='妖琴师'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if to_select:
            tg=sample(to_select,1)[0]
        if canUseSkill(self,data) and canUseOrb(self,3,data) and tg:
            self.sk3(tg,data)
            return
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team==i.team and i!=self:
                to_select.append(i)
        if to_select:
            tg=sample(to_select,1)[0]
        if canUseSkill(self,data) and canUseOrb(self,2,data) and tg:
            self.sk2(tg,data)
        if canNormalAttack(self,data) and tg:
            self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了惊弦"%(self.name,tg.name))
        
        d={'flag':['惊弦','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)
    

    def sk2(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-2,data)
        if data['mode']==0:
            my_print(data,"%s使用了余音"%(self.name))
    
        to_select=[]
        for i in data['uands']:
            if i.alive and tg.team==i.team:
                to_select.append(i)
        
        if to_select:
            for i in to_select:
                b={'结算':-1,  #回合后结算
                                       '回合':1,
                                       '驱散':1,
                                       '有益':1,
                                       '速度':20
                                       }
                gainBuff(i,'余音·加速',b,data)
        gainExtraTurn(tg,data)
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了疯魔琴心"%(self.name))

        d={'flag':['aoe','疯魔琴心']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.85*1.2
        damage(d,data)
    
    def sk3b(self,tg,data):
        if random()<0.2:
            tg.po=0
            my_print(data,'%s的行动条被清空'%(tg.name))
    def sk3c(self,tg,data):
        tempRandom=random()
        if tempRandom<0.2*(1+self.hit):
            if tempRandom<0.2*(1+self.hit)/(1+tg.resist):
                tempMinus='混乱'
                b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':1,
                                   '有益':-1,
                                   '混乱':1,
                                   '覆盖':['混乱'],
                                   }

                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)
                
class 追月神():
    def __init__(self,info):
        self.atki=2305
        self.dfi=450
        self.maxhpi=12760
        self.spi=109
        
        self.type='追月神'
        
        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

        
    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,2,data):
            self.sk3(data)
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了邀月"%(self.name,tg.name))
        
        d={'flag':['邀月','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)
    
    def sk1b(self,data):
        self.po+=0.2
        data['action'].sort(key=lambda x:(x.po,x.sp,-x.id))
        if self.po>=1:
            self.po=1
        my_print(data,'%s触发了邀月自拉条，现在的行动条位置我%.2f'%(self.name,self.po))
    def sk2(self,data):
        if not canUsePassive(self,data):
            return        
        b={'结算':1,  #回合前结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':1,
                                   '免控':1,
                                   }
        gainBuff(self,'清辉月华·免控',b,data)
    def sk2b(self,data):
        data['orbPo'][self.team]+=4
        my_print(data,'%s推动鬼火行动条'%self.name)
        b={'结算':-1,  #回合后结算
                                       '回合':1,
                                       '驱散':0,
                                       '有益':1,
                                       '覆盖':['追月·幻境']
                                       }
        gainBuff(self,'追月·幻境',b,data)
        for i in data['uands']:
            if i.team==self.team:
                b1={'结算':-3, #不结算
                    '回合':-1,
                    '驱散':0,
                    '有益':1,
                    '攻击':0.2,
                    '速度':20,
                    '覆盖':['月之祝福·加攻加速']
                    }
                gainBuff(i,'月之祝福·加攻加速',b1,data)
    def sk3(self,data):     
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-2,data)
        b={'结算':-1,  #回合后结算
                                       '回合':1,
                                       '驱散':0,
                                       '有益':1,
                                       '覆盖':['追月·幻境']
                                       }
        gainBuff(self,'追月·幻境',b,data)
        for i in data['uands']:
            if i.team==self.team:
                b1={'结算':-3, #不结算
                    '回合':-1,
                    '驱散':0,
                    '有益':1,
                    '攻击':0.2,
                    '速度':20,
                    '覆盖':['月之祝福·加攻加速']
                    }
                gainBuff(i,'月之祝福·加攻加速',b1,data)

class 清姬():
    def __init__(self,info):
        self.atki=2412
        self.dfi=467
        self.maxhpi=11849
        self.spi=105

        self.type='清姬'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if canUseSkill(self,data) and canUseOrb(self,3,data) and len(to_select)>1:
            tg=sample(to_select,1)[0]
            self.sk3(tg,data)
        elif canNormalAttack(self,data):
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了蛇行击"%(self.name,tg.name))
        
        d={'flag':['蛇行击','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.86*1.20
        if fj:
            d['flag'].append(fj)
        damage(d,data)
        
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了焚身之火"%(self.name))
        d={'flag':['aoe','焚身之火']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.36*1.32
        d['times']=3
        damage(d,data)
    
    def sk3b(self,tg,data):
        temp=1
        for i in range(3):
            tempMinus='焚身之火·毒'+str(i)
            if tempMinus not in tg.buff.keys():
                temp=0
                break
        if temp:
            return 
        tempRandom=random()
        if tempRandom<0.5*(1+self.hit):
            if tempRandom<0.5*(1+self.hit)/(1+tg.resist): 
                b={'结算':-1,  #回合后结算
                                           '回合':2,
                                           '驱散':0,
                                           '有益':-1,
                                           '毒':self,
                                           '覆盖':[tempMinus]
                                           }
                if canUsePassive(self,data):
                    b['防御']=-0.08
                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)

class 青坊主():
    def __init__(self,info):
        self.atki=2385
        self.dfi=415
        self.maxhpi=13330
        self.spi=118

        self.type='青坊主'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']
        self.佛光=0

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if to_select:
            tg=sample(to_select,1)[0]
        if canUseSkill(self,data) and canUseOrb(self,3,data) and len(to_select)>=2:
            self.sk3(tg,data)
            
        elif canNormalAttack(self,data) and tg:
            self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了摩诃"%(self.name,tg.name))
        
        d={'flag':['摩诃','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)
    

    def sk2(self,data,ts=0):
        if not canUsePassive(self,data) and not ts:
            return
        self.佛光+=1
        if self.佛光>=6:
            self.佛光=6
        tempMinus='佛光'
        for i in data['units']:
            if i.team==self.team and i.alive:
                b={'结算':-1,  #回合后结算
                                   '回合':-1,
                                   '驱散':0,
                                   '有益':1,
                                   '层数':self.佛光,
                                   '抵抗':self.佛光*0.15,
                                   '覆盖':['佛光'],
                                   }
                gainBuff(i,tempMinus,b,data)
                   
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了禅心"%(self.name))
        d={'flag':['禅心','aoe']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.66*1.2*(1-(self.佛光-1)*0.1)
        damage(d,data)
        dispel(tg,2,self,data)        

class 镰鼬():
    def __init__(self,info):
        self.atki=2680
        self.dfi=432
        self.maxhpi=11621
        self.spi=117

        self.type='镰鼬'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']
        self.佛光=0

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if to_select:
            tg=sample(to_select,1)[0]
        if canUseSkill(self,data) and canUseOrb(self,3,data) and '兄弟之绊·加攻' not in self.buff.keys():
            self.sk3(tg,data)
            
        elif canNormalAttack(self,data) and tg:
            self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了胖揍"%(self.name,tg.name))
        
        d={'flag':['胖揍','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.2
        if fj:
            d['flag'].append(fj)
        damage(d,data)
        self.sk2(data)
    def sk1b(self,tg,data):
        tempRandom=random()
        if tempRandom<0.2*(1+self.hit):
            if tempRandom<0.2*(1+self.hit)/(1+tg.resist):
                if data['mode']==0:
                    my_print(data,"%s触发%s的胖揍"%(tg.name,self.name))
                tempInt=randint(1,3)
                if tempInt==1:
                    b={'结算':-1,  #回合后结算
                                           '回合':1,
                                           '驱散':0,
                                           '有益':-1,
                                           '眩晕':0,
                                           '覆盖':['眩晕']
                                           }
                    gainBuff(tg,'眩晕',b,data)
                if tempInt==2:
                    b={'结算':-1,  #回合后结算
                                           '回合':2,
                                           '驱散':1,
                                           '有益':-1,
                                           '胖揍·毒':self,
                                           '覆盖':['胖揍·毒']
                                           }
                    gainBuff(tg,'胖揍·毒',b,data)
                if tempInt==3:
                    b={'结算':-1,  #回合后结算
                                           '回合':2,
                                           '驱散':1,
                                           '有益':-1,
                                           '防御':-0.3,
                                           '覆盖':['胖揍·减防']
                                           }
                    gainBuff(tg,'胖揍·减防',b,data)
            else:
                resisted(tg,self,data)

    def sk2(self,data):
        if not canUsePassive(self,data):
            return
        if canMove(self,data) and random()<0.3:
            gainExtraTurn(self,data)
                   
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了兄弟之绊"%(self.name))
        for i in data['uands']:
            if i.alive and i.team==self.team:
                i.po+=0.3
                if i.po>1:
                    i.po=1
                data['action'].sort(key=lambda x:(x.po,x.sp,-x.id))
                b={'结算':-1,  #回合后结算
                                           '回合':2,
                                           '驱散':1,
                                           '有益':1,
                                           '攻击':0.25,
                                           '覆盖':[]
                                           }
                gainBuff(i,'兄弟之绊·加攻',b,data)
                b={'结算':-1,  #回合后结算
                                           '回合':2,
                                           '驱散':1,
                                           '有益':1,
                                           '抵抗':0.2,
                                           '覆盖':[]
                                           }
                gainBuff(i,'兄弟之绊·加抗',b,data)
        self.sk2(data)

class 二口女():
    def __init__(self,info):
        self.atki=2626
        self.dfi=445
        self.maxhpi=11507
        self.spi=116

        self.type='二口女'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if to_select:
            tg=sample(to_select,1)[0]
        if canUseSkill(self,data) and canUseOrb(self,3,data) and tg:
            self.sk3(tg,data)
            
        elif canNormalAttack(self,data) and tg:
            self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了意外袭击"%(self.name,tg.name))
        
        d={'flag':['意外袭击','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)
    

    def sk2(self,data):
        if not canUsePassive(self,data):
            return
        temp=1
        if random()<0.66:
            if '子弹' not in self.buff.keys():
                b={'结算':-1,  #回合后结算
                                   '回合':-1,
                                   '驱散':1,
                                   '有益':1,
                                   '层数':1,
                                   }
                gainBuff(self,'子弹',b,data)
            else:
                if self.buff['子弹']['层数']==6:
                    temp=0
                self.buff['子弹']['层数']+=temp
            my_print(data,'%s触发恐惧，现有%d层子弹印记'%(self.name,self.buff['子弹']['层数']))
    
    def sk2b(self,data):
        temp=4
        if random()<2:
            if '子弹' not in self.buff.keys():
                b={'结算':-1,  #回合后结算
                                   '回合':-1,
                                   '驱散':1,
                                   '有益':1,
                                   '层数':temp,
                                   }
                gainBuff(self,'子弹',b,data)
            else:
                if self.buff['子弹']['层数']==6:
                    temp=0
                self.buff['子弹']['层数']+=temp
            my_print(data,'%s触发恐惧，现有%d层子弹印记'%(self.name,self.buff['子弹']['层数']))        
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了歉意"%(self.name))

        d={'flag':['歉意','特殊aoe']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.63
        damage(d,data)
        
        d['flag'].append('多段分割')
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if to_select:
            d['to']=sample(to_select,1)[0]        
        damage(d,data)
        
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if to_select:
            d['to']=sample(to_select,1)[0]        
        d['times']=1
        damage(d,data)
        
        d['td']*=1.2
        while '子弹' in self.buff.keys():
            print(self.buff['子弹']['层数'])
            self.buff['子弹']['层数']-=1
                
            to_select=[]
            for i in data['uands']:
                if i.alive and self.team!=i.team:
                    to_select.append(i)
            if to_select:
                d['to']=sample(to_select,1)[0]        
            d['times']=1
            damage(d,data)
            if self.buff['子弹']['层数']==0:
                removeBuff(self,'子弹',data)

class 弈():
    def __init__(self,info):
        self.atki=3002
        self.dfi=445
        self.maxhpi=9912
        self.spi=106

        self.type='弈'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']
        self.黑白=0

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if to_select:
            tg=sample(to_select,1)[0]
        if canUseSkill(self,data) and canUseOrb(self,3,data) and tg:
            self.sk3(tg,data)
            
        elif canNormalAttack(self,data) and tg:
            self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了征子"%(self.name,tg.name))
        
        d={'flag':['征子','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.2
        if fj:
            d['flag'].append(fj)
        damage(d,data)
        self.黑白=1-self.黑白

    def sk2(self,tg,data):
        if not canUsePassive(self,data):
            return
        tempRandom=random()
        if tempRandom<1*(1+self.hit):
            if tempRandom<1*(1+self.hit)/(1+tg.resist):

                if data['mode']==0:
                    my_print(data,"%s触发%s被动气合"%(tg.name,self.name))
                temp=0
                for i in range(4):
                    tempName='气合'+str(i)
                    if tempName not in tg.buff.keys():
                        temp=1
                        break
                if temp:      
                    b={'结算':-1,  #回合后结算
                                               '回合':-1,
                                               '驱散':0,
                                               '有益':-1,
                                               '气合':deepcopy(self.黑白),
                                               }
                    if self.黑白==0:
                        b['受到伤害增加']=0.05
                    else:
                        b['造成伤害减少']=0.05
                    gainBuff(tg,tempName,b,data)
                else:
                    for i in range(4):
                        tempName='气合'+str(i)
                        if tg.buff[tempName]['气合']!=self.黑白:
                            tg.buff[tempName]['气合']=self.黑白
                            break
            else:
                resisted(tg,self,data)
        temp=1
        tempbw=-1
        for i in range(4):
            tempName='气合'+str(i)
            if tempName not in tg.buff.keys():
                temp=0
                break
            if tempbw==-1:
                tempbw=tg.buff[tempName]['气合']
            if tg.buff[tempName]['气合']!=tempbw:
                temp=0
                break
        if temp:
            my_print(data,'%s触发了气合·四子同色'%(tg.name))
            d={'flag':['气合']}
            d['to']=tg
            d['from']=self
            d['td']=self.atk*6
            damage(d,data)
            for i in range(4):            
                removeBuff(tg,'气合'+str(i),data)
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了神之一手"%(self.name))

        d={'flag':['神之一手','特殊aoe']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.42*1.2
        damage(d,data)
        self.黑白=1-self.黑白
        d['flag'].append('多段分割')
        for _ in range(8):
                
            to_select=[]
            for i in data['uands']:
                if i.alive and self.team!=i.team:
                    to_select.append(i)
            if to_select:
                d['to']=sample(to_select,1)[0]        
            d['times']=1
            damage(d,data)
            self.黑白=1-self.黑白

class 白狼():
    def __init__(self,info):
        self.atki=3082
        self.dfi=397
        self.maxhpi=10823
        self.spi=112

        self.type='白狼'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if to_select:
            tg=sample(to_select,1)[0]
        if canUseSkill(self,data) and canUseOrb(self,3,data) and tg:
            self.sk3(tg,data)
            
        elif canNormalAttack(self,data) and tg:
            self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了文射"%(self.name,tg.name))
        
        d={'flag':['文射','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk2(self,data):
        if not canUsePassive(self,data):
            return
        b={'结算':1,  #回合前结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':1,
                                   }
        gainBuff(self,'冥想',b,data)
    def sk2b(self,data):
        if not canUsePassive(self,data):
            return
        if '冥想' in self.buff.keys():
            b2={'结算':-1,  #回合后结算
                                       '回合':1,
                                       '驱散':1,
                                       '有益':1,
                                       '暴伤':0.2,
                                       }
            gainBuff(self,'冥想·加爆',b2,data)
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了无我"%(self.name))

        d={'flag':['无我']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*2.37*1.2
        damage(d,data)

class 樱花妖():
    def __init__(self,info):
        self.atki=2385
        self.dfi=397
        self.maxhpi=13785
        self.spi=99

        self.type='樱花妖'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if to_select:
            tg=sample(to_select,1)[0]
        if canUseSkill(self,data) and canUseOrb(self,3,data) and tg:
            self.sk3(tg,data)       
        elif canNormalAttack(self,data) and tg:
            self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了樱落"%(self.name,tg.name))
        
        d={'flag':['樱落','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)

    def sk2(self,tg,data):
        if not canUsePassive(self,data):
            return
        回复量=self.maxhp*0.08
        if random()<0.2:
            回复量*=2
        if random()<self.crit:
            回复量*=self.critDamage
        h={'flag':['复苏']}
        h['to']=tg
        h['from']=self
        h['heal']=回复量
        heal(h,data)
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了樱吹雪"%(self.name))

        d={'flag':['樱吹雪','aoe']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.76*1.1
        damage(d,data)
    def sk3b(self,tg,data):
        tempRandom=random()
        if tempRandom<0.5*(1+self.hit):
            if tempRandom<0.5*(1+self.hit)/(1+tg.resist): 
                tempMinus='衰败'
                b={'结算':-1,  #回合后结算
                                           '回合':2,
                                           '驱散':0,
                                           '有益':-1,
                                           '减疗':0.5,
                                           '覆盖':['衰败']
                                           }
              
                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)
        temp1=0
        for buff,buffInfo in tg.buff.items():
            if buffInfo['有益']==1 and buffInfo['驱散']==1:
                temp1+=1
                
        dispel(tg,-1,self,data)
        
        if temp1:
            tempRandom=random()
            if tempRandom<0.25*(1+self.hit):
                if tempRandom<0.25*(1+self.hit)/(1+tg.resist): 
                    tempMinus='睡眠'
                    b={'结算':-1,  #回合后结算
                                               '回合':1,
                                               '驱散':1,
                                               '有益':-1,
                                               '睡眠':0,
                                               '覆盖':['睡眠']
                                               }
                  
                    gainBuff(tg,tempMinus,b,data)
                else:
                    resisted(tg,self,data)  

class 万年竹():
    def __init__(self,info):
        self.atki=3270
        self.dfi=392
        self.maxhpi=10140
        self.spi=115

        self.type='万年竹'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']


    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        to_select=[]
        for i in data['uands']:
            if i.alive and i!=self and self.team==i.team:
                to_select.append(i)
        if to_select and canUseSkill(self,data) and canUseOrb(self,3,data):
            self.sk3(to_select,data)
        else:
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and self.team==i.team:
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg and canNormalAttack(self,data):
                self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了笛中剑"%(self.name,tg.name))
        
        d={'flag':['笛中剑','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)
        
    def sk2(self,tg,frm,data):
        tempFlag='竹叶守护·反击%d'%(frm.id)
        if tempFlag not in self.buff.keys() and (self==frm or random()<0.6):
            if data['mode']==0:
                my_print(data,'%s触发了%s的竹叶守护反击'%(tg.name,self.name))
            data['反击'].append({'to':tg,
                                 'from':self,
                                 'flag':tempFlag,
                                })
            b={'结算':-4,  #行动后结算
                                       '回合':1,
                                       '驱散':0,
                                       '有益':0,
                                       '隐藏':1,                               
                                }
            gainBuff(self,tempFlag,b,data)
    

    def sk2b(self,data):
        if not canUsePassive(self,data):
            return

        b={'结算':1,  #回合前结算
                                   '回合':-1,
                                   '驱散':0,
                                   '有益':0,
                                   '守护':self
                                   }
                   
        gainBuff(self,'竹叶守护',b,data)
    def sk3(self,tgs,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        temp=[]
        for i in tgs:
            b={'结算':-3,  #不结算
                                   '回合':-1,
                                   '驱散':0,
                                   '有益':0,
                                   '守护':self,
                                   '攻击':self.atk*0.15/i.atki,
                                   
                                   }
                   
            gainBuff(i,'竹叶守护',b,data)
        b={'结算':1,  #回合前结算
                                       '回合':1,
                                       '驱散':0,
                                       '有益':0,
                                       '隐藏':1,
                                       '覆盖':['竹叶守护他人']
                                       }
        gainBuff(self,'竹叶守护他人',b,data)                  

class 夜叉():
    def __init__(self,info):
        self.atki=3268
        self.dfi=392
        self.maxhpi=10139
        self.spi=110

        self.type='夜叉'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if to_select:
            tg=sample(to_select,1)[0]
        if canUseSkill(self,data) and canUseOrb(self,3,data) and tg:
            self.sk3(tg,data)
            
        elif canNormalAttack(self,data) and tg:
            self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了屠戮"%(self.name,tg.name))
        
        d={'flag':['屠戮','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)
    

    def sk2(self,data):
        if not canUsePassive(self,data) or random()<0.5:
            return
        tempName='鬼魅'+str(0)
        i=1
        while tempName in self.buff.keys():
            tempName='鬼魅'+str(i)
            i+=1
        
        b={'结算':-1,  #回合后结算
                                   '回合':2,
                                   '驱散':1,
                                   '有益':1,
                                   '速度':20,
                                   }
        gainBuff(self,tempName,b,data)
        
    def sk3(self,tg,data,flag=['黄泉之海']):
        if '明灯·增伤' not in self.buff.keys() and '多段分割' not in flag:
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s对%s使用了黄泉之海"%(self.name,tg.name))

        d={'flag':flag}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.98*1.2
        damage(d,data)
        if random()<0.5:
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive and self.team!=i.team:
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                if '多段分割' not in flag:
                    d['flag'].append('多段分割')
                self.sk3(tg,data,d['flag'])
            
class 烟烟罗():
    def __init__(self,info):
        self.atki=3162
        self.dfi=392
        self.maxhpi=10596
        self.spi=112

        self.type='烟烟罗'        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        tg=None
        to_select=[]
        for i in data['uands']:
            if i.alive and self.team!=i.team:
                to_select.append(i)
        if to_select:
            tg=sample(to_select,1)[0]
        if canUseSkill(self,data) and canUseOrb(self,3,data) and tg:
            self.sk3(tg,data)
            
        elif canNormalAttack(self,data) and tg:
            self.sk1(tg,data)
        


    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        if data['mode']==0:
            my_print(data,"%s对%s使用了蹂躏"%(self.name,tg.name))
        
        d={'flag':['蹂躏','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.80*1.2
        if fj:
            d['flag'].append(fj)
        damage(d,data)
    

    def sk2(self,tg,data):
        if not canUsePassive(self,data):
            return
        tempRandom=random()
        if tempRandom<0.1*(1+self.hit):
            if tempRandom<0.1*(1+self.hit)/(1+tg.resist):
                tempMinus='变形·烟雾小鬼'
                b={'结算':-1,  #回合后结算
                                   '回合':1,
                                   '驱散':0,
                                   '有益':-1,
                                   '变形':1,
                                   '封印被动':1,
                                   '覆盖':[],
                                   }
                gainBuff(tg,tempMinus,b,data)
            else:
                resisted(tg,self,data)
        
    def sk3(self,tg,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-3,data)
        if data['mode']==0:
            my_print(data,"%s使用了烟之鬼"%(self.name))
        d={'flag':['烟之鬼',]}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.19*1.2
        d['times']=5
        damage(d,data)
        temp=d['flag']
        temp.append('aoe')
        temp.append('多段分割')
        d={'flag':temp}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.44*1.2*(1+temp.count('暴击'))
        damage(d,data)

class 金鱼姬():
    def __init__(self,info):
        self.atki=2332
        self.dfi=410
        self.maxhpi=13671
        self.spi=116
        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.type='金鱼姬'
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']
        

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canUseSkill(self,data) and canUseOrb(self,2,data) and not data['summons'][self.team]:
            self.sk3(data)
            
        elif canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive==1 and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk1(tg,data)
            
    def sk1(self,tg,data,fj=None):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        
        if data['mode']==0:
            my_print(data,"%s对%s使用了扇舞"%(self.name,tg.name))
        
        d={'flag':['扇舞','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*0.8*1.25
        if fj:
            d['flag'].append(fj)
        damage(d,data)
        
    def sk1b(self,tg,data):
        h={'flag':['扇舞']}
        h['to']=tg
        h['from']=self
        h['heal']=self.maxhp*0.25
        heal(h,data)

    def sk3(self,data):
        if '明灯·增伤' not in self.buff.keys():
            gainOrb(self,-2,data)
        if data['mode']==0:
            my_print(data,'%s召唤金鱼'%self.name)
        data['ids']+=1
        data['summons'][self.team]=金鱼({
        'id':data['ids'],
        '名字':self.name+'的金鱼',
        '速度':self.sp,
        '位置':0,
        '队伍':self.team,
        '生命':self.maxhp*0.66,
        '攻击':self.atk,
        '防御':self.df,
        '暴击':self.critDamage,
        '暴击伤害':self.critDamage,
        '效果命中':self.hit,
        '效果抵抗':self.resist,
        '御魂':''
            })
        

        data['uands'].append(data['summons'][self.team])
        data['action'].insert(1,data['summons'][self.team])

class 金鱼():
    def __init__(self,info):
        self.atki=info['攻击']
        self.dfi=info['防御']
        self.maxhpi=info['生命']
        self.spi=info['速度']
        

        self.sp=info['速度']
        self.sp0=info['速度']
        
        self.name=info['名字']
        self.team=info['队伍']
        self.po=info['位置']
        self.alive=1
        self.id=info['id']
        self.buff={}
        
        self.type='金鱼'
        
        self.maxhp=info['生命']
        self.maxhp0=info['生命']
        self.hp=info['生命']

        self.atk=info['攻击']
        self.atk0=info['攻击']
        
        self.df=info['防御']
        self.df0=info['防御']

        self.crit=info['暴击']
        self.crit0=info['暴击']
        
        self.critDamage=info['暴击伤害']
        self.critDamage0=info['暴击伤害']
        
        self.resist=info['效果抵抗']
        self.resist0=info['效果抵抗']
        
        self.hit=info['效果命中']
        self.hit0=info['效果命中']
        
        self.soul=info['御魂']
        self.计数=0

    def __repr__(self):
        return '%s:%.2f'%(self.name,self.po)

    def move(self,data):
        #判断使用哪个技能
        if canNormalAttack(self,data):
            #判断合理的选择目标
            tg=None
            to_select=[]
            for i in data['uands']:
                if i.alive==1 and isEnemy(self,i,self):
                    to_select.append(i)
            if to_select:
                tg=sample(to_select,1)[0]
            if tg:
                self.sk3(tg,data)
            
    def sk3(self,tg,data):
        if '嘲讽' in self.buff.keys():
            tg=self.buff['嘲讽']['嘲讽']
        
        if data['mode']==0:
            my_print(data,"%s对%s使用了金鱼·普攻"%(self.name,tg.name))
        
        d={'flag':['金鱼·普攻','普攻']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.25

        damage(d,data)


    def sk1(self,tg,data,fj=None):
        if data['mode']==0:
            my_print(data,"%s使用了金鱼·反击"%(self.name))

        d={'flag':['金鱼·反击','aoe','反击']}
        d['to']=tg
        d['from']=self
        d['td']=self.atk*1.2

        damage(d,data)
        
soulList=['阴摩罗','心眼','鸣屋','狰','轮入道','蝠翼','镇墓兽','破势','伤魂鸟','网切','三味','针女','树妖','薙魂','钟灵','镜姬','被服','涅槃之火','地藏像','木魅','日女巳时','反枕','招财猫','雪幽魂',
'媚妖','珍珠','火灵','蚌精','魍魉之匣','返魂香','骰子鬼']      
shikigamiClassList=[山风,玉藻前,雪童子,彼岸花,荒,花鸟卷,辉夜姬,大天狗,酒吞童子,荒川之主,阎魔,两面佛,小鹿男,茨木童子,青行灯,妖刀姬,
                    一目连,奴良陆生,御馔津,鬼灯,卖药郎,
                    桃花妖,雪女,鬼使白,鬼使黑,傀儡师,匣中少女,食梦貘,般若,凤凰火,孟婆,犬神,吸血姬,百目鬼,姑获鸟,络新妇,骨女,
                    鬼女红叶,黑童子,跳跳哥哥,海坊主,判官,妖狐,妖琴师,追月神,清姬,青坊主,镰鼬,二口女,弈,白狼,樱花妖,万年竹,夜叉,
                    烟烟罗,金鱼姬]    
shikigamiNameList=['山风','玉藻前','雪童子','彼岸花','荒','花鸟卷','辉夜姬','大天狗','酒吞童子','荒川之主','阎魔','两面佛','小鹿男','茨木童子','青行灯','妖刀姬',
                   '一目连','奴良陆生','御馔津','鬼灯','卖药郎',
                   '桃花妖','雪女','鬼使白','鬼使黑','傀儡师','匣中少女','食梦貘','般若','凤凰火','孟婆','犬神','吸血姬','百目鬼','姑获鸟','络新妇','骨女',
                   '鬼女红叶','黑童子','跳跳哥哥','海坊主','判官','妖狐','妖琴师','追月神','清姬','青坊主','镰鼬','二口女','弈','白狼','樱花妖','万年竹','夜叉',
                   '烟烟罗','金鱼姬']
shikigamiDict={shikigamiNameList[i]:shikigamiClassList[i] for i in range(len(shikigamiClassList))}
