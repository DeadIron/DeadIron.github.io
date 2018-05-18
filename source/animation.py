import pyglet
import shikigami as sg
import process as pr

windowX=1280
battx=[0,0,0,0,0,windowX-120,windowX-120,windowX-120,windowX-120,windowX-120,-100]
batty=[80,210,340,470,600,80,210,340,470,600,-100]


def drawHp(data):
    for i,unit in enumerate(data['units']):
        if i<5:
            pyglet.graphics.draw_indexed(4, pyglet.gl.GL_QUADS, [0,1,2,3,0],('v2i',(battx[i]+140,batty[i],battx[i]+140,batty[i]+120,battx[i]+150,batty[i]+120,battx[i]+150,batty[i])),('c3B', tuple([0]*3*4)))
            pyglet.graphics.draw_indexed(4, pyglet.gl.GL_QUADS, [0,1,2,3,0],('v2i',(battx[i]+140,batty[i],battx[i]+140,batty[i]+int(120*unit.hp/unit.maxhp),battx[i]+150,batty[i]+int(120*unit.hp/unit.maxhp),battx[i]+150,batty[i])),('c3B', (239,204,88,183,85,14,183,85,14,239,204,88)))
            
        else:
            pyglet.graphics.draw_indexed(4, pyglet.gl.GL_QUADS, [0,1,2,3,0],('v2i',(battx[i]-20,batty[i],battx[i]-20,batty[i]+120,battx[i]-30,batty[i]+120,battx[i]-30,batty[i])),('c3B', tuple([0]*3*4)))
            pyglet.graphics.draw_indexed(4, pyglet.gl.GL_QUADS, [0,1,2,3,0],('v2i',(battx[i]-20,batty[i],battx[i]-20,batty[i]+int(120*unit.hp/unit.maxhp),battx[i]+-30,batty[i]+int(120*unit.hp/unit.maxhp),battx[i]-30,batty[i])),('c3B', (239,204,88,183,85,14,183,85,14,239,204,88)))

def drawPo(po_sprs,data):            
    for i,unit in enumerate(po_sprs):
        unit.x=data['units'][i].po*1220
        if data['units'][i].alive:
            unit.visible=True
        else:
            unit.visible=False
        unit.draw()

def drawDamage(data):        
     pass   
def main(data):
    game_window = pyglet.window.Window(windowX, 720)

    pyglet.resource.path=["../img"]
    pyglet.resource.reindex()

    back_img=pyglet.resource.image("back.png")
    back_spr=pyglet.sprite.Sprite(img=back_img,x=0,y=0)

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
        drawHp(data)
        drawPo(po_sprs,data)
    @game_window.event
    def on_draw():
        game_window.clear()
        back_spr.draw()
        for obj in po_sprs:
            obj.draw()
        for obj in batt_sprs:
            obj.draw()
        drawHp(data)
    pyglet.clock.schedule_interval(update,1/120.0)
    pyglet.app.run()

