import java.util.*;
import java.util.Map.Entry;
import java.awt.Point;

public class PlayerAI extends ClientAI {
	public PlayerAI() {
	}

	@Override
	public Move getMove(Gameboard gameboard, Opponent opponent, Player player)
			throws NoItemException, MapOutOfBoundsException {
		// Check for wall tester
		// System.out.println(checkForWall(gameboard, new Point(1, 0), new
		// Point(3, 0)) + " == true");
		// System.out.println(checkForWall(gameboard, new Point(1, 0), new
		// Point(2, 1)) + " == false");
		// System.out.println(checkForWall(gameboard, new Point(2, 5), new
		// Point(2, 2)) + " == true");
		// System.out.println(checkForWall(gameboard, new Point(0, 3), new
		// Point(4, 3)) + " == false");

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

	private boolean checkForWall(Gameboard gameboard, Point start, Point finish) throws MapOutOfBoundsException {
		Node[][] allNodes = new Node[gameboard.getWidth()][gameboard.getHeight()];
		for (int x = 0; x < gameboard.getWidth(); x++) {
			for (int y = 0; y < gameboard.getHeight(); y++) {
				allNodes[x][y] = new Node(x, y);
			}
		}
		Queue<Node> openSet = new PriorityQueue<>((n1, n2) -> {
			return n1.heuristicCost - n2.heuristicCost;
		});
		openSet.add(allNodes[start.x][start.y]);
		Set<Node> closedSet = new HashSet<>();
		// If we can't make it to our destination in less than maxDistance
		// steps, there is a wall in the way
		int maxDistance = manDistance(gameboard, start.getX(), start.getY(), finish.getX(), finish.getY()) + 5;
		System.out.println(maxDistance);
		for (int i = 0; i < maxDistance && !openSet.isEmpty(); i++) {
			Node current = openSet.poll();
			System.out.println(current.x + ", " + current.y);
			// Finish
			if (current.x == finish.x && current.y == finish.y) {
				return false;
			}
			closedSet.add(current);
			// Neighbors
			for (Node n : getNeighbors(gameboard, allNodes, current)) {
				if (closedSet.contains(n) || gameboard.isWallAtTile(n.x, n.y) || gameboard.isTurretAtTile(n.x, n.y)) {
					continue;
				}
				int tentative_g_score = current.distanceFromStart + 1;
				n.distanceFromStart = tentative_g_score;
				n.heuristicCost = n.distanceFromStart + manDistance(gameboard, n.x, n.y, finish.x, finish.y);
				openSet.add(n);
			}
		}
		return true;
	}

	private int manDistance(Gameboard gameboard, double x, double y, double x2, double y2) {
		int dx = (int) (Math.abs(x2 - x));
		int dy = (int) (Math.abs(y2 - y));
		return Math.min(dx, Math.abs(dx - gameboard.getWidth() / 2))
				+ Math.min(dy, Math.abs(dy - gameboard.getHeight() / 2));
	}

	private List<Node> getNeighbors(Gameboard gameboard, Node[][] allNodes, Node current) {
		final int gw = gameboard.getWidth();
		final int gh = gameboard.getHeight();
		List<Node> points = new ArrayList<>();
		points.add(allNodes[wrapCoord(current.x - 1, gw)][wrapCoord(current.y, gh)]);
		points.add(allNodes[wrapCoord(current.x + 1, gw)][wrapCoord(current.y, gh)]);
		points.add(allNodes[wrapCoord(current.x, gw)][wrapCoord(current.y - 1, gh)]);
		points.add(allNodes[wrapCoord(current.x, gw)][wrapCoord(current.y + 1, gh)]);
		return points;
	}

	public int[][] getPotentialMap(Gameboard gameboard, Opponent opponent, Player player)
			throws MapOutOfBoundsException {
		int[][] pmap = new int[gameboard.getWidth()][gameboard.getHeight()];
		// Default is right-facing

		// Me
		pmap[player.getX()][player.getY()] = 10000;
		// Opponent
		pmap[opponent.getX()][opponent.getY()] = -10000;
		// Bullets
		Map<Point, Integer> bulletShape = new HashMap<>();
		bulletShape.put(new Point(0, 1), 2);
		bulletShape.put(new Point(0, 2), 1);
		for (Bullet b : gameboard.getBullets()) {
			switch (b.getDirection()) {
			case DOWN:
				for (Entry<Point, Integer> s : bulletShape.entrySet()) {
					Point p = s.getKey();
					Integer v = s.getValue();
					// Transform
					int x = wrapCoord(b.getX() + (int) p.getX(), gameboard.getWidth());
					int y = wrapCoord(b.getY() - (int) p.getY(), gameboard.getHeight());
					// Add value
					pmap[x][y] += v;
				}
				break;
			case LEFT:
				for (Entry<Point, Integer> s : bulletShape.entrySet()) {
					Point p = s.getKey();
					Integer v = s.getValue();
					// Transform
					int x = wrapCoord(b.getX() - (int) p.getY(), gameboard.getWidth());
					int y = wrapCoord(b.getY() + (int) p.getX(), gameboard.getHeight());
					// Add value
					pmap[x][y] += v;
					System.out.println(x + ", " + y);
				}
				break;
			case RIGHT:
				for (Entry<Point, Integer> s : bulletShape.entrySet()) {
					Point p = s.getKey();
					Integer v = s.getValue();
					// Transform
					int x = wrapCoord(b.getX() + (int) p.getY(), gameboard.getWidth());
					int y = wrapCoord(b.getY() + (int) p.getX(), gameboard.getHeight());
					// Add value
					pmap[x][y] += v;
				}
				break;
			case UP:
				for (Entry<Point, Integer> s : bulletShape.entrySet()) {
					Point p = s.getKey();
					Integer v = s.getValue();
					// Transform
					int x = wrapCoord(b.getX() + (int) p.getX(), gameboard.getWidth());
					int y = wrapCoord(b.getY() + (int) p.getY(), gameboard.getHeight());
					// Add value
					pmap[x][y] += v;
				}
				break;
			default:
				throw new MapOutOfBoundsException("Impossible bullet direction!");
			}
		}
		// Turrets
		Map<Point, Integer> turretShape = new HashMap<>();
		for (int dx = -4; dx < 4; dx++) {
			turretShape.put(new Point(dx, 0), 3);
		}
		for (int dy = -4; dy < 4; dy++) {
			turretShape.put(new Point(0, dy), 3);
		}
		for (Turret t : gameboard.getTurrets()) {
			if (t.isFiringNextTurn()) {
				for (Entry<Point, Integer> s : turretShape.entrySet()) {
					Point p = s.getKey();
					Integer v = s.getValue();
					// Transform
					int x = wrapCoord(t.getX() + (int) p.getX(), gameboard.getWidth());
					int y = wrapCoord(t.getY() + (int) p.getY(), gameboard.getHeight());
					// Add value
					pmap[x][y] += v;
				}
			}
		}
		return pmap;
	}

	public int wrapCoord(int c, int max) {
		if (c <= -1) {
			return c + max;
		} else if (c >= max) {
			return c - max;
		}
		return c;
	}
}
