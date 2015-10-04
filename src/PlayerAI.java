import java.util.*;
import java.util.Map.Entry;
import java.awt.Point;

public class PlayerAI extends ClientAI {

	// ----CONSTANTS
	// ------------------------------------------------------------
	static final int POWERUP_SCORE = 200;
	static final int PLAYER_SCORE = 750;
	static final int TURRET_SCORE = 500;

	static final int DANGER_THRESHOLD = 8;

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
		// TODO print potential
		for (int y = 0; y < gameboard.getHeight(); y++) {
			for (int x = 0; x < gameboard.getWidth(); x++) {
				System.out.print(potentialField.getPotentialMap()[x][y] + " ");
			}
			System.out.println();
		}

		// ----Check Current Danger
		int[][] potentialMap = potentialField.getPotentialMap();
		int currentDanger = potentialMap[player.x][player.y];

		// ----Check for targets
		// Players

		// ----Plan movement
		Move next_move = Move.FORWARD;

		// Get paths to the different powerups
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
				System.out.println(player.x + ", " + player.y);
				if (shortest_path != null) {
					System.out.println(shortest_path.path);
				}
				next_move = getNextMove(gameboard, player, shortest_path.path.peek());
			} catch (BadMoveException e) {
				// TODO Auto-generated catch block
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
			return PLAYER_SCORE / 1000;
		} else if (obj instanceof Turret) {
			return TURRET_SCORE / 1000;
		} else {
			return 0;
		}
	}

	/** Finds the direction required to go to an adjacent point */
	public static Direction getMoveDirection(Gameboard gameboard, int fromX, int fromY, int toX, int toY)
			throws BadMoveException {
		// Get the positional differences
		int dx = PotentialField.wrapDistanceSigned(fromX, toX, gameboard.getWidth());
		int dy = PotentialField.wrapDistanceSigned(fromY, toY, gameboard.getHeight());
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
