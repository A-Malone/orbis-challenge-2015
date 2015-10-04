
public class Node {
	public int x;
	public int y;
	public int distanceFromStart = Integer.MAX_VALUE;
	public int heuristicCost = Integer.MAX_VALUE;
	public Node parent;

	public Node(int ix, int iy) {
		x = ix;
		y = iy;
	}
}
