import arcade
import os
import json

SPRITE_SCALING = 2
SPRITE_NATIVE_SIZE = 32
SPRITE_SIZE = int(SPRITE_NATIVE_SIZE * SPRITE_SCALING)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Sprite Enemies in a Platformer Example"

MOVEMENT_SPEED = 3
JUMP_SPEED = 10
GRAVITY = 0.5


class MarioArcade(arcade.Window):

	def __init__(self):

		super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

		file_path = os.path.dirname(os.path.abspath(__file__))
		os.chdir(file_path)

		self.RightBorders = None
		self.Obstacles = None
		self.Enemies = None
		self.Player = None
		self.Goal = None

		self.points = 0
		self.levels = ["level1.csv", "level2.csv"]
		self.current = 0
		self.won = False

	def setup(self):
		self.reloading = True
		self.physics_engine = None
		self.game_over = False
		self.wlength = 0
		self.wheight = 0

		self.RightBorders = arcade.SpriteList()
		self.Obstacles = arcade.SpriteList()
		self.Enemies = arcade.SpriteList()
		self.Player = arcade.SpriteList()
		self.Goal = arcade.SpriteList()

		levelMap = self.load(self.levels[self.current])

		self.wlength = len(levelMap[0])
		self.wheight = SCREEN_HEIGHT // len(levelMap) + 2
		SPRITE_SCALING = self.wheight / SPRITE_NATIVE_SIZE

		for i in range(0, len(levelMap)):
			for j in range(0, self.wlength):
				shallDraw = True
				tile = arcade.Sprite()

				if levelMap[i][j] == "R":
					tile = arcade.Sprite("wall.png", SPRITE_SCALING)
					tile.alpha = 1
					self.RightBorders.append(tile)
					tile.width = 1e4

				if levelMap[i][j] == "L":
					tile = arcade.Sprite("wall.png", SPRITE_SCALING)
					tile.alpha = 0
					self.Obstacles.append(tile)
					tile.width = 1

				if levelMap[i][j] == "S":
					shallDraw = False
					continue
				if levelMap[i][j] == "G":
					tile = arcade.Sprite("ground.png", SPRITE_SCALING)
					self.Obstacles.append(tile)
				if levelMap[i][j] == "W":
					tile = arcade.Sprite("wall.png", SPRITE_SCALING)
					self.Obstacles.append(tile)

				if levelMap[i][j] == "P":
					tile = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", SPRITE_SCALING / 2.5)
					self.Player.append(tile)

				if levelMap[i][j].startswith("E"):
					if levelMap[i][j] == "E1":
						tile = arcade.Sprite("enemy1.png", SPRITE_SCALING)
					if levelMap[i][j] == "E2":
						tile = arcade.Sprite("enemy2.png", SPRITE_SCALING)
					self.Enemies.append(tile)
					tile.boundary_right = SPRITE_SIZE * 3 + j * self.wheight * 0.97
					tile.boundary_left = -SPRITE_SIZE * 3 + j * self.wheight * 0.97
					tile.change_x = 1
				if levelMap[i][j] == "T1":
					tile = arcade.Sprite("trap1.png", SPRITE_SCALING)
					self.Enemies.append(tile)
				if levelMap[i][j] == "T2":
					tile = arcade.Sprite("trap2.png", SPRITE_SCALING)
					self.Enemies.append(tile)
				if levelMap[i][j] == "C":
					tile = arcade.Sprite("coin.png", SPRITE_SCALING)
					self.Goal.append(tile)
				if levelMap[i][j] == "F":
					tile = arcade.Sprite("goal.png", SPRITE_SCALING)
					self.Goal.append(tile)

				if shallDraw:
					tile.bottom = SCREEN_HEIGHT - (i + 1) * self.wheight * 0.97
					tile.left = j * self.wheight * 0.97

		for b in self.RightBorders:
			self.Obstacles.append(b)
		self.physics_engine = arcade.PhysicsEnginePlatformer(self.Player[0], self.Obstacles, gravity_constant=GRAVITY)
		arcade.set_background_color(arcade.color.AERO_BLUE)
		self.reloading = False

	def load(self, path):
		res = []
		f = open(path, "r")
		lines = f.readlines()
		res = [l.replace("\n", "").split(",") for l in lines]
		return res

	def on_draw(self):
		arcade.start_render()
		if self.won:
			arcade.draw_text(str(self.points), 200, 200,  arcade.color.AMARANTH_PURPLE, 160)
			return
		arcade.draw_text(str(self.points), 700, 520,  arcade.color.AMARANTH_PURPLE, 48)
		self.Obstacles.draw()
		self.Enemies.draw()
		self.Player.draw()
		self.Goal.draw()

	def on_key_press(self, key, modifiers):
		if key == arcade.key.S:
			self.save()
		if self.won:
			if key == arcade.key.ENTER:
				exit()
			return
		if key == arcade.key.UP:
			if self.physics_engine.can_jump():
				self.Player[0].change_y = JUMP_SPEED
		elif key == arcade.key.LEFT:
			self.Player[0].change_x = -MOVEMENT_SPEED
		elif key == arcade.key.RIGHT:
			self.Player[0].change_x = MOVEMENT_SPEED

	def on_key_release(self, key, modifiers):
		if key == arcade.key.UP or key == arcade.key.DOWN:
			self.Player[0].change_y = 0
		elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
			self.Player[0].change_x = 0

	def on_update(self, delta_time):
		if self.reloading:
			return

		self.physics_engine.update()
		self.Player.update()

		if self.Player[0].left >= SCREEN_WIDTH / 2:
			for objects in [self.Obstacles, self.Enemies, self.Goal]:
				for object in objects:
					object.left -= self.Player[0].left - SCREEN_WIDTH / 2

		if self.Player[0].left < 0:
			self.Player[0].left = 0

		if len(arcade.check_for_collision_with_list(self.Player[0],    self.RightBorders)):
			game_over = True
			self.win()
			return

		coins = arcade.check_for_collision_with_list(self.Player[0], self.Goal)
		if len(coins):
			self.points += 1
			coins[0].remove_from_sprite_lists()
			return

		if self.Player[0].bottom >= SCREEN_HEIGHT:
			game_over = True
			self.lose()
			return

		if len(arcade.check_for_collision_with_list(self.Player[0],    self.Enemies)):
			game_over = True
			self.lose()
			return

		for enemy in self.Enemies:
			for walls in [self.Obstacles, self.Enemies]:
				if len(arcade.check_for_collision_with_list(enemy, walls)) > 0:
					enemy.change_x *= -1
			if enemy.boundary_left is not None and enemy.left <= enemy.boundary_left:
				enemy.change_x *= -1
			if enemy.boundary_right is not None and enemy.right >= enemy.boundary_right:
				enemy.change_x *= -1
		self.Enemies.update()

		self.Obstacles.update()
		self.Goal.update()

	def win(self):
		if self.current + 1 < len(self.levels):
			self.current += 1
			self.setup()
		else:
			self.won = True

	def lose(self):
		self.setup()

	def save(self):
		j = json.dumps({"currentLevel": self.current, "points": self.points})
		# yes, I know it's a weak spot that allows to earn unlimited points on save-load. who cares?
		f = open("save.json", "w")
		f.write(j)
		f.close()


def main():
	window = MarioArcade()
	if os.path.exists("save.json"):
		print ("Found previous save. L to load, any other key to start a new game")
		inp = input()
		if inp == "L" or inp == "l":
			f = open("save.json", "r")
			loaded = json.loads(f.read())
			p = loaded["points"]
			c = loaded["currentLevel"]
			window.current = c
			window.points = p
	window.setup()
	arcade.run()


if __name__ == "__main__":
	main()
