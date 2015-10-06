from PythonClientAPI.libs.Game.Enums import *
from PythonClientAPI.libs.Game.MapOutOfBoundsException import *

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.g = 0
        self.h = 0
        self.parent = None

class PlayerAI:
    def __init__(self):
        self.marked_turrets = []
        self.list_of_safe_moves = []
        self.path = []
        self.map_threshold = 11
        pass

    def move_right(self, player):
        #Face right if not already doing so, then move forward
        if player.direction != Direction.RIGHT:
            return self.try_move(self.list_of_safe_moves, Move.FACE_RIGHT)
        else:
            return self.try_move(self.list_of_safe_moves, Move.FORWARD)

    def move_up(self, player):
        #Face up if not already doing so, then move forward
        if player.direction != Direction.UP:
            return self.try_move(self.list_of_safe_moves, Move.FACE_UP)
        else:
            return self.try_move(self.list_of_safe_moves, Move.FORWARD)

    def move_left(self, player):
        #Face left if not already doing so, then move forward
        if player.direction != Direction.LEFT:
            return self.try_move(self.list_of_safe_moves, Move.FACE_LEFT)
        else:
            return self.try_move(self.list_of_safe_moves, Move.FORWARD)

    def move_down(self, player):
        #Face down if not already doing so, then move forward
        if player.direction != Direction.DOWN:
            return self.try_move(self.list_of_safe_moves, Move.FACE_DOWN)
        else:
            return self.try_move(self.list_of_safe_moves, Move.FORWARD)

    def move(self, gameboard, player, tx, ty):
        if self.path:
            if tx > player.x:
                if player.x == 0 and tx == gameboard.width - 1:
                    return self.move_left(player)
                return self.move_right(player)

            if tx < player.x:
                if player.x == gameboard.width - 1 and tx == 0:
                    return self.move_right(player)
                return self.move_left(player)

            if ty > player.y:
                if player.y == 0 and ty == gameboard.height - 1:
                    return self.move_up(player)
                return self.move_down(player)

            if ty < player.y:
                if player.y == gameboard.height - 1 and ty == 0:
                    return self.move_down(player)
                return self.move_up(player)
        else:
            return self.try_move(self.list_of_safe_moves, Move.FORWARD)

    def a_star_search(self, gameboard, start, end):
        #Returns the path from start to end
        open_set = set()
        closed_set = set()
        current = start
        open_set.add(current)
        while open_set:
            #Find the Node with smallest heuristic value
            current = min(open_set, key=lambda x:x.g + x.h)
            #Check if we found the end
            if current.x == end.x and current.y == end.y:
                path = []
                while current.parent:
                    #If we found the end, traverse the path we took and return it
                    path.append(current)
                    current = current.parent
                path.append(current)
                #Return path in correct order
                return path[::-1]
            open_set.remove(current)
            closed_set.add(current)
            children = []
            #Look at all the possible Nodes that we can move to from the current Node
            #Left
            tmpx, tmpy = self.fix_coordinates(gameboard, current.x - 1, current.y)
            if self.no_obstacle(gameboard, tmpx, tmpy):
                children.append(Node(tmpx, tmpy))
            #Right
            tmpx, tmpy = self.fix_coordinates(gameboard, current.x + 1, current.y)
            if self.no_obstacle(gameboard, tmpx, tmpy):
                children.append(Node(tmpx, tmpy))
            #Down
            tmpx, tmpy = self.fix_coordinates(gameboard, current.x, current.y - 1)
            if self.no_obstacle(gameboard, tmpx, tmpy):
                children.append(Node(tmpx, tmpy))
            #Up
            tmpx, tmpy = self.fix_coordinates(gameboard, current.x, current.y + 1)
            if self.no_obstacle(gameboard, tmpx, tmpy):
                children.append(Node(tmpx, tmpy))

            for node in children:
                if self.find(node, closed_set):
                    continue
                if self.find(node, open_set):
                    #If we can get to this node in a faster way, remember the faster way
                    g = current.g + self.get_smart_distance(gameboard, current.x, current.y, node.x, node.y)
                    if node.g > g:
                        node.g = g
                        node.parent = current
                else:
                    #If haven't explored this Node yet, explore it and set its heuristic values
                    node.g = current.g + self.get_smart_distance(gameboard, current.x, current.y, node.x, node.y)
                    node.h = self.get_smart_distance(gameboard, node.x, node.y, end.x, end.y)
                    node.parent = current
                    open_set.add(node)
        #Path not found
        return []

    def find(self, node, myset):
        #Returns True if node is in myset
        for i in myset:
            if node.x == i.x and node.y == i.y:
                return True
        return False

    def no_obstacle(self, gameboard, x, y):
        #Returns True if there is no wall or turrent at position (x, y)
        return not (gameboard.is_wall_at_tile(x, y) or gameboard.is_turret_at_tile(x, y))

    def get_smart_distance(self, gameboard, px, py, tx, ty):
        #Returns the correct distance from a tile considering board wrapping
        if px > tx:
            xdistance = min(px - tx, gameboard.width - px + tx)
        else:
            xdistance = min(tx - px, gameboard.width - tx + px)

        if py > ty:
            ydistance = min(py - ty, gameboard.height - py + ty)
        else:
            ydistance = min(ty - py, gameboard.height - ty + py)

        return xdistance + ydistance

    # Fix coordinates so they don't go off the map if they are out of bounds
    def fix_coordinates(self, gameboard, x, y):
        if x >= gameboard.width:
            x = x - gameboard.width
        if y >= gameboard.height:
            y = y - gameboard.height
        if x < 0:
            x = x + gameboard.width
        if y < 0:
            y = y + gameboard.height
        return x, y

    # Returns a list of blocked directions in the format [right, left, down, up] if the path is not blocked/reachable.
    # Returns False if the path is blocked/reachable.
    def is_a_clear_to_b(self, gameboard, static_val, var_axis, var_a, var_b, length = 100):
        x_up = 0
        x_down = 0
        y_up = 0
        y_down = 0

        if var_axis == "x":
            if var_a < var_b:
                # Check for a -> b and <- a   b <-
                if var_b - var_a <= length:
                    for x in range(var_a + 1, var_b):
                        x, y = self.fix_coordinates(gameboard, x, static_val)
                        if gameboard.is_wall_at_tile(x, y) or gameboard.is_turret_at_tile(x, y):
                            x_up = 1
                else:
                    x_up = 1
                if (gameboard.width - var_b) + var_a <= length:
                    for x in range(var_a - 1, var_b - gameboard.width, -1):
                        x, y = self.fix_coordinates(gameboard, x, static_val)
                        if gameboard.is_wall_at_tile(x, y) or gameboard.is_turret_at_tile(x, y):
                            x_down = 1
                else:
                    x_down = 1
            elif var_a > var_b:
                # Check for b -> a and <- b   a <-
                if (gameboard.width - var_a) + var_b <= length:
                    for x in range(var_a + 1, gameboard.width + var_b):
                        x, y = self.fix_coordinates(gameboard, x, static_val)
                        if gameboard.is_wall_at_tile(x, y) or gameboard.is_turret_at_tile(x, y):
                            x_up = 1
                else:
                    x_up = 1
                if var_a - var_b <= length:
                    for x in range(var_a - 1, var_b, -1):
                        x, y = self.fix_coordinates(gameboard, x, static_val)
                        if gameboard.is_wall_at_tile(x, y) or gameboard.is_turret_at_tile(x, y):
                            x_down = 1
                else:
                    x_down = 1
        elif var_axis == "y":
            if var_a < var_b:
                # Check for a -> b and <- a   b <-
                if var_b - var_a <= length:
                    for y in range(var_a + 1, var_b):
                        x, y = self.fix_coordinates(gameboard, static_val, y)
                        if gameboard.is_wall_at_tile(x, y) or gameboard.is_turret_at_tile(x, y):
                            y_up = 1
                else:
                    y_up = 1
                if (gameboard.height - var_b) + var_a <= length:
                    for y in range(var_a - 1, var_b - gameboard.height, -1):
                        x, y = self.fix_coordinates(gameboard, static_val, y)
                        if gameboard.is_wall_at_tile(x, y) or gameboard.is_turret_at_tile(x, y):
                            y_down = 1
                else:
                    y_down = 1
            elif var_a > var_b:
                # Check for b -> a and <- b   a <-
                if (gameboard.height - var_a) + var_b <= length:
                    for y in range(var_a + 1, gameboard.height + var_b):
                        x, y = self.fix_coordinates(gameboard, static_val, y)
                        if gameboard.is_wall_at_tile(x, y) or gameboard.is_turret_at_tile(x, y):
                            y_up = 1
                else:
                    y_up = 1
                if var_a - var_b <= length:
                    for y in range(var_a - 1, var_b, -1):
                        x, y = self.fix_coordinates(gameboard, static_val, y)
                        if gameboard.is_wall_at_tile(x, y) or gameboard.is_turret_at_tile(x, y):
                            y_down = 1
                else:
                    y_down = 1
        if (x_up and x_down) or (y_up and y_down):
            return False
        else:
            return [x_up, x_down, y_up, y_down]

    def does_a_laser_b(self, gameboard, a, b_x, b_y):
        b_x, b_y = self.fix_coordinates(gameboard, b_x, b_y)

        # Find if object a can laser to position (b_x, b_y)
        if a.x == b_x:
            # If the distance between the shooter and the target is >4 don't even bother
            if abs(a.y - b_y) <= 4 or (min(a.y, b_y) + gameboard.height - max(a.y, b_y)) <= 4:
                dist = min(abs(a.y - b_y), (min(a.y, b_y) + gameboard.height - max(a.y, b_y)))
                if self.is_a_clear_to_b(gameboard, a.x, "y", a.y, b_y, dist):
                    return True
        elif a.y == b_y:
            # If the distance between the shooter and the target is >4 don't even bother
            if abs(a.x - b_x) <= 4 or (min(a.x, b_x) + gameboard.width - max(a.x, b_x)) <= 4:
                dist = min(abs(a.x - b_x), (min(a.x, b_x) + gameboard.width - max(a.x, b_x)))
                if self.is_a_clear_to_b(gameboard, a.y, "x", a.x, b_x, dist):
                    return True
        return False


    def does_a_bullet_b(self, gameboard, a, b_x, b_y):
        b_x, b_y = self.fix_coordinates(gameboard, b_x, b_y)

        # Find if object a can shoot bullet to position (b_x, b_y)
        if a.direction == Direction.UP and b_x == a.x and b_y == a.y - 1 or \
            a.direction == Direction.DOWN and b_x == a.x and b_y == a.y + 1 or \
            a.direction == Direction.LEFT and b_x == a.x - 1 and b_y == a.y or \
            a.direction == Direction.RIGHT and b_x == a.x + 1 and b_y == a.y:
            return True
        return False

    # Makes a list of moves which will not lose you the game
    def find_safe_moves(self, gameboard, player, opponent):
        temp_list = [Move.SHOOT, Move.NONE, Move.FACE_DOWN, Move.FACE_UP, Move.FACE_LEFT, Move.FACE_RIGHT,
                     Move.SHIELD, Move.LASER, Move.TELEPORT_0, Move.TELEPORT_1, Move.TELEPORT_2, Move.TELEPORT_3,
                     Move.TELEPORT_4, Move.TELEPORT_5, Move.FORWARD]

        # Check if any turrets will laser your current or forward positions
        for turret in gameboard.turrets:
            if not (gameboard.current_turn + 1) % (turret.fire_time + turret.cooldown_time) == 0 and \
                not ((gameboard.current_turn + 1) % (turret.fire_time + turret.cooldown_time)) > turret.fire_time and \
                not turret.is_dead and not player.shield_active and turret not in self.marked_turrets:
                if self.does_a_laser_b(gameboard, turret, player.x, player.y):
                    if Move.FACE_DOWN in temp_list:
                        temp_list.remove(Move.FACE_DOWN)
                        temp_list.remove(Move.FACE_UP)
                        temp_list.remove(Move.FACE_LEFT)
                        temp_list.remove(Move.FACE_RIGHT)
                        temp_list.remove(Move.NONE)
                        temp_list.remove(Move.SHOOT)
                if player.direction == Direction.UP and self.does_a_laser_b(gameboard, turret, player.x, player.y - 1) or \
                    player.direction == Direction.DOWN and self.does_a_laser_b(gameboard, turret, player.x, player.y + 1) or \
                    player.direction == Direction.LEFT and self.does_a_laser_b(gameboard, turret, player.x - 1, player.y) or \
                    player.direction == Direction.RIGHT and self.does_a_laser_b(gameboard, turret, player.x + 1, player.y):
                        if Move.FORWARD in temp_list:
                            temp_list.remove(Move.FORWARD)

        # Check if your opponent will laser your current or forward positions
        if (not player.shield_active) and opponent.laser_count:
            if self.does_a_laser_b(gameboard, opponent, player.x, player.y):
                if Move.FACE_DOWN in temp_list:
                    temp_list.remove(Move.FACE_DOWN)
                    temp_list.remove(Move.FACE_UP)
                    temp_list.remove(Move.FACE_LEFT)
                    temp_list.remove(Move.FACE_RIGHT)
                    temp_list.remove(Move.NONE)
                    temp_list.remove(Move.SHOOT)
            if player.direction == Direction.UP and self.does_a_laser_b(gameboard, opponent, player.x, player.y - 1) or \
                player.direction == Direction.DOWN and self.does_a_laser_b(gameboard, opponent, player.x, player.y + 1) or \
                player.direction == Direction.LEFT and self.does_a_laser_b(gameboard, opponent, player.x - 1, player.y) or \
                player.direction == Direction.RIGHT and self.does_a_laser_b(gameboard, opponent, player.x + 1, player.y):
                    if Move.FORWARD in temp_list:
                        temp_list.remove(Move.FORWARD)

        # Check if any bullets will hit your current or forward positions
        for bullet in gameboard.bullets:
            if self.does_a_bullet_b(gameboard, bullet, player.x, player.y):
                if Move.FACE_DOWN in temp_list:
                    temp_list.remove(Move.FACE_DOWN)
                    temp_list.remove(Move.FACE_UP)
                    temp_list.remove(Move.FACE_LEFT)
                    temp_list.remove(Move.FACE_RIGHT)
                    temp_list.remove(Move.NONE)
                    temp_list.remove(Move.SHOOT)
            if player.direction == Direction.UP and self.does_a_bullet_b(gameboard, bullet, player.x, player.y - 1) or \
                player.direction == Direction.DOWN and self.does_a_bullet_b(gameboard, bullet, player.x, player.y + 1) or \
                player.direction == Direction.LEFT and self.does_a_bullet_b(gameboard, bullet, player.x - 1, player.y) or \
                player.direction == Direction.RIGHT and self.does_a_bullet_b(gameboard, bullet, player.x + 1, player.y):
                    if Move.FORWARD in temp_list:
                        temp_list.remove(Move.FORWARD)

        # Check if opponent will shoot your current or forward position
        if (not player.shield_active):
            if self.does_a_bullet_b(gameboard, opponent, player.x, player.y):
                if Move.FACE_DOWN in temp_list:
                    temp_list.remove(Move.FACE_DOWN)
                    temp_list.remove(Move.FACE_UP)
                    temp_list.remove(Move.FACE_LEFT)
                    temp_list.remove(Move.FACE_RIGHT)
                    temp_list.remove(Move.NONE)
                    temp_list.remove(Move.SHOOT)
            if player.direction == Direction.UP and self.does_a_bullet_b(gameboard, opponent, player.x, player.y - 1) or \
                player.direction == Direction.DOWN and self.does_a_bullet_b(gameboard, opponent, player.x, player.y + 1) or \
                player.direction == Direction.LEFT and self.does_a_bullet_b(gameboard, opponent, player.x - 1, player.y) or \
                player.direction == Direction.RIGHT and self.does_a_bullet_b(gameboard, opponent, player.x + 1, player.y):
                    if Move.FORWARD in temp_list:
                        temp_list.remove(Move.FORWARD)

        # Check if you have any of the power ups to use
        if player.laser_count == 0:
            temp_list.remove(Move.LASER)
        if player.shield_count == 0:
            temp_list.remove(Move.SHIELD)
        if player.teleport_count == 0:
            temp_list.remove(Move.TELEPORT_0)
            temp_list.remove(Move.TELEPORT_1)
            temp_list.remove(Move.TELEPORT_2)
            temp_list.remove(Move.TELEPORT_3)
            temp_list.remove(Move.TELEPORT_4)
            temp_list.remove(Move.TELEPORT_5)

        # Update the list of safe moves available
        self.list_of_safe_moves = temp_list

    # Tests a greedy move to see if it's safe to make. If it's not, use the most safe and viable move.
    # If no moves are available, just use your greedy move. #YOLO
    def try_move(self, list_of_safe_moves, move):
        if move in list_of_safe_moves:
            return move
        elif len(list_of_safe_moves) > 0:
            return list_of_safe_moves[0]
        else:
            return move

    # Try to kill a turret if you pass by it on the way to getting power ups.
    def kill_turret_yolo(self, gameboard, player, turret, static_axis):
        # Find the number of turns you will be safe in the turret's firing range.
        if (gameboard.current_turn % (turret.fire_time + turret.cooldown_time)) > turret.fire_time:
            num_of_safe_turns = turret.cooldown_time - \
                            ((gameboard.current_turn % (turret.fire_time + turret.cooldown_time)) - turret.fire_time)
        else:
            num_of_safe_turns = 0

        if static_axis == "x":
            # If out of turret range, you have all the turns you want to kill it
            if abs(player.x - turret.x) > 4 or abs((player.x + turret.x) - gameboard.width) > 4:
                num_of_safe_turns = 100

            # If the player has enough time to kill the turret while passing by, do it
            if self.is_a_clear_to_b(gameboard, turret.y, "x", player.x, turret.x)[0] == 0:
                # Turn and shoot turret to your right
                if (player.direction == Direction.UP or player.direction == Direction.DOWN) and num_of_safe_turns >= 3:
                    return self.try_move(self.list_of_safe_moves, Move.FACE_RIGHT)
                elif player.direction == Direction.RIGHT:
                    self.marked_turrets.append(turret)
                    return self.try_move(self.list_of_safe_moves, Move.SHOOT)
            elif self.is_a_clear_to_b(gameboard, turret.y, "x", player.x, turret.x)[1] == 0:
                # Turn and shoot turret to your left
                if (player.direction == Direction.UP or player.direction == Direction.DOWN) and num_of_safe_turns >= 3:
                    return self.try_move(self.list_of_safe_moves, Move.FACE_LEFT)
                elif player.direction == Direction.LEFT:
                    self.marked_turrets.append(turret)
                    return self.try_move(self.list_of_safe_moves, Move.SHOOT)

            # If you have a laser and can hit the turret, do it
            if player.laser_count > 0 and self.does_a_laser_b(gameboard, player, turret.x, turret.y):
                return self.try_move(self.list_of_safe_moves, Move.LASER)
            # If the turret can shoot you and you have a shield, use the shield to kill the turret
            if self.does_a_laser_b(gameboard, turret, player.x, player.y):
                if player.shield_active and num_of_safe_turns < 1:
                    return Move.SHOOT
                elif player.shield_count > 0 and num_of_safe_turns < 2:
                    return self.try_move(self.list_of_safe_moves, Move.SHIELD)

        elif static_axis == "y":
            # If out of turret range, you have all the turns you want to kill it
            if abs(player.y - turret.y) > 4 or abs((player.y + turret.y) - gameboard.height) > 4:
                num_of_safe_turns = 100

            # If the player has enough time to kill the turret while passing by, do it
            if self.is_a_clear_to_b(gameboard, turret.x, "y", player.y, turret.y)[2] == 0:
                # Turn and shoot turret to your down
                if (player.direction == Direction.LEFT or player.direction == Direction.RIGHT) and num_of_safe_turns >= 3:
                    return self.try_move(self.list_of_safe_moves, Move.FACE_DOWN)
                elif player.direction == Direction.DOWN:
                    self.marked_turrets.append(turret)
                    return self.try_move(self.list_of_safe_moves, Move.SHOOT)
            elif self.is_a_clear_to_b(gameboard, turret.x, "y", player.y, turret.y)[3] == 0:
                # Turn and shoot turret to your up
                if (player.direction == Direction.LEFT or player.direction == Direction.RIGHT) and num_of_safe_turns >= 3:
                    return self.try_move(self.list_of_safe_moves, Move.FACE_UP)
                elif player.direction == Direction.UP:
                    self.marked_turrets.append(turret)
                    return self.try_move(self.list_of_safe_moves, Move.SHOOT)

            # If you have a laser and can hit the turret, do it
            if player.laser_count > 0 and self.does_a_laser_b(gameboard, player, turret.x, turret.y):
                return self.try_move(self.list_of_safe_moves, Move.LASER)
            # If the turret can shoot you and you have a shield, use the shield to kill the turret
            if self.does_a_laser_b(gameboard, turret, player.x, player.y):
                if player.shield_active and num_of_safe_turns < 1:
                    return Move.SHOOT
                elif player.shield_count > 0 and num_of_safe_turns < 2:
                    return self.try_move(self.list_of_safe_moves, Move.SHIELD)
        return None

    def get_move(self, gameboard, player, opponent):
        # Get a list of moves that you are allowed to make this turn. This will be checked before any move is made.
        self.find_safe_moves(gameboard, player, opponent)

        # Try to kill opponent if they are in proximity and defenseless
        if player.laser_count > 0 and opponent.shield_count == 0 and not opponent.shield_active:
            if self.does_a_laser_b(gameboard, player, opponent.x, opponent.y):
                return self.try_move(self.list_of_safe_moves, Move.LASER)

        # Kill turret if it is in proximity and there is enough time to kill it
        for turret in gameboard.turrets:
            possible_move = None
            if not turret.is_dead and turret not in self.marked_turrets:
                if turret.x == player.x and self.is_a_clear_to_b(gameboard, player.x, "y", player.y, turret.y):
                    possible_move = self.kill_turret_yolo(gameboard, player, turret, "y")
                elif turret.y == player.y and self.is_a_clear_to_b(gameboard, player.y, "x", player.x, turret.x):
                    possible_move = self.kill_turret_yolo(gameboard, player, turret, "x")
            # Sometimes, the turret will be in a position where you can kill it but you don't have the means. In these
            # cases, you will let the poor turret go and be on your merry way.
            if possible_move != None:
                return possible_move

        # If there are no power ups to go for, you must hunt the enemy instead.
        if len(gameboard.power_ups) == 1:
            return self.find_opponent(gameboard, player, opponent)

        # If you have a path to the closest power up, keep following it.
        if self.path:
            if player.teleport_count > 0:
                return self.try_teleport(gameboard, player, self.path[-1].x, self.path[-1].y, opponent)

            if player.x == self.path[0].x and player.y == self.path[0].y:
                self.path = self.path[1:]

            if self.path:
                return self.move(gameboard, player, self.path[0].x, self.path[0].y)

        # If you don't have a path to a power up but there are power ups remaining, make a path to the next power up
        if len(gameboard.power_ups) > 0:
            #Get the power up!
            return self.get_power_up(gameboard, player, opponent)

    def try_teleport(self, gameboard, player, tx, ty, opponent):
        paths = []
        end = Node(tx, ty)
        shortest = self.path
        teleport = -1
        for i in range(len(gameboard.teleport_locations)):
            start = Node(gameboard.teleport_locations[i][0], gameboard.teleport_locations[i][1])
            temp = self.a_star_search(gameboard, start, end)
            if len(temp) < len(shortest):
                shortest = temp
                teleport = i
        if teleport == -1:
            if self.path:
                if player.x == self.path[0].x and player.y == self.path[0].y:
                    self.path = self.path[1:]
                if self.path:
                    return self.move(gameboard, player, self.path[0].x, self.path[0].y)
            if len(gameboard.power_ups) > 0:
                #Get the power up!
                return self.get_power_up(gameboard, player, opponent)
        else:
            self.path = []
            if teleport == 0:
                return Move.TELEPORT_0
            elif teleport == 1:
                return Move.TELEPORT_1
            elif teleport == 2:
                return Move.TELEPORT_2
            elif teleport == 3:
                return Move.TELEPORT_3
            elif teleport == 4:
                return Move.TELEPORT_4
            elif teleport == 5:
                return Move.TELEPORT_5


    def get_power_up(self, gameboard, player, opponent):
        #Find the closest power up for the player
        paths = []
        for power_up in gameboard.power_ups:
            if self.get_smart_distance(gameboard, player.x, player.y, power_up.x, power_up.y) < self.map_threshold:
                    start = Node(player.x, player.y)
                    end = Node(power_up.x, power_up.y)
                    paths.append(self.a_star_search(gameboard, start, end))
        self.path = min(paths, key=lambda x:len(x))
        self.path = self.path[1:]
        return self.move(gameboard, player, self.path[0].x, self.path[0].y)

    def find_opponent(self, gameboard, player, opponent):
        start = Node(player.x, player.y)
        end = Node(opponent.x, opponent.y)
        self.path = self.a_star_search(gameboard, start, end)
        self.path = self.path[1:]
        if player.teleport_count > 0:
            return self.try_teleport(gameboard, player, self.path[-1].x, self.path[-1].y, opponent)
        return self.move(gameboard, player, self.path[0].x, self.path[0].y)