import java.awt.Point;
import java.util.HashMap;
import java.util.Map;

public class InfluenceShapes {
	public static Map<Point, Integer> getBulletPattern() {
		Map<Point, Integer> pattern = new HashMap<Point, Integer>();
		
		//Forward line
		pattern.put(new Point(0,1), 10);
		pattern.put(new Point(0,2), 9);
		pattern.put(new Point(0,3), 6);
		pattern.put(new Point(0,4), 4);
		
		//Side threats
		pattern.put(new Point( 1,1), 4);
		pattern.put(new Point(-1,1), 4);
		pattern.put(new Point( 2,1), 2);
		pattern.put(new Point(-2,1), 2);
		
		return pattern;
	}
	
	public static Map<Point, Integer> getPlayerPattern() {
		Map<Point, Integer> pattern = new HashMap<Point, Integer>();
		
		//Potential of being imminently shot at
		pattern = getBulletPattern();
		
		//Longshots
		pattern.put(new Point( 0, 5), 2);
		pattern.put(new Point( 0, 6), 2);
		pattern.put(new Point( 0, 7), 1);
		
		//Potential of getting turned on
		pattern.put(new Point(-1, 0), 4);
		pattern.put(new Point( 1, 0), 4);
		pattern.put(new Point( 1,-1), 4);	
		
		return pattern;
	}
	
	public static Map<Point, Integer> getTurretPattern(int frames_to_fire) {
		Map<Point, Integer> pattern = new HashMap<Point, Integer>();
		
		int threat = 10-frames_to_fire*2;
		if(threat<0){threat = 0;}		
		
		int[] directions = {-1, 1};
		for(int i : directions){
			for(int x = i; x != 4*i + i; x+=i){
				pattern.put(new Point(x, 0), threat);
			}
			for(int y = i; y != 4*i + i; y+=i){
				pattern.put(new Point(0, y), threat);
			}
		}
		return pattern;
	}
}
