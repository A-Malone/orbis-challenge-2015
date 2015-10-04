import java.awt.Point;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.Queue;
import java.util.Set;
import java.util.Map.Entry;

public class PotentialField {
	private int[][] pmap;

	public Queue<Point> getBestPath(Gameboard gameboard, int startX, int startY, int finishX, int finishY)
			throws NoPathException, MapOutOfBoundsException {
		Node[][] allNodes = new Node[gameboard.getWidth()][gameboard.getHeight()];
		for (int x = 0; x < gameboard.getWidth(); x++) {
			for (int y = 0; y < gameboard.getHeight(); y++) {
				allNodes[x][y] = new Node(x, y);
			}
		}
		Queue<Node> openSet = new PriorityQueue<>((n1, n2) -> {
			return n1.heuristicCost - n2.heuristicCost;
		});
		openSet.add(allNodes[finishX][finishY]);
		Set<Node> closedSet = new HashSet<>();
		// If we can't make it to our destination in less than maxDistance
		// steps, there is a wall in the way
		while (!openSet.isEmpty()) {
			Node current = openSet.poll();
			// Finish
			if (current.x == startX && current.y == startY) {
				return rebuildPath(allNodes, startX, startY, finishX, finishY);
			}
			closedSet.add(current);
			// Neighbors
			for (Node n : getNeighbors(gameboard, allNodes, current)) {
				if (closedSet.contains(n) || gameboard.isWallAtTile(n.x, n.y) || gameboard.isTurretAtTile(n.x, n.y)) {
					continue;
				}
				int tentative_g_score = current.distanceFromStart + pmap[current.x][current.y] + 1;
				if (tentative_g_score < n.distanceFromStart) {
					n.parent = current;
					n.distanceFromStart = tentative_g_score;
					n.heuristicCost = n.distanceFromStart + manDistance(gameboard, n.x, n.y, finishX, finishY);
					openSet.add(n);
				}
			}
		}
		throw new NoPathException();
	}

	private Deque<Point> rebuildPath(Node[][] allNodes, int startX, int startY, int finishX, int finishY) {
		Deque<Point> path = new ArrayDeque<>();
		Node current = allNodes[startX][startY];
		while (current.x != finishX || current.y != finishY) {
			// Go to next one
			current = current.parent;
			// Push it into the path
			path.add(new Point(current.x, current.y));
		}
		return path;
	}

	private boolean checkForWall(Gameboard gameboard, int startX, int startY, int finishX, int finishY)
			throws MapOutOfBoundsException {
		Node[][] allNodes = new Node[gameboard.getWidth()][gameboard.getHeight()];
		for (int x = 0; x < gameboard.getWidth(); x++) {
			for (int y = 0; y < gameboard.getHeight(); y++) {
				allNodes[x][y] = new Node(x, y);
			}
		}
		Queue<Node> openSet = new PriorityQueue<>((n1, n2) -> {
			return n1.heuristicCost - n2.heuristicCost;
		});
		openSet.add(allNodes[startX][startY]);
		Set<Node> closedSet = new HashSet<>();
		// If we can't make it to our destination in less than maxDistance
		// steps, there is a wall in the way
		int maxDistance = manDistance(gameboard, startX, startY, finishX, finishY) + 5;
		while (!openSet.isEmpty()) {
			Node current = openSet.poll();
			// Took too long to get to finish
			if (current.distanceFromStart > maxDistance) {
				return true;
			}
			// Success
			else if (current.x == finishX && current.y == finishY) {
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
				n.heuristicCost = n.distanceFromStart + manDistance(gameboard, n.x, n.y, finishX, finishY);
				openSet.add(n);
			}
		}
		return true;
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

	public void updatePotentialMap(Gameboard gameboard, Opponent opponent, Player player)
			throws MapOutOfBoundsException {
		pmap = new int[gameboard.getWidth()][gameboard.getHeight()];

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
					if (!checkForWall(gameboard, b.x, b.y, p.x, p.y)) {
						// Transform
						int x = wrapCoord(b.x + p.x, gameboard.getWidth());
						int y = wrapCoord(b.y - p.y, gameboard.getHeight());
						// Add value
						pmap[x][y] += v;
					}
				}
				break;
			case LEFT:
				for (Entry<Point, Integer> s : bulletShape.entrySet()) {
					Point p = s.getKey();
					Integer v = s.getValue();
					if (!checkForWall(gameboard, b.x, b.y, p.x, p.y)) {
						// Transform
						int x = wrapCoord(b.x - p.y, gameboard.getWidth());
						int y = wrapCoord(b.y + p.x, gameboard.getHeight());
						// Add value
						pmap[x][y] += v;
					}
				}
				break;
			case RIGHT:
				for (Entry<Point, Integer> s : bulletShape.entrySet()) {
					Point p = s.getKey();
					Integer v = s.getValue();
					if (!checkForWall(gameboard, b.x, b.y, p.x, p.y)) {
						// Transform
						int x = wrapCoord(b.x + p.y, gameboard.getWidth());
						int y = wrapCoord(b.y + p.x, gameboard.getHeight());
						// Add value
						pmap[x][y] += v;
					}
				}
				break;
			case UP:
				for (Entry<Point, Integer> s : bulletShape.entrySet()) {
					Point p = s.getKey();
					Integer v = s.getValue();
					if (!checkForWall(gameboard, b.x, b.y, p.x, p.y)) {
						// Transform
						int x = wrapCoord(b.x + p.x, gameboard.getWidth());
						int y = wrapCoord(b.y + p.y, gameboard.getHeight());
						// Add value
						pmap[x][y] += v;
					}
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
	}

	public int[][] getPotentialMap() {
		return pmap;
	}

	public static int wrapCoord(int c, int max) {
		if (c <= -1) {
			return c + max;
		} else if (c >= max) {
			return c - max;
		}
		return c;
	}

	public int manDistance(Gameboard gameboard, double x, double y, double x2, double y2) {
		int dx = (int) (Math.abs(x2 - x));
		int dy = (int) (Math.abs(y2 - y));
		return Math.min(dx, Math.abs(dx - gameboard.getWidth() / 2))
				+ Math.min(dy, Math.abs(dy - gameboard.getHeight() / 2));
	}
}
