
public class Node {
	int x;
	int y;
	int distanceFromStart = Integer.MAX_VALUE;
	int heuristicCost = Integer.MAX_VALUE;

	public Node(int ix, int iy) {
		x = ix;
		y = iy;
	}
}
