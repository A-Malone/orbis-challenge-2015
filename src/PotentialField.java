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

	public Path getBestPath(Gameboard gameboard, int startX, int startY, int finishX, int finishY)
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
		allNodes[finishX][finishY].distanceFromStart = 0;
		Set<Node> closedSet = new HashSet<>();
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
				// Account for turning costs
				if (current.parent != null) {
					int dxFromParent = current.parent.x - current.x;
					int dyFromParent = current.parent.y - current.y;
					int dxToNeighbor = current.x - n.x;
					int dyToNeighbor = current.y - n.y;
					if (dxFromParent != dxToNeighbor || dyFromParent != dyToNeighbor) {
						tentative_g_score += pmap[current.x][current.y] + 1;
					}
				}
				// Append to open set
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

	private Path rebuildPath(Node[][] allNodes, int startX, int startY, int finishX, int finishY) {
		Deque<Point> path = new ArrayDeque<>();
		Node current = allNodes[startX][startY];
		while (current.x != finishX || current.y != finishY) {
			// Go to next one
			current = current.parent;
			// Push it into the path
			path.add(new Point(current.x, current.y));
		}
		return new Path(path, allNodes[startX][startY].distanceFromStart);
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
		allNodes[startX][startY].distanceFromStart = 0;
		Set<Node> closedSet = new HashSet<>();
		// If we can't make it to our destination in less than maxDistance
		// steps, there is a wall in the way
		int maxDistance = manDistance(gameboard, startX, startY, finishX, finishY);
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
				if (tentative_g_score < n.distanceFromStart) {
					n.distanceFromStart = tentative_g_score;
					n.heuristicCost = n.distanceFromStart + manDistance(gameboard, n.x, n.y, finishX, finishY);
					openSet.add(n);
				}
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

		// Opponent
		applyInfluenceShape(gameboard, pmap, opponent.x, opponent.y, opponent.direction,
				InfluenceShapes.getPlayerPattern(opponent.getLaserCount() > 0));
		// Bullets
		for (Bullet b : gameboard.getBullets()) {
			applyInfluenceShape(gameboard, pmap, b.x, b.y, b.direction, InfluenceShapes.getBulletPattern());
		}
		// Turrets
		for (Turret t : gameboard.getTurrets()) {
			int timeToFire = (gameboard.getCurrentTurnNumber() % (t.getFireTime() + t.getCooldownTime())) - 1;
			applyInfluenceShape(gameboard, pmap, t.x, t.y, Direction.UP, InfluenceShapes.getTurretPattern(timeToFire));
		}
	}

	private void applyInfluenceShape(Gameboard gameboard, int[][] pmap, int ix, int iy, Direction direction,
			Map<Point, Integer> shape) throws MapOutOfBoundsException {
		switch (direction) {
		case DOWN:
			for (Entry<Point, Integer> s : shape.entrySet()) {
				Point p = s.getKey();
				Integer v = s.getValue();
				// Transform
				int x = wrapCoord(ix + p.x, gameboard.getWidth());
				int y = wrapCoord(iy - p.y, gameboard.getHeight());
				if (!checkForWall(gameboard, ix, iy, x, y)) {
					// Add value
					pmap[x][y] += v;
				}
			}
			break;
		case LEFT:
			for (Entry<Point, Integer> s : shape.entrySet()) {
				Point p = s.getKey();
				Integer v = s.getValue();
				// Transform
				int x = wrapCoord(ix - p.y, gameboard.getWidth());
				int y = wrapCoord(iy + p.x, gameboard.getHeight());
				if (!checkForWall(gameboard, ix, iy, x, y)) {
					// Add value
					pmap[x][y] += v;
				}
			}
			break;
		case RIGHT:
			for (Entry<Point, Integer> s : shape.entrySet()) {
				Point p = s.getKey();
				Integer v = s.getValue();
				// Transform
				int x = wrapCoord(ix + p.y, gameboard.getWidth());
				int y = wrapCoord(iy + p.x, gameboard.getHeight());
				if (!checkForWall(gameboard, ix, iy, x, y)) {
					// Add value
					pmap[x][y] += v;
				}
			}
			break;
		case UP:
			for (Entry<Point, Integer> s : shape.entrySet()) {
				Point p = s.getKey();
				Integer v = s.getValue();
				// Transform
				int x = wrapCoord(ix + p.x, gameboard.getWidth());
				int y = wrapCoord(iy + p.y, gameboard.getHeight());
				if (!checkForWall(gameboard, ix, iy, x, y)) {
					// Add value
					pmap[x][y] += v;
				}
			}
			break;
		default:
			throw new MapOutOfBoundsException("Impossible direction!");
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

	public static int wrapDistance(int x1, int x2, int max) {
		int dx = Math.abs(x1 - x2);
		return Math.min(dx, Math.abs(dx - max));
	}

	public int manDistance(Gameboard gameboard, int x, int y, int x2, int y2) {
		int dx = wrapDistance(x, x2, gameboard.getWidth());
		int dy = wrapDistance(y, y2, gameboard.getHeight());
		return dx + dy;
	}
}
