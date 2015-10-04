import java.util.*;
import java.util.Map.Entry;
import java.awt.Point;

public class PlayerAI extends ClientAI {

	// ----CONSTANTS
	// ------------------------------------------------------------
	static final int POWERUP_SCORE = 200;
	static final int PLAYER_SCORE = 750;
	static final int TURRET_SCORE = 500;

	// Parameters
	static final int DANGER_THRESHOLD = 8;
	static final int BLOODTHIRST = 2;
	static final int FEAR_OPPONENT = 5;

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

		// ----Create the move queue
		PriorityQueue<WeightedMove> moveQueue = new PriorityQueue<>((m1, m2) -> (int) (m2.roi - m1.roi));

		// ----Check Current Danger
		int[][] potentialMap = potentialField.getPotentialMap();
		int currentDanger = potentialMap[player.x][player.y];
		
		//Add in some ROI for standing still
		moveQueue.add(new WeightedMove(Move.NONE, (float)100 / currentDanger));

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

		// Check regular shot
		for (int i = 1; i != 4; i++) {
			Point point = Utils.directionToPoint(player.direction);
			point.x = Utils.wrapCoord(point.x * i + player.x, gameboard.getWidth());
			point.y = Utils.wrapCoord(point.y * i + player.y, gameboard.getHeight());
			for (GameObjects obj : gameboard.getGameObjectsAtTile(point.x, point.y)) {
				if (obj instanceof Wall) {
					break;
				} else if (obj instanceof Turret) {
					Turret tur = (Turret) obj;
					if (!tur.isDead()) {
						float roi = ((float) TURRET_SCORE) / currentDanger;
						moveQueue.add(new WeightedMove(Move.SHOOT, roi));
					} else {
						break;
					}
				} else if (obj instanceof Opponent) {
					Opponent op = (Opponent) obj;

					// Check for guaranteed hits
					Point diff = Utils.directionToPoint(op.getDirection());
					diff.translate(op.x - player.x, op.y - player.y);
					if ((diff.x == 0) == (point.x == 0) && (diff.y < 0) == (point.y < 0)) {
						return Move.SHOOT;
					} else if ((diff.y == 0) == (point.y == 0) && (diff.x < 0) == (point.x < 0)) {
						moveQueue.add(new WeightedMove(Move.SHOOT, ((float) PLAYER_SCORE) / (currentDanger)));
					} else {
						int dist_factor = (i > 2) ? i : 0;
						float roi = ((float) PLAYER_SCORE) / (currentDanger) / dist_factor;
						moveQueue.add(new WeightedMove(Move.SHOOT, roi));
					}
				}
			}
		}

		// ----Plan movement
		// Get paths to the different objectives
		Map<GameObjects, Integer> objectives = getObjectives(gameboard, player, opponent);

		for (Entry<GameObjects, Integer> entry : objectives.entrySet()) {
			try {
				GameObjects obj = entry.getKey();
				Path path = potentialField.getBestPath(gameboard, player, obj.x, obj.y);

				float roi = ((float) getReward(obj)) / path.cost * 100;
				Move first_move = getNextMove(gameboard, player, path.path.peek());

				moveQueue.add(new WeightedMove(first_move, roi));

			} catch (NoPathException e) {
				e.printStackTrace();
				continue;
			} catch (BadMoveException e) {
				e.printStackTrace();
				continue;
			}
		}

		// Return the move that leads to the best ROI
		return moveQueue.peek().move;
	}

	private Map<GameObjects, Integer> getObjectives(Gameboard gameboard, Player player, Opponent opponent) {
		Map<GameObjects, Integer> map = new HashMap<GameObjects, Integer>();
		for (PowerUp pup : gameboard.getPowerUps()) {
			map.put(pup, POWERUP_SCORE);
		}
		map.put(opponent,
				PLAYER_SCORE + BLOODTHIRST * evaluateStrength(player) - FEAR_OPPONENT * evaluateStrength(opponent));

		// Only care about live turrets
		gameboard.getTurrets().stream().filter(t -> !t.isDead()).forEach(t -> map.put(t, TURRET_SCORE));
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

		strength += comb.getHP() * 100;
		strength += comb.getLaserCount() * 50;
		strength += comb.getShieldCount() * 50;
		strength += comb.isShieldActive() ? 100 : 0;

		return strength;
	}

	private Point directionToPoint(Direction d) {
		switch (d) {
		case DOWN:
			return new Point(0, 1);
		case UP:
			return new Point(0, -1);
		case RIGHT:
			return new Point(1, 0);
		case LEFT:
			return new Point(-1, 0);
		default:
			return new Point(0, 0);
		}
	}
}
