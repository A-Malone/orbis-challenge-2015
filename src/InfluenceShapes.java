import java.awt.Point;
import java.util.HashMap;
import java.util.Map;

public class InfluenceShapes {
	private static Map<Point, Integer> bulletPattern;
	private static Map<Point, Integer> playerPattern;
	private static Map<Point, Integer> playerWithLaserPattern;

	static {
		bulletPattern = new HashMap<Point, Integer>();
		// Forward line
		bulletPattern.put(new Point(0, 1), 10);
		bulletPattern.put(new Point(0, 2), 9);
		bulletPattern.put(new Point(0, 3), 6);
		bulletPattern.put(new Point(0, 4), 4);
		// Side threats
		bulletPattern.put(new Point(1, 1), 4);
		bulletPattern.put(new Point(-1, 1), 4);
		bulletPattern.put(new Point(2, 1), 2);
		bulletPattern.put(new Point(-2, 1), 2);

		// Potential of being imminently shot at
		playerPattern = new HashMap<Point, Integer>(getBulletPattern());
		playerPattern.put(new Point(0, 0), 10);
		// Longshots		
		playerPattern.put(new Point(0, 5), 2);
		playerPattern.put(new Point(0, 6), 2);
		playerPattern.put(new Point(0, 7), 1);
		// Potential of getting turned on
		playerPattern.put(new Point(-1, 0), 4);
		playerPattern.put(new Point(1, 0), 4);
		playerPattern.put(new Point(1, -1), 4);

		playerWithLaserPattern = new HashMap<Point, Integer>(playerPattern);
		getTurretPattern(0).forEach((k, v) -> playerWithLaserPattern.merge(k, v, (v1, v2) -> v1 + v2));
	}

	public static Map<Point, Integer> getBulletPattern() {
		return bulletPattern;
	}

	public static Map<Point, Integer> getPlayerPattern(boolean hasLaser) {
		if (hasLaser) {
			return playerWithLaserPattern;
		}
		return playerPattern;
	}

	public static Map<Point, Integer> getTurretPattern(int frames_to_fire) {
		Map<Point, Integer> pattern = new HashMap<Point, Integer>();
		int threat = 10 - frames_to_fire * 2;
		if (threat < 0) {
			threat = 0;
		}
		int[] directions = { -1, 1 };
		for (int i : directions) {
			for (int x = i; x != 4 * i + i; x += i) {
				pattern.put(new Point(x, 0), threat);
			}
			for (int y = i; y != 4 * i + i; y += i) {
				pattern.put(new Point(0, y), threat);
			}
		}
		return pattern;
	}

}
