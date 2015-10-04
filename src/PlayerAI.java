import java.util.*;
import java.util.Map.Entry;
import java.awt.Point;

public class PlayerAI extends ClientAI {	
	
	//----CONSTANTS
	//------------------------------------------------------------
	static final int POWERUP_SCORE = 200;
	static final int PLAYER_SCORE = 750;
	static final int TURRET_SCORE = 750;
	
	//States
	static final int FIND_POWER_UPS = 0;
	static final int TERMINATOR = 1;
	
	//----FIELDS
	//------------------------------------------------------------
	PotentialField potentialField;
	int state;
	
	public PlayerAI() {
		potentialField = new PotentialField();
		state = FIND_POWER_UPS;
	}

	@Override
	public Move getMove(Gameboard gameboard, Opponent opponent, Player player)
			throws NoItemException, MapOutOfBoundsException {
		
		//Update the potential field
		potentialField.updatePotentialMap(gameboard, opponent, player);
		
		Move next_move;
		
		//Get paths to the different powerups
		ArrayList<PowerUp> powerUps = gameboard.getPowerUps();
		if(powerUps.size() > 0){
			int shortest_length = Integer.MAX_VALUE;
			Queue<Point> shortest_path = null;
			
			for(PowerUp pup : powerUps){
				try {
					Queue<Point> path = potentialField.getBestPath(gameboard, player.x, player.y, pup.x, pup.y);
				} catch (NoPathException e) {
					
				}
			}
			next_move = shortest_path.peek();
		}
		else
		{
			next_move = Move.FORWARD;
		}		
		return next_move;
	}
	
	private Map<GameObjects, Integer> getObjectives(Gameboard gameboard, Opponent opponent){
		Map<GameObjects, Integer> map = new HashMap<GameObjects, Integer>();
		for(PowerUp pup : gameboard.getPowerUps()){
			map.put(pup, POWERUP_SCORE * objectiveWeight(pup));
		}
		map.put(opponent, PLAYER_SCORE * objectiveWeight(opponent));
		for(Turret tur : gameboard.getTurrets()){
			map.put(tur, TURRET_SCORE * objectiveWeight(tur));
		}
		return map;
	}
	
	private int objectiveWeight(GameObjects obj){
		switch(state){
		case FIND_POWER_UPS:
			if(obj instanceof PowerUp){
				return 2;
			}
			return 1;
		case TERMINATOR:
			if(obj instanceof Opponent){
				return 2;
			}
			return 1;
		default:
			return 1;
		}
	}
}
