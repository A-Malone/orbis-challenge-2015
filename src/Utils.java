import java.awt.Point;

/**
 * A utility class containing several coordinate-wrapping functions and other
 * useful things.
 * 
 * @author wesley
 *
 */
public final class Utils {
	/**
	 * Converts a {@link Direction} into a unit vector in that direction.
	 * 
	 * @return a unit vector or the zero vector
	 */
	public static Point directionToPoint(Direction d) {
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

	/**
	 * Wraps a single integer c at a maximum of max.<br>
	 * Usage: <code>wrapCoord(x, gameboard.getWidth())</code>
	 */
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

	/**
	 * Wraps a 1D vector x1->x2 at a maximum of max. {@link wrapDistance} does
	 * the same thing without preserving direction.<br>
	 * Usage: <code>wrapCoord(x, gameboard.getWidth())</code>
	 */
	public static int wrapDistanceSigned(int x1, int x2, int max) {
		int dx = x2 - x1;
		int dx2 = dx < 0 ? dx + max : dx - max;
		if (Math.abs(dx) < Math.abs(dx2)) {
			return dx;
		}
		return dx2;
	}

	/**
	 * Calculates the Manhattan distance between two points, accounting for map
	 * wrapping at maxx and maxy.
	 * 
	 * @return the Manhattan Distance
	 */
	public static int manDistance(int x, int y, int x2, int y2, int maxx, int maxy) {
		int dx = wrapDistance(x, x2, maxx);
		int dy = wrapDistance(y, y2, maxy);
		return dx + dy;
	}
}
