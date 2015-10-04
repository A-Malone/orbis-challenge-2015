import java.awt.Point;

public final class Utils {
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

	public static int wrapCoord(int c, int max) {
		if (c <= -1) {
			return c + max;
		} else if (c >= max) {
			return c - max;
		}
		return c;
	}

	public static int wrapDistanceSigned(int x1, int x2, int max) {
		int dx = x2 - x1;
		int dx2 = dx < 0 ? dx + max : dx - max;
		if (Math.abs(dx) < Math.abs(dx2)) {
			return dx;
		}
		return dx2;
	}

	public static int wrapDistance(int x1, int x2, int max) {
		int dx = Math.abs(x1 - x2);
		return Math.min(dx, Math.abs(dx - max));
	}

	public static int manDistance(int x, int y, int x2, int y2, int maxx, int maxy) {
		int dx = wrapDistance(x, x2, maxx);
		int dy = wrapDistance(y, y2, maxy);
		return dx + dy;
	}
}
