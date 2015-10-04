import java.util.*;
import java.util.Map.Entry;
import java.awt.Point;

public class PlayerAI extends ClientAI {

	// ----CONSTANTS
	// ------------------------------------------------------------
	static final int POWERUP_SCORE = 200;
	static final int PLAYER_SCORE = 750;
	static final int TURRET_SCORE = 500;

	static final int DANGER_THRESHOLD = 6;

	// ----FIELDS
	// ------------------------------------------------------------
	private PotentialField potentialField;

	public PlayerAI() {
		potentialField = new PotentialField();
	}

	@Override
	public Move getMove(Gameboard gameboard, Opponent opponent, Player player)
			throws NoItemException, MapOutOfBoundsException {

		// ----Potential Field Update
		potentialField.updatePotentialMap(gameboard, opponent, player);
		for (int y = 0; y < gameboard.getHeight(); y++) {
			for (int x = 0; x < gameboard.getWidth(); x++) {
				System.out.print(potentialField.getPotentialMap()[x][y] + " ");
			}
			System.out.println();
		}

		// ----Check Current Danger
		int[][] potentialMap = potentialField.getPotentialMap();
		int currentDanger = potentialMap[player.x][player.y];
		if (currentDanger < DANGER_THRESHOLD) {

			// ----Check for targets
			// Check laser range
			if (player.getLaserCount() > 0) {
				for (Entry<Point, Integer> entry : InfluenceShapes.getTurretPattern(0).entrySet()) {
					Point point = new Point(entry.getKey());
					point.x = Utils.wrapCoord(point.x + player.x, gameboard.getWidth());
					point.y = Utils.wrapCoord(point.y + player.y, gameboard.getHeight());

					for (GameObjects obj : gameboard.getGameObjectsAtTile(point.x, point.y)) {
						if (obj instanceof Opponent) {
							// Check for guaranteed hit
							Opponent op = (Opponent) obj;
							Point diff = Utils.directionToPoint(op.getDirection());
							diff.translate(op.x - player.x, op.y - player.y);
							if (diff.x == 0 || diff.y == 0) {
								return Move.LASER;
							}
						}
					}
				}
			}

			// Check regular shot range
			for (int i = 1; i != 4; i++) {
				Point point = Utils.directionToPoint(player.direction);
				point.x = Utils.wrapCoord(point.x * i + player.x, gameboard.getWidth());
				point.y = Utils.wrapCoord(point.y * i + player.y, gameboard.getHeight());
				for (GameObjects obj : gameboard.getGameObjectsAtTile(point.x, point.y)) {
					if (obj instanceof Turret && !((Turret) obj).isDead()) {
						return Move.SHOOT;
					}
					if (obj instanceof Opponent) {
						if (i <= 2) {
							return Move.SHOOT;
						}
						Opponent op = (Opponent) obj;
						Point diff = Utils.directionToPoint(op.getDirection());
						diff.translate(op.x - player.x, op.y - player.y);
						if ((diff.x == 0) == (point.x == 0) && (diff.y < 0) == (point.y < 0)) {
							return Move.SHOOT;
						}
						if ((diff.y == 0) == (point.y == 0) && (diff.x < 0) == (point.x < 0)) {
							return Move.SHOOT;
						}
					}
				}
			}
		}

		// ----Plan movement
		// Get paths to the different powerups
		Move next_move = Move.NONE;

		Map<GameObjects, Integer> objectives = getObjectives(gameboard, opponent);
		if (objectives.size() > 0) {
			float best_roi = 0;
			Path shortest_path = null;
			for (Entry<GameObjects, Integer> entry : objectives.entrySet()) {
				try {
					GameObjects obj = entry.getKey();
					Path path = potentialField.getBestPath(gameboard, player, player.x, player.y, obj.x, obj.y);
					float roi = (float) (getReward(obj)) / path.cost;
					if (roi > best_roi) {
						best_roi = roi;
						shortest_path = path;
					}
				} catch (NoPathException e) {
					e.printStackTrace();
					continue;
				}
			}
			try {
				System.out.println(player.x + ", " + player.y + ", " + player.direction.toString());
				if (shortest_path != null) {
					System.out.println(shortest_path.path);
				}
				next_move = getNextMove(gameboard, player, shortest_path.path.peek());
			} catch (BadMoveException e) {
				e.printStackTrace();
			}
		}
		return next_move;
	}

	private Map<GameObjects, Integer> getObjectives(Gameboard gameboard, Opponent opponent) {
		Map<GameObjects, Integer> map = new HashMap<GameObjects, Integer>();
		for (PowerUp pup : gameboard.getPowerUps()) {
			map.put(pup, POWERUP_SCORE);
		}
		map.put(opponent, PLAYER_SCORE);
		for (Turret tur : gameboard.getTurrets()) {
			map.put(tur, TURRET_SCORE);
		}
		return map;
	}

	private int getReward(GameObjects obj) {
		if (obj instanceof PowerUp) {
			return POWERUP_SCORE;
		} else if (obj instanceof Opponent) {
			return PLAYER_SCORE;
		} else if (obj instanceof Turret) {
			return TURRET_SCORE;
		} else {
			return 0;
		}
	}

	/** Finds the direction required to go to an adjacent point */
	public static Direction getMoveDirection(Gameboard gameboard, int fromX, int fromY, int toX, int toY)
			throws BadMoveException {
		// Get the positional differences
		int dx = Utils.wrapDistanceSigned(fromX, toX, gameboard.getWidth());
		int dy = Utils.wrapDistanceSigned(fromY, toY, gameboard.getHeight());
		// Calculate the direction
		if (dx == 0 && dy == 1) {
			return Direction.DOWN;
		} else if (dx == 0 && dy == -1) {
			return Direction.UP;
		} else if (dx == 1 && dy == 0) {
			return Direction.RIGHT;
		} else if (dx == -1 && dy == 0) {
			return Direction.LEFT;
		} else {
			// Should never happen
			System.err.println(fromX + ", " + fromY + " -> " + toX + ", " + toY + " is " + dx + ", " + dy);
			throw new BadMoveException();
		}
	}

	/**
	 * Extracts the Move object from the current position inside the 'player'
	 * object, and the desired position 'pos'
	 */
	private Move getNextMove(Gameboard gameboard, Player player, Point pos) throws BadMoveException {
		Direction nextDir = getMoveDirection(gameboard, player.x, player.y, pos.x, pos.y);

		if (nextDir == player.direction) {
			return Move.FORWARD;
		} else {
			return Direction.directionToMovement(nextDir);
		}
	}

	/**
	 * Heuristic estimate of combat strength
	 */
	private int evaluateStrength(Combatant comb) {
		int strength = 0;

		strength += comb.getLaserCount() * 50;
		strength += comb.getShieldCount() * 50;
		strength += comb.isShieldActive() ? 100 : 0;

		return strength;
	}
}
