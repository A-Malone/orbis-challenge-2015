import java.util.*;
import java.util.Map.Entry;
import java.awt.Point;

public class PlayerAI extends ClientAI {
	PotentialField potentialField;

	public PlayerAI() {
		potentialField = new PotentialField();
	}

	@Override
	public Move getMove(Gameboard gameboard, Opponent opponent, Player player)
			throws NoItemException, MapOutOfBoundsException {
		potentialField.updatePotentialMap(gameboard, opponent, player);
		// Check for wall tester
		// System.out.println(checkForWall(gameboard, new Point(1, 0), new
		// Point(3, 0)) + " == true");
		// System.out.println(checkForWall(gameboard, new Point(1, 0), new
		// Point(2, 1)) + " == false");
		// System.out.println(checkForWall(gameboard, new Point(2, 5), new
		// Point(2, 2)) + " == true");
		// System.out.println(checkForWall(gameboard, new Point(0, 3), new
		// Point(4, 3)) + " == false");

		// Check pathfinder
		try {
			System.out.println(potentialField.getBestPath(gameboard, 1, 1, 3, 3));
		} catch (NoPathException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		// int[][] pmap = getPotentialMap(gameboard, opponent, player);
		// for (int y = 0; y < gameboard.getHeight(); y++) {
		// for (int x = 0; x < gameboard.getWidth(); x++) {
		// if (pmap[x][y] >= 9000) {
		// System.out.print("P");
		// } else if (pmap[x][y] <= -9000) {
		// System.out.print("O");
		// } else if (gameboard.isWallAtTile(x, y)) {
		// System.out.print("W");
		// } else {
		// System.out.print(pmap[x][y]);
		// }
		// System.out.print(" ");
		// }
		// System.out.println();
		// }

		// Write your AI here
		return Move.NONE;
	}
}
