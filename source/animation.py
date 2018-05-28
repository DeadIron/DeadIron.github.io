import pyglet
import shikigami as sg
import process as pr
from collections import deque

windowX=1280
battx=[0,0,0,0,0,windowX-120,windowX-120,windowX-120,windowX-120,windowX-120,-100]
batty=[80,210,340,470,600,80,210,340,470,600,-100]
hpChangerx=[160,160,160,160,160,windowX-160,windowX-160,windowX-160,windowX-160,windowX-160,]    

def timeToRemove(time):
    if time<40:
        temp=255
    else:
        temp=255-time*3
    if temp<0:
        temp=0
    return temp

def showLabel(data):
    if data['win']!=0:
        turn_label = pyglet.text.Label(text="%d队胜利"%(data['win']), x=640, y=640,anchor_x="center")
        turn_label.font_size=30
        turn_label.bold=True
        turn_label.draw()
        return
    if data['animation'].turn:
        turn_label = pyglet.text.Label(text="%s的回合"%(data['animation'].turn.name), x=640, y=640,anchor_x="center")
        turn_label.font_size=30
        turn_label.bold=True
        turn_label.draw()
    if data['animation'].action:
        action_label = pyglet.text.Label(text="%s的行动"%(data['animation'].action.name), x=640, y=600,anchor_x="center")
        action_label.font_size=24
        action_label.draw()
    leftOrb_label = pyglet.text.Label(text="火:%d\n格:%d"%(data['orb'][0],data['orbPo'][0]), x=240, y=600,anchor_x="center")
    leftOrb_label.font_size=20
    leftOrb_label.draw()    
    rightOrb_label = pyglet.text.Label(text="火:%d\n格:%d"%(data['orb'][1],data['orbPo'][0]), x=1000, y=600,anchor_x="center")
    rightOrb_label.font_size=20
    rightOrb_label.draw()    
def drawHp(batt_sprs,data):
    for i,unit in enumerate(data['units']):
        if i<5: 
            if unit.alive:
                pyglet.graphics.draw_indexed(4, pyglet.gl.GL_QUADS, [0,1,2,3,0],('v2i',(battx[i]+140,batty[i],battx[i]+140,batty[i]+120,battx[i]+150,batty[i]+120,battx[i]+150,batty[i])),('c3B', tuple([0]*3*4)))
                pyglet.graphics.draw_indexed(4, pyglet.gl.GL_QUADS, [0,1,2,3,0],('v2i',(battx[i]+140,batty[i],battx[i]+140,batty[i]+int(120*unit.hp/unit.maxhp),battx[i]+150,batty[i]+int(120*unit.hp/unit.maxhp),battx[i]+150,batty[i])),('c3B', (239,204,88,183,85,14,183,85,14,239,204,88)))
                
        else:
            if unit.alive:
                pyglet.graphics.draw_indexed(4, pyglet.gl.GL_QUADS, [0,1,2,3,0],('v2i',(battx[i]-20,batty[i],battx[i]-20,batty[i]+120,battx[i]-30,batty[i]+120,battx[i]-30,batty[i])),('c3B', tuple([0]*3*4)))
                pyglet.graphics.draw_indexed(4, pyglet.gl.GL_QUADS, [0,1,2,3,0],('v2i',(battx[i]-20,batty[i],battx[i]-20,batty[i]+int(120*unit.hp/unit.maxhp),battx[i]+-30,batty[i]+int(120*unit.hp/unit.maxhp),battx[i]-30,batty[i])),('c3B', (239,204,88,183,85,14,183,85,14,239,204,88)))
        if unit.hp==0:
            batt_sprs[i].visible=False
def drawPo(po_sprs,data):            
    for i,unit in enumerate(po_sprs):
        if data['animation'].turn in data['units'] and i == data['units'].index(data['animation'].turn):
            unit.x=1220
        else:
            unit.x=data['units'][i].po*1000
        if data['units'][i].alive:
            unit.visible=True
        else:
            unit.visible=False
        unit.draw()
def atk(attack_sprs,data):
    anm=data['animation']
    if anm.atk==1:
        for i,atkt in enumerate(data['animation'].atkt):
            frm=anm.atkf
            ifrm=data['units'].index(frm)
            attack_img=pyglet.resource.image("sword.jpg")
            temp=pyglet.sprite.Sprite(img=attack_img,x=battx[ifrm]+60,y=batty[ifrm]+60)
            temp.anchor_x='center'
            temp.anchor_y='center'
            temp.scale=0.04
            temp.draw()
            attack_sprs[i]=temp
            anm.atk=2
    elif anm.atk==2:
        frm=anm.atkf
        ifrm=data['units'].index(frm)
        for i,to in enumerate(data['animation'].atkt):
            ito=data['units'].index(to)

            vx=(battx[ito]-battx[ifrm])/100
            vy=(batty[ito]-batty[ifrm])/100
            
            attack_sprs[i].x+=vx
            attack_sprs[i].y+=vy
            attack_sprs[i].draw()
            if (ito<=4 and battx[ito] > int(attack_sprs[i].x)) or (ito>4 and battx[ito] < int(attack_sprs[i].x)):
                del attack_sprs[i]
            if not attack_sprs:
                anm.atk=0
        
def heal(heal_sprs,data):
    anm=data['animation']
    if anm.heal==1:
        for i,healt in enumerate(data['animation'].healt):
            frm=anm.healf
            ifrm=data['units'].index(frm)
            heal_img=pyglet.resource.image("4.png")
            temp=pyglet.sprite.Sprite(img=heal_img,x=battx[ifrm],y=batty[ifrm]+60)
            temp.anchor_x='center'
            temp.anchor_y='center'
            temp.scale=0.5
            if ifrm>4:
                temp.x-=160
            else:
                temp.x+=160
            temp.draw()
            heal_sprs[i]=temp
            anm.heal=2
    elif anm.heal==2:
        frm=anm.healf
        ifrm=data['units'].index(frm)
        for i,to in enumerate(data['animation'].healt):
            ito=data['units'].index(to)

            vx=(battx[ito]-battx[ifrm])
            if ifrm>4:
                vx+=160
                vx/=50
            else:
                vx-=160
                vx/=50
            vy=(batty[ito]-batty[ifrm]-60)/50
            
            heal_sprs[i].x+=vx
            heal_sprs[i].y+=vy
            heal_sprs[i].draw()
            if (ito<=4 and battx[ito] > int(heal_sprs[i].x)) or (ito>4 and battx[ito] < int(heal_sprs[i].x)):
                del heal_sprs[i]
            if not heal_sprs:
                anm.heal=0
def drawDamage(damage_sprs,data):        
    temp=[]
    while data['animation'].hpChange:
        temp.append(data['animation'].hpChange.pop()+[0])
        
    while damage_sprs:
        temp.append(damage_sprs.pop())
    tempy=[0,0,0,0,0,0,0,0,0,0]    
    for changer,hpChange,label,time in temp:
        ichanger=data['units'].index(changer)
        tempText="%d"%hpChange
        if tempText=="0":
            continue
        tempLabel=pyglet.text.Label(text=tempText,x=hpChangerx[ichanger],y=batty[ichanger]+tempy[ichanger])
        if ichanger>=5:
            tempLabel.anchor_x="right"
        tempy[ichanger]+=20
        tempLabel.font_size=20
        toRemove=timeToRemove(time)
        if hpChange>0:
            tempLabel.color=(0,255,0,toRemove)
        if hpChange<0 and label:
            tempLabel.color=(255,255,0,toRemove)
        if hpChange<0 and not label:
            tempLabel.color=(255,255,255,toRemove)
        if toRemove!=0:
            damage_sprs.append([changer,hpChange,label,time+1])
        tempLabel.draw()
        
def main(data):
    game_window = pyglet.window.Window(windowX, 720)

    pyglet.resource.path=["../img"]
    pyglet.resource.reindex()

    back_img=pyglet.resource.image("back.png")
    back_spr=pyglet.sprite.Sprite(img=back_img,x=0,y=0)
    
    attack_sprs={}
    damage_sprs=[]
    heal_sprs={}

    
    po_sprs=[]
    batt_sprs=[]
    for unit in data['units']:
        try:
            temp_img=pyglet.resource.image(unit.type+".png")
        except:
            temp_img=pyglet.resource.image("99.png")
        po_sprs.append(pyglet.sprite.Sprite(img=temp_img,x=0,y=0))
        batt_sprs.append(pyglet.sprite.Sprite(img=temp_img,x=battx[len(batt_sprs)],y=batty[len(batt_sprs)]))
        po_sprs[-1].scale=0.5
    
    def update(dt):
        drawHp(batt_sprs,data)
        drawPo(po_sprs,data)
        atk(attack_sprs,data)
        heal(heal_sprs,data)
        drawDamage(damage_sprs,data)
    @game_window.event
    def on_draw():
        game_window.clear()
        back_spr.draw()
        for obj in po_sprs:
            obj.draw()
        for obj in batt_sprs:
            obj.draw()
        drawHp(batt_sprs,data)
        drawPo(po_sprs,data)
        atk(attack_sprs,data)
        heal(heal_sprs,data)
        showLabel(data)
        drawDamage(damage_sprs,data)
#        pyglet.clock.ClockDisplay()
        
    pyglet.clock.schedule_interval(update,1/120.0)
    pyglet.app.run()

