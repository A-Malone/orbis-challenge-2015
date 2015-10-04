import java.awt.Point;
import java.util.Queue;

/**
 * A path to take and total cost of taking that path.
 * 
 * @author wesley
 *
 */
public class Path {
	public final Queue<Point> path;
	public final int cost;

	public Path(Queue<Point> ip, int ic) {
		path = ip;
		cost = ic;
	}
}
