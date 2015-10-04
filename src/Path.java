import java.awt.Point;
import java.util.Queue;

public class Path {
	public final Queue<Point> path;
	public final int cost;

	public Path(Queue<Point> ip, int ic) {
		path = ip;
		cost = ic;
	}
}
