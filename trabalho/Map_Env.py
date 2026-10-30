from maspy import *
from maspy.learning import *
from collections import deque
from random import randint
from threading import Lock
import random

def generate_map_with_walls(width, height, targets, wall_prob=0.1, max_attempts=2000):
    def neighbors(x, y):
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < width and 0 <= ny < height:
                yield nx, ny

    for _ in range(max_attempts):
        walls = {(x, y) for x in range(width) for y in range(height)
                 if random.random() < wall_prob and (x, y) not in targets}

        queue = deque([targets[0]])
        reachable = {targets[0]}
        while queue:
            cx, cy = queue.popleft()
            for nx, ny in neighbors(cx, cy):
                if (nx, ny) not in walls and (nx, ny) not in reachable:
                    reachable.add((nx, ny))
                    queue.append((nx, ny))

        total_open = width * height - len(walls)
        if len(reachable) == total_open:
            available = sorted(reachable)
            return walls, available

    raise RuntimeError("Failed to generate a valid map.")

class Map(Environment):
    def __init__(self, map_size=(10, 10), walls_prob=0.1):
        super().__init__()
        self.printing = False
        self.moves = {
            "up": (0, -1),"down": (0, 1), 
            "right": (1, 0), "left": (-1, 0),
        }
        self.map_size = map_size
        if map_size[0] * map_size[1] < 2:
             raise ValueError("O mapa precisa ter pelo menos duas posições.")

        targets = random.sample(
            [(x, y) for x in range(map_size[0]) for y in range(map_size[1])],
            2
        )

        self.target_values = dict(zip(targets, (5, 10)))
        self.claimed = {}
        self.target_lock = Lock()
        
        self.print(f"Targets are at {targets}")

        positions = generate_map_with_walls(
            map_size[0], map_size[1], targets, walls_prob, 2000
        )

        for target in targets:
            self.create(Percept("target", target))
            
        for wall in positions[0]:
            self.create(Percept("wall", wall))

        self.create(Percept("position", positions[1], listed))
        self.possible_starts = "off-policy"
            
    def reset_positions(self, og_pos):
        found_pos = self.get(Percept("arrived_target", (Any, Any)), all=True)
        assert isinstance(found_pos, list)
        self.delete(found_pos)
        new_pos_prcpts = self.get(Percept("agt_position", (Any, Any)), all=True)
        assert isinstance(new_pos_prcpts, list)
        for pos_prcpt in new_pos_prcpts:
            pos_prcpt.change(values=og_pos[pos_prcpt.group])

    def on_connect(self, agt):
        targets = self.get(Percept("target", (Any, Any)), all=True)
        target_positions = [target.values for target in targets]

        free_positions = self.get(Percept("position"), ck_values=False).values
        candidates = [
            pos for pos in free_positions
            if pos not in target_positions
        ]

        if not candidates:
            raise ValueError("Não existe posição inicial livre fora dos targets.")

        distant_positions = [
            pos for pos in candidates
            if all(
                abs(pos[0] - target[0]) + abs(pos[1] - target[1])
                > self.map_size[0] / 2
                for target in target_positions
            )
        ]

        start_pos = random.choice(distant_positions or candidates)
        self.create(Percept("agt_position", start_pos, agt))
    
    def moviment(self, position, direction):
        dx, dy = self.moves[direction]
        new_x = max(0, min(position[0] + dx, self.map_size[0] - 1))
        new_y = max(0, min(position[1] + dy, self.map_size[1] - 1)) 
        return new_x, new_y

    def claim_target(self, agt, target):
        with self.target_lock:
            position = self.get(
                Percept("agt_position", (Any, Any), agt),
                ck_group=True
            ).values

            if (
                position != target
                or target not in self.target_values
                or target in self.claimed
                or agt in self.claimed.values()
            ):
                return False

            highest = max(
                self.target_values,
                key=self.target_values.get
            )

            if target != highest and highest not in self.claimed:
                return False

            self.claimed[target] = agt
            return True
    
    def move_transition(self, position, direction):
        reward = -1
        terminated = False
        
        new_position = self.moviment(position, direction)

        if self.has(Percept("target", new_position)):
            reward = 10
            terminated = True
        elif self.has(Percept("wall", new_position)) or position == new_position:
            reward = -10
        return new_position, reward, terminated
    
    @action(listed, ["up", "down", "left", "right"], move_transition)
    def move(self, agt, direction):
        arrivals = self.get(
            Percept("arrived_target", (Any, Any), agt),
            all=True,
            ck_group=True
        ) or []

        if arrivals:
            self.delete(arrivals)
        position = self.get(Percept("agt_position", (Any, Any), agt), ck_group=True)
        assert isinstance(position, Percept)
        
        wall_flag = False
        pos = position.values
        if direction == "stay":
            new_pos = pos
        else:
            new_pos = self.moviment(pos, direction)
            if self.has(Percept("wall", new_pos)):
                wall_flag = True
                new_pos = pos
            else:
                position.change(values=new_pos)
        
        n_pos = self.get(Percept("agt_position", (Any, Any), agt), ck_group=True).values
        if n_pos in self.target_values:
            value = self.target_values[n_pos]

            self.print(
                f"{agt} chegou ao target {n_pos}, valor {value}"
            )

            self.create(
                Percept("arrived_target", (n_pos, value), agt)
            )
        elif wall_flag:
            self.print(f"{agt} in {pos} moves {direction} but hits a wall")
        else:
            self.print(f"{agt} in {pos} moves {direction} to {n_pos}")