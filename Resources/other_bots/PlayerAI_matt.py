from PythonClientAPI.libs.Game.Enums import *
from PythonClientAPI.libs.Game.MapOutOfBoundsException import *
import copy


class PlayerAI:
    def __init__(self):
        # Initialize any objects or variables you need here.
        self.originalmap = []
        self.wavefrontmap = []
        self.instruction = []
        self.direction = []
        self.target_position = [0,0]
        self.wavefront_start_value = 10

        self.search_mode = False
        self.danger_here = False
        self.danger_bullet_here = False
        self.danger_step = False
        self.step_movable = False
        self.enemy_near = False
        self.attack_mode = False
        self.bullet_front = False

        self.bulletlist = []
        self.bulletlist2 = []
        self.maptemp = []
        self.danger = 0
        self.maptemp = []
        pass

    def get_move(self, gameboard, player, opponent):
        # map generation
        self.updatemap(gameboard,opponent)

        # map awareness:
        self.awareness(gameboard, player, opponent)

        if self.danger_here == True and self.danger_step == False:
            if self.step_movable == True:
                self.search_mode = False
                return Move.FORWARD
            else:
                return self.power_up_defence(gameboard, player)
        if self.danger_here == False and self.danger_step == True and self.search_mode == True:
            if self.instruction == [] or self.instruction[0] == 1:
                return Move.NONE
        if self.danger_here == True and (self.danger_step == True or self.step_movable == False):
            return self.power_up_defence(gameboard, player)

        # check to be in attack mode        
        if self.enemy_near == True:
            self.attack_mode = True
        else:
            self.attack_mode = False
            self.initialize_attack_mode(gameboard)
            
        if self.attack_mode == True:
            # has to turn off search mode
            self.search_mode = False
            self.instruction = []
            return self.attack_action(gameboard, player, opponent)
        
        # power up searchmode
        if self.search_mode == False:
            self.search_powerup(gameboard, player,opponent);
        return self.followinstruction(player)

    def power_up_defence(self, gameboard, player):
        print("defense")
        if self.bullet_front == True or self.danger_bullet_here == True:
            if player.teleport_count > 0:
                return Move.TELEPORT_0
            if player.shield_count > 0:
                return Move.SHIELD          
        else:
        # shield > laser > teleport
            if player.laser_count > 0:
                return Move.LASER            
            if player.shield_count > 0:
                return Move.SHIELD 
            if player.teleport_count > 0:
                return Move.TELEPORT_0
        return self.followinstruction(player)

    def awareness(self, gameboard, player, opponent):
        if self.originalmap[player.x][player.y] >= 2:
            self.danger_here = True
            if self.originalmap[player.x][player.y] == 3:
                self.danger_bullet_here = True
        else:
            self.danger_here = False
            self.danger_bullet_here = False

        self.danger_step = False
        self.step_movable = True
        self.bullet_front = False
        if player.direction == Direction.UP:
            if self.originalmap[player.x][(player.y-1)%gameboard.height] > 1:
                self.danger_step = True
            elif self.originalmap[player.x][(player.y-1)%gameboard.height] == 1:
                self.step_movable = False
            if self.originalmap[player.x][(player.y-1)%gameboard.height] == 5:
                self.bullet_front = True
        if player.direction == Direction.DOWN:
            if self.originalmap[player.x][(player.y+1)%gameboard.height] > 1:
                self.danger_step = True
            elif self.originalmap[player.x][(player.y+1)%gameboard.height] == 1:
                self.step_movable = False
            if self.originalmap[player.x][(player.y+1)%gameboard.height] == 5:
                self.bullet_front = True
        if player.direction == Direction.RIGHT:
            if self.originalmap[(player.x+1)%gameboard.width][player.y] > 1:
                self.danger_step = True
            elif self.originalmap[(player.x+1)%gameboard.width][player.y] == 1:
                self.step_movable = False
            if self.originalmap[(player.x+1)%gameboard.width][player.y] == 5:
                self.bullet_front = True
        if player.direction == Direction.LEFT:
            if self.originalmap[(player.x-1)%gameboard.width][player.y] > 1:
                self.danger_step = True
            elif self.originalmap[(player.x-1)%gameboard.width][player.y] > 1:
                self.step_movable = False
            if self.originalmap[(player.x-1)%gameboard.width][player.y] == 5:
                self.bullet_front = True

        self.enemy_near = False
        if (abs(player.x-opponent.x) + abs(player.y-opponent.y)) < 6:
            self.enemy_near = True
        return

    def search_powerup(self, gameboard, player,opponent):
        self.wavefrontmapcopy()
        self.wavefront(player.x,player.y,self.wavefront_start_value,gameboard)
        #update targets
        self.poweruptarget(gameboard,opponent)
        #update instructions
        self.getinstruction(player,self.target_position[0],self.target_position[1],gameboard)
        self.search_mode = True
        
    
    def updatemap(self, gameboard, opponent):
        self.originalmap = [[0 for j in range(gameboard.height)] for i in range(gameboard.width)]
        #by convention, wall is 1, powerup region is 2, bullet is 3, current bullet 5
        #get wall:
        for coor in gameboard.walls:
            self.originalmap[coor.x][coor.y] = 1
        #get turrent region:
        for coor in gameboard.turrets:
            self.originalmap[coor.x][coor.y] = 1
        #get bullet position:
        for fire in gameboard.turrets:
            if fire.is_firing_next_turn == True:
                for i in range (1,5):
                    if self.originalmap[(fire.x+i)%gameboard.width][fire.y] == 1:
                        break
                    self.originalmap[(fire.x+i)%gameboard.width][fire.y] = 2
                for i in range (1,5):
                    if self.originalmap[(fire.x-i)%gameboard.width][fire.y] == 1:
                        break
                    self.originalmap[(fire.x-i)%gameboard.width][fire.y] = 2
                for i in range (1,5):
                    if self.originalmap[fire.x][(fire.y+i)%gameboard.height] == 1:
                        break
                    self.originalmap[fire.x][(fire.y+i)%gameboard.height] = 2
                for i in range (1,5):
                    if self.originalmap[fire.x][(fire.y-i)%gameboard.height] == 1:
                        break
                    self.originalmap[fire.x][(fire.y-i)%gameboard.height] = 2


        for bullet in gameboard.bullets:
            if bullet.direction == Direction.UP:
                if self.originalmap[bullet.x][(bullet.y-1)%gameboard.height] != 1:
                    self.originalmap[bullet.x][(bullet.y-1)%gameboard.height] = 3
                if self.originalmap[bullet.x][bullet.y] == 0:
                    self.originalmap[bullet.x][bullet.y] = 5
            if bullet.direction == Direction.DOWN:
                if self.originalmap[bullet.x][(bullet.y+1)%gameboard.height] != 1:
                    self.originalmap[bullet.x][(bullet.y+1)%gameboard.height] = 3
                if self.originalmap[bullet.x][bullet.y] == 0:
                    self.originalmap[bullet.x][bullet.y] = 5                    
            if bullet.direction == Direction.RIGHT:
                if self.originalmap[(bullet.x+1)%gameboard.width][bullet.y] != 1:
                    self.originalmap[(bullet.x+1)%gameboard.width][bullet.y] = 3
                if self.originalmap[bullet.x][bullet.y] == 0:
                    self.originalmap[bullet.x][bullet.y] = 5                
            if bullet.direction == Direction.LEFT:
                if self.originalmap[(bullet.x-1)%gameboard.width][bullet.y] != 1:
                    self.originalmap[(bullet.x-1)%gameboard.width][bullet.y] = 3
                if self.originalmap[bullet.x][bullet.y] == 0:
                    self.originalmap[bullet.x][bullet.y] = 5                
        
        #opponent treated as wall:
        self.originalmap[opponent.x][opponent.y] = 1
        
        #virtual bullet:
        if opponent.direction == Direction.UP:
            if self.originalmap[opponent.x][(opponent.y-1)%gameboard.height] != 1:
                self.originalmap[opponent.x][(opponent.y-1)%gameboard.height] = 3
        if opponent.direction == Direction.DOWN:
            if self.originalmap[opponent.x][(opponent.y+1)%gameboard.height] != 1:
                self.originalmap[opponent.x][(opponent.y+1)%gameboard.height] = 3
        if opponent.direction == Direction.RIGHT:
            if self.originalmap[(opponent.x+1)%gameboard.width][opponent.y] != 1:
                self.originalmap[(opponent.x+1)%gameboard.width][opponent.y] = 3
        if opponent.direction == Direction.LEFT:
            if self.originalmap[(opponent.x-1)%gameboard.width][opponent.y] != 1:
                self.originalmap[(opponent.x-1)%gameboard.width][opponent.y] = 3
        
        return 1

    def wavefrontmapcopy(self):
        self.wavefrontmap = copy.deepcopy(self.originalmap)

    
    def wavefront(self,x,y,num,gameboard):
        #if num > 35:
        #    return
        if x < 0:
            x = gameboard.width-1
        if x == gameboard.width:
            x = 0
        if y < 0:
            y = gameboard.height-1
        if y == gameboard.height:
            y = 0      
                
        if self.wavefrontmap[x][y] == 0 or num < self.wavefrontmap[x][y]:
            self.wavefrontmap[x][y]=num
            self.wavefront(x+1,y,num+1,gameboard)
            self.wavefront(x,y+1,num+1,gameboard)
            self.wavefront(x-1,y,num+1,gameboard)
            self.wavefront(x,y-1,num+1,gameboard)
        return

    
    def getinstruction(self,player,x,y,gameboard):
        # 1 represents going straight, 2 for up, 3 for down, 4 for right, 5 for left
        return self.horizontalinstruction(player,x,y,gameboard)
        ref = -1
        if player.direction == Direction.RIGHT:
            ref = 1
        # if the same horizontal direction
        if (x - player.x)*ref > 0:
            return horizontalinstruction(self,player,x,y)
        elif player.direction == Direction.RIGHT or player.direction == Direction.LEFT:
            return vertialinstruction(self,player,x,y)
        
        ref = -1
        if player.direction == Direction.UP:
            ref = 1
        if (y - player.y)*ref > 0:
            return vertialinstruction(self,player,x,y)
        else:
            return horizontalinstruction(self,player,x,y)

    def verticalinstruction(self,num,player,x,y):
        return self.horizontalinstruction(num,player,x,y)
    
    # x,y are the target coordinate
    def horizontalinstruction(self,player,x,y,gameboard):
        self.direction = []
        self.instruction = []
        self.horizontalrecursion(x,y,gameboard)
        for i in self.direction:
            if self.instruction == [] or i != self.instruction[-1]:
                self.instruction.append(i)
            self.instruction.append(1)
        return
        

    def horizontalrecursion(self,x,y,gameboard):
        if x < 0:
            x = gameboard.width-1
        if x == gameboard.width:
            x = 0
        if y < 0:
            y = gameboard.height-1
        if y == gameboard.height:
            y = 0
        if self.wavefrontmap[x][y] == self.wavefront_start_value:
            return
        if self.wavefrontmap[x][(y+1)%gameboard.height] == self.wavefrontmap[x][y] - 1:
            self.direction.insert(0,2) # up         
            return self.horizontalrecursion(x,y+1,gameboard)
        if self.wavefrontmap[x][(y-1)%gameboard.height] == self.wavefrontmap[x][y] - 1:
            self.direction.insert(0,3) # down
            return self.horizontalrecursion(x,y-1,gameboard)
        if self.wavefrontmap[(x+1)%gameboard.width][y] == self.wavefrontmap[x][y] - 1:
            self.direction.insert(0,5) # left
            return self.horizontalrecursion(x+1,y,gameboard)
        if self.wavefrontmap[(x-1)%gameboard.width][y] == self.wavefrontmap[x][y] - 1:
            self.direction.insert(0,4) # right
            return self.horizontalrecursion(x-1,y,gameboard)

    def poweruptarget(self,gameboard,opponent):
        # note: if no target, enemy position will be used
        mindis = 100
        if gameboard.power_ups == []:
            self.target_position[0]=opponent.x;
            self.target_position[1]=opponent.y;            
        for pu in gameboard.power_ups:
            if self.wavefrontmap[pu.x][pu.y] < mindis and self.wavefrontmap[pu.x][pu.y] > 2:
                self.target_position[0]=pu.x;
                self.target_position[1]=pu.y;
                mindis = self.wavefrontmap[pu.x][pu.y]
        return
        
    def get_to_enemy(self,gameboard,opponent):
        self.target_position[0] = opponent.x
        self.target_position[1] = opponent.y
        return
        
    def followinstruction(self,player):
        if self.instruction == []:
            self.search_mode = 0
            return
        op = self.instruction.pop(0);
        if op == 1:
            return Move.FORWARD
        # if direction is the same, no need to turn
        #if (player.direction == Direction.UP and op == 2) or (player.direction == Direction.DOWN and op == 3) or (player.direction == Direction.RIGHT and op == 4) or (player.direction == Direction.LEFT and op == 5):
        #    op = self.instruction.pop(0)
        
        if op == 2:
            return Move.FACE_UP
        if op == 3:
            return Move.FACE_DOWN
        if op == 4:
            return Move.FACE_RIGHT
        if op == 5:
            return Move.FACE_LEFT
        return Move.NONE


    def chase(self,gameboard,player,tx,ty,orient):        
        leftscore=0
        rightscore=0
        upscore=0
        downscore=0
        #distance
        distscale = 3
        rightdx = tx - player.x
        if rightdx < 0: rightdx = rightdx + gameboard.width
        leftdx = player.x - tx
        if leftdx < 0: leftdx = leftdx + gameboard.width        
        downdx = ty - player.y
        if downdx < 0: downdx = downdx + gameboard.height
        updx = player.y - ty
        if updx < 0: updx = updx + gameboard.height            
        if rightdx < leftdx: rightscore+=distscale
        elif leftdx < rightdx: leftscore+=distscale
        if updx < downdx: upscore+=distscale
        elif downdx < updx: downscore+=distscale
        if rightdx == 0: rightscore -= 2
        if leftdx == 0: leftscore -= 2
        if updx == 0: upscore -= 2
        if downdx == 0: downscore -= 2
        #player direction        
        pdirscale = 2
        if player.direction == Direction.UP: upscore+=pdirscale
        elif player.direction == Direction.DOWN: downscore+=pdirscale
        elif player.direction == Direction.LEFT: leftscore+=pdirscale
        elif player.direction == Direction.RIGHT: rightscore+=pdirscale
        #enemy direction
        if orient != -1:
            edirscale = 1
            if orient == Direction.UP: downscore+=edirscale
            elif orient == Direction.DOWN: upscore+=edirscale
            elif orient == Direction.LEFT: rightscore+=edirscale
            elif orient == Direction.RIGHT: leftscore+=edirscale
        #obstacle
        if gameboard.is_wall_at_tile((player.x+1)%gameboard.width,player.y): rightscore -= 5000
        if gameboard.is_wall_at_tile((player.x-1)%gameboard.width,player.y): leftscore -= 5000
        if gameboard.is_wall_at_tile(player.x,(player.y+1)%gameboard.height): downscore -= 5000
        if gameboard.is_wall_at_tile(player.x,(player.y-1)%gameboard.height): upscore -= 5000
        if ((player.x+1)%gameboard.width,player.y) in self.bulletlist: rightscore -= 4000
        if ((player.x-1)%gameboard.width,player.y) in self.bulletlist: leftscore -= 4000
        if (player.x,(player.y+1)%gameboard.height) in self.bulletlist: downscore -= 4000
        if (player.x,(player.y-1)%gameboard.height) in self.bulletlist: upscore -= 4000      
        if self.originalmap[(player.x+1)%gameboard.width][player.y]: rightscore -= 4000
        if self.originalmap[(player.x-1)%gameboard.width][player.y]: leftscore -= 4000
        if self.originalmap[player.x][(player.y+1)%gameboard.height]: downscore -= 4000
        if self.originalmap[player.x][(player.y-1)%gameboard.height]: upscore -= 4000
        
        #no going back
        rightscore -= self.maptemp[(player.x+1)%gameboard.width][player.y]
        leftscore -= self.maptemp[(player.x-1)%gameboard.width][player.y]
        downscore -= self.maptemp[player.x][(player.y+1)%gameboard.height]
        upscore -= self.maptemp[player.x][(player.y-1)%gameboard.height]
        #in case of danger
        if self.danger == 1:
            self.danger = 2
            for i in gameboard.bullets:
                if i.direction == Direction.DOWN:
                    if(i.x,(i.y+2)%gameboard.height) == (player.x,player.y): 
                        downscore -= 5000
                        continue
                if i.direction == Direction.UP:
                    if(i.x,(i.y-2)%gameboard.height) == (player.x,player.y): 
                        upscore -= 5000
                        continue
                if i.direction == Direction.LEFT:
                    if((i.x-2)%gameboard.width,(i.y)) == (player.x,player.y): 
                        leftscore -= 5000
                        continue
                if i.direction == Direction.RIGHT:
                    if((i.x+2)%gameboard.width,(i.y)) == (player.x,player.y): 
                        rightscore -= 5000
                        continue 
            if orient == Direction.DOWN:
                if(tx,(ty+2)%gameboard.height) == (player.x,player.y): 
                    downscore -= 3000
            if orient == Direction.UP:
                if(tx,(ty-2)%gameboard.height) == (player.x,player.y): 
                    upscore -= 3000
            if orient == Direction.LEFT:
                if((tx-2)%gameboard.width,(ty)) == (player.x,player.y): 
                    leftscore -= 3000
            if orient == Direction.RIGHT:
                if((tx+2)%gameboard.width,(ty)) == (player.x,player.y): 
                    rightscore -= 3000
            if ((player.x+1)%gameboard.width,player.y) in self.bulletlist2: rightscore -= 5000
            if ((player.x-1)%gameboard.width,player.y) in self.bulletlist2: leftscore -= 5000
            if (player.x,(player.y+1)%gameboard.height) in self.bulletlist2: downscore -= 5000
            if (player.x,(player.y-1)%gameboard.height) in self.bulletlist2: upscore -= 5000             
        #analyze
        movelist = [upscore,downscore,leftscore,rightscore]
        largest, idx = max((largest, idx) for (idx, largest) in enumerate(movelist))
        if(Direction(idx+1))==player.direction:
            return (7)
        return (idx+1)
    
    def horclearpath(self,gameboard,axis,small,big):
        i = small
        if big < small:
            big = small+gameboard.width
        while small <= big:
            if gameboard.is_wall_at_tile(small%gameboard.width,axis):
                return False
            small = (small+1)
        return True
    
    def vertclearpath(self,gameboard,axis,small,big):
        i = small
        if big < small:
            big = small+gameboard.width
        while small <= big:
            if gameboard.is_wall_at_tile(axis,small%gameboard.width):
                return False
            small = (small+1)
        return True    
        
            
    def enemy_detected(self,gameboard,player,opponent):
        
        #if player.direction == Direction.UP and opponent.direction == Direction.LEFT:
        #    if (opponent.x-player.x)%gameboard.width == (player.y-opponent.y)%gameboard.height:
        #        return True
        #if player.direction == Direction.DOWN and opponent.direction == Direction.LEFT:
        #    if (opponent.x-player.x)%gameboard.width == (opponent.y-player.y)%gameboard.height:
        #        return True
        #if player.direction == Direction.UP and opponent.direction == Direction.RIGHT:
        #    if (player.x-opponent.x)%gameboard.width == (player.y-opponent.y)%gameboard.height:
        #        return True
        #if player.direction == Direction.DOWN and opponent.direction == Direction.RIGHT:
        #    if (player.x-opponent.x)%gameboard.width == (opponent.y-player.y)%gameboard.height:
        #        return True   
        
        if player.direction == Direction.DOWN and (opponent.y-player.y)%gameboard.height<=4:
            if player.x == opponent.x and self.vertclearpath(gameboard,player.x,player.y,opponent.y):
                return True              
        if player.direction == Direction.LEFT and (player.x-opponent.x)%gameboard.width<=4:            
            if player.y == opponent.y and self.horclearpath(gameboard,player.y,opponent.x,player.x):
                return True         
        if player.direction == Direction.UP and (player.y - opponent.y)%gameboard.height<=4:
            if player.x == opponent.x and self.vertclearpath(gameboard,player.x,opponent.y,player.y):
                return True              
        if player.direction == Direction.RIGHT and (opponent.x-player.x)%gameboard.width<=4:
            if player.y == opponent.y and self.horclearpath(gameboard,player.y,player.x,opponent.x):
                return True         
        return False
    
    def chill(self,gameboard):
        for i in range(0,gameboard.width):
            for j in range(0,gameboard.height):
                if self.maptemp[i][j]!=0:
                    self.maptemp[i][j]-=2

    def get_bullet_list(self, gameboard, player, opponent):
        self.bulletlist = []
        self.bulletlist2 = []
        for i in gameboard.bullets:
            if i.direction == Direction.DOWN:
                self.bulletlist.append((i.x,(i.y+1)%gameboard.height))
                self.bulletlist2.append((i.x,(i.y+2)%gameboard.height))
            if i.direction == Direction.UP:
                self.bulletlist.append((i.x,(i.y-1)%gameboard.height))
                self.bulletlist2.append((i.x,(i.y-2)%gameboard.height))
            if i.direction == Direction.LEFT:
                self.bulletlist.append(((i.x-1)%gameboard.width,(i.y)))
                self.bulletlist2.append(((i.x-2)%gameboard.width,(i.y)))
            if i.direction == Direction.RIGHT:
                self.bulletlist.append(((i.x+1)%gameboard.width,(i.y)))
                self.bulletlist2.append(((i.x+2)%gameboard.width,(i.y)))
            if opponent.direction == Direction.DOWN:
                self.bulletlist.append((opponent.x,(opponent.y+1)%gameboard.height))
                self.bulletlist2.append((opponent.x,(opponent.y+2)%gameboard.height))
            if opponent.direction == Direction.UP:
                self.bulletlist.append((opponent.x,(opponent.y-1)%gameboard.height))
                self.bulletlist2.append((opponent.x,(opponent.y-2)%gameboard.height))
            if opponent.direction == Direction.LEFT: 
                self.bulletlist.append(((opponent.x-1)%gameboard.width,(opponent.y)))
                self.bulletlist2.append(((opponent.x-2)%gameboard.width,(opponent.y)))
            if opponent.direction == Direction.RIGHT:
                self.bulletlist.append(((opponent.x+1)%gameboard.width,(opponent.y))) 
                self.bulletlist2.append(((opponent.x+2)%gameboard.width,(opponent.y)))                
        return

    def initialize_attack_mode(self,gameboard):
        self.danger = 0
        self.maptemp = [[0 for j in range(gameboard.height)] for i in range(gameboard.width)]
        
    
    def attack_action(self, gameboard, player, opponent):
        #self.calculate_bullets(gameboard)
        #self.calculate_laser(gameboard)
        self.get_bullet_list(gameboard, player, opponent)
        if self.danger == 2:
            action = 7
            self.danger = 0
        elif (player.x,player.y) in self.bulletlist:
            action = 7
        elif (player.x,player.y) in self.bulletlist2:
            self.danger = 1
            action = self.chase(gameboard,player,opponent.x,opponent.y,opponent.direction)
        elif self.enemy_detected(gameboard,player,opponent):
            action = 6
        else:
            action = self.chase(gameboard,player,opponent.x,opponent.y,opponent.direction)
        self.chill(gameboard)
        if action==1:
            return Move.FACE_UP
        if action==2:        
            return Move.FACE_DOWN
        if action==3:
            return Move.FACE_LEFT
        if action==4:
            return Move.FACE_RIGHT
        if action==5:
            return Move.NONE
        if action==6:
            return Move.SHOOT
        if action==7:
            self.maptemp[player.x][player.y] += 40
            return Move.FORWARD
        if action==9:
            return Move.SHIELD
        if action==8:
            return Move.LASER
        if action==10:
            return Move.TELEPORT_0
        if action==11:
            return Move.TELEPORT_1
        if action==12:
            return Move.TELEPORT_2
        if action==13:
            return Move.TELEPORT_3
        if action==14:
            return Move.TELEPORT_4
        if action==15:
            return Move.TELEPORT_5 
        return Move.NONE

    def chase(self,gameboard,player,tx,ty,orient):        
        leftscore=0
        rightscore=0
        upscore=0
        downscore=0
        #distance
        distscale = 3
        rightdx = tx - player.x
        if rightdx < 0: rightdx = rightdx + gameboard.width
        leftdx = player.x - tx
        if leftdx < 0: leftdx = leftdx + gameboard.width        
        downdx = ty - player.y
        if downdx < 0: downdx = downdx + gameboard.height
        updx = player.y - ty
        if updx < 0: updx = updx + gameboard.height            
        if rightdx < leftdx: rightscore+=distscale
        elif leftdx < rightdx: leftscore+=distscale
        if updx < downdx: upscore+=distscale
        elif downdx < updx: downscore+=distscale
        if rightdx == 0: rightscore -= 2
        if leftdx == 0: leftscore -= 2
        if updx == 0: upscore -= 2
        if downdx == 0: downscore -= 2
        #player direction        
        pdirscale = 2
        if player.direction == Direction.UP: upscore+=pdirscale
        elif player.direction == Direction.DOWN: downscore+=pdirscale
        elif player.direction == Direction.LEFT: leftscore+=pdirscale
        elif player.direction == Direction.RIGHT: rightscore+=pdirscale
        #enemy direction
        if orient != -1:
            edirscale = 1
            if orient == Direction.UP: downscore+=edirscale
            elif orient == Direction.DOWN: upscore+=edirscale
            elif orient == Direction.LEFT: rightscore+=edirscale
            elif orient == Direction.RIGHT: leftscore+=edirscale
        #obstacle
        if gameboard.is_wall_at_tile((player.x+1)%gameboard.width,player.y): rightscore -= 5000
        if gameboard.is_wall_at_tile((player.x-1)%gameboard.width,player.y): leftscore -= 5000
        if gameboard.is_wall_at_tile(player.x,(player.y+1)%gameboard.height): downscore -= 5000
        if gameboard.is_wall_at_tile(player.x,(player.y-1)%gameboard.height): upscore -= 5000
        if ((player.x+1)%gameboard.width,player.y) in self.bulletlist: rightscore -= 4000
        if ((player.x-1)%gameboard.width,player.y) in self.bulletlist: leftscore -= 4000
        if (player.x,(player.y+1)%gameboard.height) in self.bulletlist: downscore -= 4000
        if (player.x,(player.y-1)%gameboard.height) in self.bulletlist: upscore -= 4000
        if self.originalmap[(player.x+1)%gameboard.width][player.y]: rightscore -= 4000
        if self.originalmap[(player.x-1)%gameboard.width][player.y]: leftscore -= 4000
        if self.originalmap[player.x][(player.y+1)%gameboard.height]: downscore -= 4000
        if self.originalmap[player.x][(player.y-1)%gameboard.height]: upscore -= 4000
        #no going back
        rightscore -= self.maptemp[(player.x+1)%gameboard.width][player.y]
        leftscore -= self.maptemp[(player.x-1)%gameboard.width][player.y]
        downscore -= self.maptemp[player.x][(player.y+1)%gameboard.height]
        upscore -= self.maptemp[player.x][(player.y-1)%gameboard.height]
        #in case of danger
        if self.danger == 1:
            self.danger = 2
            for i in gameboard.bullets:
                if i.direction == Direction.DOWN:
                    if(i.x,(i.y+2)%gameboard.height) == (player.x,player.y): 
                        downscore -= 5000
                        continue
                if i.direction == Direction.UP:
                    if(i.x,(i.y-2)%gameboard.height) == (player.x,player.y): 
                        upscore -= 5000
                        continue
                if i.direction == Direction.LEFT:
                    if((i.x-2)%gameboard.width,(i.y)) == (player.x,player.y): 
                        leftscore -= 5000
                        continue
                if i.direction == Direction.RIGHT:
                    if((i.x+2)%gameboard.width,(i.y)) == (player.x,player.y): 
                        rightscore -= 5000
                        continue 
            if orient == Direction.DOWN:
                if(tx,(ty+2)%gameboard.height) == (player.x,player.y): 
                    downscore -= 3000
            if orient == Direction.UP:
                if(tx,(ty-2)%gameboard.height) == (player.x,player.y): 
                    upscore -= 3000
            if orient == Direction.LEFT:
                if((tx-2)%gameboard.width,(ty)) == (player.x,player.y): 
                    leftscore -= 3000
            if orient == Direction.RIGHT:
                if((tx+2)%gameboard.width,(ty)) == (player.x,player.y): 
                    rightscore -= 3000
            if ((player.x+1)%gameboard.width,player.y) in self.bulletlist2: rightscore -= 5000
            if ((player.x-1)%gameboard.width,player.y) in self.bulletlist2: leftscore -= 5000
            if (player.x,(player.y+1)%gameboard.height) in self.bulletlist2: downscore -= 5000
            if (player.x,(player.y-1)%gameboard.height) in self.bulletlist2: upscore -= 5000             
        #analyze
        movelist = [upscore,downscore,leftscore,rightscore]
        largest, idx = max((largest, idx) for (idx, largest) in enumerate(movelist))
        if(Direction(idx+1))==player.direction:
            return (7)
        return (idx+1)
