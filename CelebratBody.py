##太阳系前四大行星运动轨迹模拟,包含参考系变换
##通过调整REF_COORD　改变参考天体
import pygame
import math

#全局常量
SCREEN_SIZE = (1280,810)
REF_COORD = "venus"
SIM_RATIO  = 31558150 /10  #地球公转周期s/10   10s 地球绕日一圈  现实10s 对应模拟31558150s      
#时间模拟比例 SIM_RATIO 越大越快,越不精准
#加速度实际,速度模拟,位置模拟
#时间模拟:sim_dt = dt/1000*SIM_RATIO
#计算实际速度:根据模拟位置,求导算出实际速度 因此模拟速度即为真实速度    模拟时间变化的只是dt

PIXEL_TO_M = 0.7E09  #1像素 == 0.7e9 m

G = 6.67E-11#m^3/(kg*s^2)    #引力常数

MASS_MERCURY = 3.3E23#kg   #水星质量
MASS_MARS = 6.41E23#kg     #火星质量
MASS_VENUS = 4.86E24#kg    #金星质量
MASS_EARTH = 5.97e24#kg    #地球质量
MASS_SOLAR =2E30#kg        #太阳质量

#天体颜色参数
COLOR_EARTH = (14,82,153)
COLOR_MARS = (171,74,21)
COLOR_VENUS = (147,145,53)
COLOR_MERCURY = (158,41,0)
COLOR_SOLAR = (217,165,83)

#天体尺寸参数   太阳--行星:非真实比例
R_EARTH = 16.9
R_MARS = 9
R_SOLAR = 30
R_VENUS = 16
R_MERCURY = 6.5

#轨道参数
AU = 1.496E11#m

SMA_MERCURY = 0.387*AU   #水星半长轴
HFL_MERCURY = 0.08*AU    #水星半焦距
PERIHELION_MERCURY = SMA_MERCURY-HFL_MERCURY
ORBIT_RADIUS_EARTH = 1*AU
ORBIT_RADIUS_MARS  =  1.52*AU #平均距日距离
ORBIT_RADIUS_VENUS = 0.72*AU

VELOCITY_MERCURY_A = math.sqrt(G*MASS_SOLAR/SMA_MERCURY*(SMA_MERCURY+HFL_MERCURY)/(SMA_MERCURY-HFL_MERCURY))
VELOCITY_EARTH = 2.98E4 #m/s
VELOCITY_MARS = 2.41E4 #m/s
VELOCITY_VENUS = 3.5E4 #m/s

#天体尾迹
TRAIL_ENABLED = True
TRAIL_LENGTH = 1000
TRAIL_COLOR = (105,70,120)

#类型定义
    #天体
class CelestBody(object):
    def __init__(self,mass,pos,vel0,R,color):
        
        self.mass = mass
        self.pos = {"x":pos[0],"y":pos[1]}  #pixel
        self.vel = vel0    #m
        self.acc = {"x":0,"y":0}    #m
        
        self.color = color
        self.trail = Trail(TRAIL_LENGTH)
        self.R = R
        
    def move(self,dx,dy):
        #更新位置
        self.pos['x'] += dx
        self.pos['y'] += dy

    def update(self):
        pos = tuple(self.pos.values())
        if(TRAIL_ENABLED):
            self.trail.update(pos)  #拖尾刷新
        
        #绘制对象
        #screen.blit(self.image,pos)    #load image 方法
        pygame.draw.circle(screen,self.color,pos,self.R)

    #轨迹
class Trail:
    def __init__(self,len):
        self.length = len
        self.pos_list = []
    def update(self,new_pos):   #new_pos :tulple(x,y)

        self.pos_list.append(new_pos)
        if len(self.pos_list)>self.length:
            self.pos_list.pop(0)
        for p in self.pos_list:
            pygame.draw.circle(screen,TRAIL_COLOR,p,2)

#p2m pixel to meter
def p2m(pixel):
    return pixel*PIXEL_TO_M

#m2p meter to pixel
def m2p(meter):
    return meter/PIXEL_TO_M

#加速度积分
def add_dvel_dt(v0,a,sim_dt): #v0 dict    v+dv        a : tuple
    ax = a[0]
    ay = a[1]
    v0x = v0['x']
    v0y = v0['y']
    
    v1x = v0x+ax*sim_dt
    v1y = v0y+ay*sim_dt
    
    return{'x':v1x,'y':v1y}
#速度积分
def add_dpos_dt(pos0,v,sim_dt): #pos0 dict    r+dr    v:dict
    if type(v).__name__ == "dict":
        vx = v['x']
        vy = v['y']
    else:
        vx = v[0]
        vy = v[1]
    pos0x = pos0['x']
    pos0y = pos0['y']
    
    pos1x = pos0x+m2p(vx*sim_dt)     #vx*dt 单位:m pos1x 单位:pixel    dt:ms
    pos1y = pos0y+m2p(vy*sim_dt)  
    
    
    return{'x':pos1x,'y':pos1y}     #position 单位:pixel
#计算引力加速度
def G_acceleration(cb1,cb2):   #求 cb1 关于cb2 的引力加速度
    cb2cb1 = (p2m(cb2.pos['x']-cb1.pos['x']),p2m(cb2.pos['y']-cb1.pos['y']))    #矢量 phycical
    mod_cb2cb1 = math.sqrt(cb2cb1[0]**2+cb2cb1[1]**2)   #phycical

    a12 = (cb2cb1[0]*G*cb2.mass/mod_cb2cb1**3,cb2cb1[1]*G*cb2.mass/mod_cb2cb1**3)   #矢量 加速度 phycical
    return a12

# 初始设置
pygame.init() # 初始化pygame
screen = pygame.display.set_mode(SCREEN_SIZE) # Pygame窗口
pygame.display.set_caption("CelebratBody") # 标题
keep_going = True

clock_frame = pygame.time.Clock()

    #实例化CelestBody
    #vel = {'x':VELOCITY_EARTH,'y':0}
cb1 = CelestBody(MASS_EARTH,(700,400+m2p(ORBIT_RADIUS_EARTH)),{'x':VELOCITY_EARTH,'y':0},R_EARTH,COLOR_EARTH)
earth = cb1 #引用,不是复制创建新对象

    #vel = {'x':0,'y':0}
cb2 = CelestBody(MASS_SOLAR,(700,400),{'x':0,'y':0},R_SOLAR,COLOR_SOLAR)
solar = cb2 #引用

cb3 = CelestBody(MASS_MARS,(700,400+m2p(ORBIT_RADIUS_MARS)),{'x':VELOCITY_MARS,'y':0},R_MARS,COLOR_MARS)
mars = cb3 #引用

cb4 = CelestBody(MASS_VENUS,(700,400+m2p(ORBIT_RADIUS_VENUS)),{'x':VELOCITY_VENUS,'y':0},R_VENUS,COLOR_VENUS)
venus = cb4

cb5 = CelestBody(MASS_MERCURY,(700,400+m2p(PERIHELION_MERCURY)),{"x":VELOCITY_MERCURY_A,"y":0},R_MERCURY,COLOR_MERCURY)
mercury = cb5

CelestBody_list = [cb1,cb2,cb3,cb4,cb5]

#循环
while keep_going:
    
    pygame.draw.circle(screen,(50,50,50),(0,0),8192)
    
    ft = clock_frame.tick_busy_loop(60)  #帧时钟&锁帧      
    dt = ft      #时间微元   实际模拟16.67ms
    sim_dt = dt/1000*SIM_RATIO
    
    #pygame.draw.circle(screen,(255,255,255),(400,300),40)
    t_ms = pygame.time.get_ticks() # 单位:ms
    t = t_ms/1000  #单位:s
    
    for event in pygame.event.get():  # 遍历事件
        if event.type == pygame.QUIT:  # 退出事件
            keep_going = False

    # 计算各天体受太阳的引力加速度
    a12 = G_acceleration(cb1,cb2)
    
    a32 = G_acceleration(cb3,cb2)
    
    a42 = G_acceleration(cb4,cb2)
    
    a52 = G_acceleration(cb5,cb2)
    
    # 由加速度计算各天体速度,位置
    earth.vel = add_dvel_dt(cb1.vel,a12,sim_dt)
    earth.pos = add_dpos_dt(cb1.pos,cb1.vel,sim_dt)
    
    mars.vel = add_dvel_dt(cb3.vel,a32,sim_dt)
    mars.pos = add_dpos_dt(cb3.pos,cb3.vel,sim_dt)
    
    venus.vel = add_dvel_dt(cb4.vel,a42,sim_dt)
    venus.pos = add_dpos_dt(cb4.pos,cb4.vel,sim_dt)
    
    mercury.vel = add_dvel_dt(cb5.vel,a52,sim_dt)
    mercury.pos = add_dpos_dt(cb5.pos,cb5.vel,sim_dt)
             
    #坐标系变换
    trans_x = 0
    trans_y = 0 
    exec(f"trans_x =  solar.pos['x']-{REF_COORD}.pos['x'] ")
    exec(f"trans_y =  solar.pos['y']-{REF_COORD}.pos['y'] ")
    for p in CelestBody_list:
        p.pos['x'] += trans_x  
        p.pos['y'] += trans_y 
        
    mercury.update()
    venus.update()        
    earth.update()
    mars.update()
    solar.update()

    pygame.display.update()  # 刷新屏幕
    
    #坐标系变换
    for p in CelestBody_list:
        p.pos['x'] -= trans_x  
        p.pos['y'] -= trans_y      
    
pygame.quit()