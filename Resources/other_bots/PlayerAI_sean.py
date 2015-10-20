from PythonClientAPI.libs.Game.Enums import *
from PythonClientAPI.libs.Game.MapOutOfBoundsException import *
from random import randint

class PlayerAI:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.target = []
        self.directions = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]
        self.just_turned = 0
        
        self.target_turret = None
        self.kill_turret_step = 0
        self.turret_kill_turn_dir = None
        self.turret_kill_turn_index = 0
        self.killing_turret = 0
        self.killed_turret = 0

        self.prev_d_staying = None
        self.prev_d_forward_one = None

    def get_move(self, gameboard, player, opponent):
        self.width = gameboard.width
        self.height = gameboard.height

        d_staying = self.danger_staying(gameboard, player, opponent, (player.x, player.y), 0)
        d_forward_one = self.danger_forward(gameboard, player, opponent, (player.x, player.y), 1)
        

        try:
            if not player.did_make_a_move and \
            (self.prev_d_forward_one["Turrets"][0][0].x == d_forward_one["Turrets"][0][0].x) and \
            (self.prev_d_forward_one["Turrets"][0][0].y == d_forward_one["Turrets"][0][0].y):
                self.target_turret = d_forward_one["Turrets"][0][0]
                self.killing_turret = 1
                self.kill_turret_step = 0
                self.turret_kill_turn_dir = None
        except:
            self.target_turret = None

        self.prev_d_staying = d_staying
        self.prev_d_forward_one = d_forward_one

        if (self.target_turret == None) and self.killing_turret:
            self.killing_turret = 0
            self.killed_turret = 1
            
        if (self.target_turret != None):
            print("Killing Turret")
            return self.kill_turret(self.target_turret,player,gameboard,opponent)
        
        suggested_direction_star = self.find_path_2(player, gameboard, opponent)
        suggested_direction_dumb = self.find_path(gameboard, player, opponent)

        suggested_direction = None
        if randint(0,3):
            suggested_direction = suggested_direction_star
        else:
            suggested_direction = suggested_direction_dumb
        print(suggested_direction)
        return self.choose_action(gameboard,player,opponent,suggested_direction,d_staying,d_forward_one)
        


    def turn_left(self, player):
        turns = {Direction.UP:Move.FACE_LEFT, Direction.LEFT:Move.FACE_DOWN, \
        Direction.DOWN:Move.FACE_RIGHT, Direction.RIGHT:Move.FACE_UP}
        return turns[player.direction]
    def turn_right(self, player):
        turns = {Direction.UP:Move.FACE_RIGHT, Direction.LEFT:Move.FACE_UP, \
        Direction.DOWN:Move.FACE_LEFT, Direction.RIGHT:Move.FACE_DOWN}
        return turns[player.direction]
    def adjust_coords(self, coordinates):
        return coordinates[0]%self.width,coordinates[1]%self.height
    def predict_coords(self, turns, direction, coordinates):
        temp_coords = [coordinates[0], coordinates[1]]
        if (direction == Direction.DOWN):
            temp_coords[1] += turns
        elif (direction == Direction.LEFT):
            temp_coords[0] -= turns
        elif (direction == Direction.RIGHT):
            temp_coords[0] += turns
        elif (direction == Direction.UP):
            temp_coords[1] -= turns
        else:
            pass
        return self.adjust_coords(tuple(temp_coords))
    def find_item_at_tile(self, gameboard, opponent, tile):
        x,y = tile
        if gameboard.is_wall_at_tile(x,y):
            return "Wall"
        elif gameboard.is_turret_at_tile(x,y):
            return "Turret"
        elif gameboard.are_bullets_at_tile(x,y):
            return "Bullets"
        elif gameboard.is_power_up_at_tile(x,y):
            return "Power Up"
        elif (opponent.x == x) and (opponent.y == y):
            return "Opponent"
        else:
            return None

    def choose_action(self,gameboard,player,opponent,path_find_sug,dg_stay,dg_forw_one):
        stay_safe = not bool([a for a in dg_stay.values() if a != []])
        forw_safe = not bool([a for a in dg_forw_one.values() if a != []])
        print(stay_safe, forw_safe)

        # Shield Reflect Any Opponent Attacks
        if (len(dg_stay['Opponent'])!=0) and not player.shield_active and (player.shield_count > 0):
            return Move.SHIELD
        # If safe to go in forward direction, go
        if (path_find_sug == player.direction) and forw_safe:
            print ("got 0")
            if (self.shoot_target(player, opponent) == 1):
                return Move.SHOOT
            else:
                return Move.FORWARD
        # If there are dangers ahead but want to go in that direciton
        if (path_find_sug == player.direction) and not forw_safe:
            print ("got 1")
            if self.shoot_target(player, opponent) == 0.5:
                if randint(0,1):
                    return Move.SHOOT
            if stay_safe:
                if not player.did_make_a_move:
                    #try shield first
                    if not player.shield_active and (player.shield_count > 0):
                        return Move.SHIELD
                    #try teleporting
                    if (player.teleport_count > 0):
                        return self.teleport_to_location(randint(0,len(gameboard.teleport_locations)-1))
                    #just go forward
                    return Move.FORWARD
                return Move.NONE
            else:
                # Can't stay cuz of danger
                if not player.shield_active and (player.shield_count > 0):
                    return Move.SHIELD
                # Shoot laser if opponent there
                if ('Laser' in dg_stay['Opponent']) and (player.laser_count > 0):
                    return Move.LASER
                if (player.teleport_count > 0):
                        return self.teleport_to_location(randint(0,len(gameboard.teleport_locations)-1))
                if not player.did_make_a_move:
                    return Move.FORWARD
                return Move.NONE
        # Wants to turn but not safe
        if (path_find_sug != player.direction) and not stay_safe:
            print ("got 2")
            if not player.shield_active and (player.shield_count > 0):
                return Move.SHIELD
            if ('Laser' in dg_stay['Opponent']) and (player.laser_count > 0):
                return Move.LASER
            if self.shoot_target(player, opponent) > 0:
                return Move.SHOOT
            if (player.hp == 1) and (player.teleport_count > 0):
                return self.teleport_to_location(randint(0,len(gameboard.teleport_locations)-1))
            if self.check_blocking_obstacle(gameboard, player, self.directions.index(player.direction)):
                return self.pursue_pref_dir(player, path_find_sug)
            if not self.check_blocking_obstacle(gameboard, player, self.directions.index(player.direction)):
                return Move.FORWARD
            else:
                # It should never get here
                return Move.NONE
        # Can turn then turn
        if (path_find_sug != player.direction) and stay_safe:
            print ("got 3")
            if path_find_sug == Direction.LEFT:
                return Move.FACE_LEFT
            elif path_find_sug == Direction.RIGHT:
                return Move.FACE_RIGHT
            elif path_find_sug == Direction.UP:
                return Move.FACE_UP
            elif path_find_sug == Direction.DOWN:
                return Move.FACE_DOWN
            else:
                return Move.NONE
        return Move.NONE

    def kill_turret(self,turret,player,gameboard,opponent):
        cycletime = turret.cooldown_time + turret.fire_time
        print(self.kill_turret_step)
        if (gameboard.current_turn%cycletime == turret.fire_time) and (self.kill_turret_step == 0):
            self.kill_turret_step += 1
            return Move.FORWARD
        elif self.kill_turret_step == 1:
            self.kill_turret_step += 1
            self.turret_kill_turn_dir = self.find_path(gameboard, player, opponent)
            self.turret_kill_turn_index = self.directions.index(self.turret_kill_turn_dir)\
             - self.directions.index(player.direction)
            return self.pursue_pref_dir(player, self.turret_kill_turn_dir)
        elif self.kill_turret_step == 2:
            self.kill_turret_step += 1
            return Move.SHOOT
        elif self.kill_turret_step == 3:
            self.kill_turret_step += 1
            return self.pursue_pref_dir(player, self.directions[(self.directions.index(self.turret_kill_turn_dir)\
             + self.turret_kill_turn_index)%4])
        elif self.kill_turret_step == 4:
            self.kill_turret_step += 1
            return Move.FORWARD
        elif self.kill_turret_step > 4:
            if turret.is_dead:
                self.turret = None
                self.kill_turret_step = 0
                self.turret_kill_turn_dir = None
            return Move.NONE
        else:
            return Move.NONE



    def find_target(self, player, gameboard):
        targets = gameboard.power_ups
        min_index = 0
        min_dis = 100
        for i in range(0, len(targets)):
            temp = min(abs(targets[i].x - player.x), self.width - abs(targets[i].x - player.x)) + \
                   min(abs(targets[i].y - player.y), self.height - abs(targets[i].y - player.y))
            #print(targets[i].power_up_type, targets[i].x, targets[i].y, temp)
            if temp < min_dis:
                min_dis = temp
                min_index = i
        try:
            return targets[min_index]
        except:
            return None

    def check_wall(self, gameboard, player, index):
        if index == 0:
            return gameboard.is_wall_at_tile(player.x, (player.y - 1) % self.height)
        if index == 1:
            return gameboard.is_wall_at_tile((player.x + 1) % self.width, player.y)
        if index == 2:
            return gameboard.is_wall_at_tile(player.x, (player.y + 1) % self.height)
        if index == 3:
            return gameboard.is_wall_at_tile((player.x - 1) % self.width, player.y)
    def check_immediate_dead_turret(self, gameboard, player, index):
        if index == 0:
            if gameboard.is_turret_at_tile(player.x, (player.y - 1) % self.height):
                return gameboard.turret_at_tile[player.x][(player.y - 1) % self.height].is_dead
            return False
        if index == 1:
            if gameboard.is_turret_at_tile((player.x + 1) % self.width, player.y):
                return gameboard.turret_at_tile[(player.x + 1) % self.width][player.y].is_dead
            return False
        if index == 2:
            if gameboard.is_turret_at_tile(player.x, (player.y + 1) % self.height):
                return gameboard.turret_at_tile[player.x][(player.y + 1) % self.height].is_dead
            return False
        if index == 3:
            if gameboard.is_turret_at_tile((player.x - 1) % self.width, player.y):
                return gameboard.turret_at_tile[(player.x - 1) % self.width][player.y].is_dead
            return False
    def check_blocking_obstacle(self, gameboard, player, index):
        return self.check_wall(gameboard,player,index) or \
        self.check_immediate_dead_turret(gameboard,player,index)

    def find_path_2(self, player, gameboard, opponent):
        target = None
        if self.target_turret != None:
            target = self.target_turret
        else:
            target = self.find_target(player, gameboard)
            if target == None:
                target = opponent
        path = find_path_A_star((player.x, player.y), (target.x,target.y), gameboard)
        return get_dir(gameboard, player, path[-1])

    def find_path(self, gameboard, player, opponent):
        prefer_dir = []
        target = None
        if self.target_turret != None:
            target = self.target_turret
        else:
            target = self.find_target(player, gameboard)
            if target == None:
                target = opponent
        t_x = target.x
        t_y = target.y
        print (target.x, target.y)
        p_x = player.x
        p_y = player.y
        dx = t_x - p_x
        dy = t_y - p_y

        if (self.width - abs(dx)) == abs(dx):
            prefer_dir.append(Direction.LEFT)
            prefer_dir.append(Direction.RIGHT)
        elif (self.width - abs(dx)) > abs(dx):
            if dx > 0:
                prefer_dir.append(Direction.RIGHT)
            if dx < 0:
                prefer_dir.append(Direction.LEFT)
        else:
            if dx > 0:
                prefer_dir.append(Direction.LEFT)
            if dx < 0:
                prefer_dir.append(Direction.RIGHT)

        if (self.height - abs(dy)) == abs(dy):
            prefer_dir.append(Direction.UP)
            prefer_dir.append(Direction.DOWN)
        elif (self.height - abs(dy)) > abs(dy):
            if dy > 0:
                prefer_dir.append(Direction.DOWN)
            if dy < 0:
                prefer_dir.append(Direction.UP)
        else:
            if dy > 0:
                prefer_dir.append(Direction.UP)
            if dy < 0:
                prefer_dir.append(Direction.DOWN)

        print(prefer_dir)
        print(self.killed_turret)
        if self.killed_turret:
            self.killed_turret = 0
            print("reward", prefer_dir[0])
            return prefer_dir[0]
        #DOWN sure if the player orients a preferred direction, it goes on that direction
        straight_dir = player.direction
        left_dir = self.directions[(self.directions.index(player.direction) - 1) % 4]
        right_dir = self.directions[(self.directions.index(player.direction) + 1) % 4]
        back_dir = self.directions[(self.directions.index(player.direction) + 2) % 4]
        
        if self.just_turned:
            if not self.check_blocking_obstacle(gameboard, player, self.directions.index(straight_dir)):
                self.just_turned = 0
                return straight_dir

        if straight_dir in prefer_dir:
            if not self.check_blocking_obstacle(gameboard, player, self.directions.index(straight_dir)):
                return straight_dir
            elif not self.check_blocking_obstacle(gameboard, player, self.directions.index(left_dir)):
                self.just_turned = 1
                return left_dir
            elif not self.check_blocking_obstacle(gameboard, player, self.directions.index(right_dir)):
                self.just_turned = 1
                return right_dir
            else:
                self.just_turned = 1
                return back_dir
        
        if left_dir in prefer_dir:
            if not self.check_blocking_obstacle(gameboard, player, self.directions.index(left_dir)):
                self.just_turned = 1
                return left_dir
            else:
                if not self.check_blocking_obstacle(gameboard, player, self.directions.index(straight_dir)):
                    return straight_dir
                else:
                    if not self.check_blocking_obstacle(gameboard, player, self.directions.index(right_dir)):
                        self.just_turned = 1
                        return right_dir
                    else:
                        self.just_turned = 1
                        return back_dir

        if right_dir in prefer_dir:
            if not self.check_blocking_obstacle(gameboard, player, self.directions.index(right_dir)):
                self.just_turned = 1
                return right_dir
            else:
                if not self.check_blocking_obstacle(gameboard, player, self.directions.index(straight_dir)):
                    return straight_dir
                else:
                    if not self.check_blocking_obstacle(gameboard, player, self.directions.index(left_dir)):
                        self.just_turned = 1
                        return left_dir
                    else:
                        self.just_turned = 1
                        return back_dir

        if back_dir in prefer_dir:
            if not self.check_blocking_obstacle(gameboard, player, self.directions.index(left_dir)):
                self.just_turned = 1
                return left_dir
            elif not self.check_blocking_obstacle(gameboard, player, self.directions.index(straight_dir)):
                return straight_dir
            elif not self.check_blocking_obstacle(gameboard, player, self.directions.index(right_dir)):
                self.just_turned = 1
                return right_dir
            else:
                self.just_turned = 1
                return back_dir

    def pursue_pref_dir(self, player, pref_dir):
        if player.direction == pref_dir:
            return Move.FORWARD
        else:
            if pref_dir == Direction.LEFT:
                return Move.FACE_LEFT
            elif pref_dir == Direction.RIGHT:
                return Move.FACE_RIGHT
            elif pref_dir == Direction.UP:
                return Move.FACE_UP
            elif pref_dir == Direction.DOWN:
                return Move.FACE_DOWN
            else:
                return Move.NONE


    def danger_staying(self, gameboard, player, opponent, position, forward=0):
        danger_items = {"Turrets":[], "Bullets": [], "Opponent": []}
        directions = [Direction.UP, Direction.LEFT, Direction.DOWN, Direction.RIGHT]
        for i in range(len(directions)):
            for j in range(1,5):
                k = self.predict_coords(j, directions[i], position)
                item_at_k = self.find_item_at_tile(gameboard, opponent, k)
                # if wall, safe from anything beyond
                if (item_at_k == "Wall"):
                    break
                #check if turret within 4 blocks is shooting now or shooting next turn
                elif (item_at_k == "Turret"):
                    if gameboard.turret_at_tile[k[0]][k[1]].is_dead:
                        continue
                    indicator = 0
                    cycle_time = gameboard.turret_at_tile[k[0]][k[1]].cooldown_time + \
                    gameboard.turret_at_tile[k[0]][k[1]].fire_time
                    if gameboard.current_turn%cycle_time <= gameboard.turret_at_tile[k[0]][k[1]].fire_time:
                        indicator += 1
                    if (gameboard.current_turn+1)%cycle_time <= gameboard.turret_at_tile[k[0]][k[1]].fire_time:
                        indicator += 2
                    if [gameboard.turret_at_tile[k[0]][k[1]], indicator] not in danger_items["Turrets"]:
                        danger_items["Turrets"].append([gameboard.turret_at_tile[k[0]][k[1]], indicator])
                #check if bullet is within 2 blocks and aiming towards you
                elif (item_at_k == "Bullets") and (j <= 2+forward):
                    for bul in gameboard.bullets_at_tile[k[0]][k[1]]:
                        if bul.direction == directions[(i+2)%4]:
                            danger_items["Bullets"].append(bul)
                elif (item_at_k == "Opponent"):
                    #check if opponent is within 2 blocks and aiming towards you
                    if (j <= 2+forward) and (opponent.direction == directions[(i+2)%4]):
                        danger_items["Opponent"].append("Bullets")
                    #check if opponent if within 4 blocks with laser
                    if (opponent.laser_count > 0):
                        if "Laser" not in danger_items["Opponent"]:
                            danger_items["Opponent"].append("Laser")
                    #else:
                    #   if ["Opponent", "Within Range"] not in danger_items:
                    #       danger_items.append(["Opponent", "Within Range"])
                else:
                    continue
        return danger_items

    def danger_forward(self, gameboard, player, opponent, position, forward_tiles):
        """assume that bullet/opponent travelled in their direction of orientation"""
        next_position = self.predict_coords(forward_tiles, player.direction, position)
        return self.danger_staying(gameboard, player, opponent, next_position, forward_tiles)



    def shoot_target(self, player, opponent):
        if self.predict_coords(1, player.direction, (player.x,player.y)) == (opponent.x,opponent.y):
            return 1
        if self.predict_coords(1,player.direction,(player.x,player.y)) \
        == self.predict_coords(1,opponent.direction,(opponent.x,opponent.y)):
            return 0.5
        else:
            return 0

    def teleport_to_location(self, integer):
        if integer == 0:
            return Move.TELEPORT_0
        elif integer == 1:
            return Move.TELEPORT_1
        elif integer == 2:
            return Move.TELEPORT_2
        elif integer == 3:
            return Move.TELEPORT_3
        elif integer == 4:
            return Move.TELEPORT_4
        elif integer == 5:
            return Move.TELEPORT_5
        else:
            return Move.NONE


pathDirections = [[0, 1], [0, -1], [-1, 0], [1, 0]]

dirIndexToEnum = [Direction.DOWN, Direction.UP, Direction.LEFT, Direction.RIGHT]

def get_dir(gameboard, player, targetPos):
    for i in range(len(pathDirections)):
        newX = (player.x + pathDirections[i][0]) % gameboard.width  
        newY = (player.y + pathDirections[i][1]) % gameboard.height
        if newX == targetPos[0] and newY == targetPos[1]:
            return dirIndexToEnum[i]
    return None

def manhattan_distance(start, end):
    return (abs(start[0]-end[0])+abs(start[1]-end[1]))

def find_path_A_star(start, end, gameboard):
    ''' Finds the closest path from point a to point b.
    based on http://theory.stanford.edu/~amitp/game-programming/a-star-flash/Pathfinder.as
Original code under MIT license, attached:
<http://www.opensource.org/licenses/mit-license.php>

Permission is hereby granted, free of charge, to any person obtaining 
a copy of this software and associated documentation files (the 
"Software"), to deal in the Software without restriction, including 
without limitation the rights to use, copy, modify, merge, publish, 
distribute, sublicense, and/or sell copies of the Software, and to 
permit persons to whom the Software is furnished to do so, subject to 
the following conditions: 
  
The above copyright notice and this permission notice shall be included 
in all copies or substantial portions of the Software. 
  
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY 
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. 

    '''
    pathDirections = [[0, -1], [0, 1], [-1, 0], [1, 0]]
    # g = already travelled, h = approx. how much to travel still, 
    initialobj = {'node': start, 'open': True, 'closed': False, 'parent': None, 'g': 0, 'h': manhattan_distance(start, end), 'f': manhattan_distance(start, end)}
    bopen = [initialobj]
    bvisited = {initialobj['node']: initialobj}
    while len(bopen) > 0:
        bopen.sort(key=lambda a: a['f']) # sort the array to find the one with the lowest approximate distance to the goal
        best = bopen.pop(0)
        best['open'] = False
        if best['node'] == end: # finished
            # todo retrace the path
            
            return retrace_path(bvisited, best, start)
        # modified for Orbis 2015
        for direction in pathDirections:
            x = (best['node'][0] + direction[0]) % gameboard.width
            y = (best['node'][1] + direction[1]) % gameboard.height
            if gameboard.wall_at_tile[x][y] or (x != end[0] and y != end[1] and gameboard.turret_at_tile[x][y]):
                continue
            newnode = (x, y)
            dist = manhattan_distance(best['node'], newnode)
            if gameboard.power_up_at_tile[x][y]:
                dist = 0
            nodeobj = None
            try:
                nodeobj = bvisited[newnode]
            except KeyError:
                nodeobj = {'node': newnode, 'open': False, 'closed': False, 'parent': best, 'g': 999999, 'h': 999999, 'f': 999999}
                bvisited[newnode] = nodeobj
            # calculate the new g value - already travelled
            new_g = best['g'] + dist
            if new_g < nodeobj['g']: # first time seeing it or new cost is better than old cost (taking different path)
                        # if true, use this path to travel to it
                if not nodeobj['open']:
                    nodeobj['open'] = True
                    bopen.append(nodeobj)
                nodeobj['g'] = new_g # update to the shorter value
                nodeobj['h'] = manhattan_distance(newnode, end)
                nodeobj['f'] = new_g + nodeobj['h']
                nodeobj['parent'] = best
    return None

def retrace_path(bvisited, best, start):
    path = []
    curvisited = best
    while curvisited != None and curvisited['node'] != start:
        path.append(curvisited['node'])
        curvisited = curvisited['parent']
    return path