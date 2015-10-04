import java.util.*;
import java.util.Map.Entry;
import java.awt.Point;

public class PlayerAI extends ClientAI {

	// ----CONSTANTS
	// ------------------------------------------------------------
	static final int POWERUP_SCORE = 200;
	static final int PLAYER_SCORE = 750;
	static final int TURRET_SCORE = 500;

	// ----FIELDS
	// ------------------------------------------------------------
	private PotentialField potentialField;

	public PlayerAI() {
		potentialField = new PotentialField();
	}

	@Override
	public Move getMove(Gameboard gameboard, Opponent opponent, Player player)
			throws NoItemException, MapOutOfBoundsException {
		// Update the potential field
		potentialField.updatePotentialMap(gameboard, opponent, player);
		// TODO print potential
		for (int y = 0; y < gameboard.getHeight(); y++) {
			for (int x = 0; x < gameboard.getWidth(); x++) {
				System.out.print(potentialField.getPotentialMap()[x][y] + " ");
			}
			System.out.println();
		}

		Move next_move = Move.FORWARD;

		// Get paths to the different powerups
		Map<GameObjects, Integer> objectives = getObjectives(gameboard, opponent);
		if (objectives.size() > 0) {
			float best_roi = 0;
			Path shortest_path = null;
			for (Entry<GameObjects, Integer> entry : objectives.entrySet()) {
				try {
					GameObjects obj = entry.getKey();
					Path path = potentialField.getBestPath(gameboard, player.x, player.y, obj.x, obj.y);
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
				next_move = getNextMove(gameboard, player, shortest_path.path.peek());
				System.out.println(shortest_path.path);
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
			return TURRET_SCORE / 300;
		} else {
			System.err.println("NO TYPE??");
			return 0;
		}
	}

	private Move getNextMove(Gameboard gameboard, Player player, Point pos) throws BadMoveException {
		// Get the positional differences
		int dx = PotentialField.wrapDistance(pos.x, player.x, gameboard.getWidth());
		int dy = PotentialField.wrapDistance(pos.y, player.y, gameboard.getHeight());

		// Calculate the next direction
		Direction nextDir;
		if (dx == 0 && dy == 1) {
			nextDir = Direction.DOWN;
		} else if (dx == 0 && dy == -1) {
			nextDir = Direction.UP;
		} else if (dx == 1 && dy == 0) {
			nextDir = Direction.RIGHT;
		} else if (dx == -1 && dy == 0) {
			nextDir = Direction.LEFT;
		} else {
			// Should never happen
			System.err.println(player.x + ", " + player.y + " -> " + pos.x + ", " + pos.y);
			throw new BadMoveException();
		}

		if (nextDir == player.direction) {
			return Move.FORWARD;
		} else {
			return Direction.directionToMovement(nextDir);
		}
	}
}
