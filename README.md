# Orbis Challenge 2015
The 2015 orbis challenge, put on by Orbis Access, was a challenge to create an AI to play a 2D game similar to the classic game, bomberman. 2 bots compete on a 2D grid to gather powerups, destroy turrets, and hunt the other player down, with the winner determined by a points system.

Our Strategy
------------
Our bot uses the concept of influence mapping to determine the safest way to navigate the board to achieve it's goals. Using an A* navigation algorithm weighted by the distance, the amount of potential danger along the path, and the reward at the end, the bot compares the cost of navigating to different objectives. Once it finds the objective with the best return on investment, it will make the first move towards that objective. Heuristics are then added on top of this to control firing and the activation of powerups.

Strengths
---------
The bot's navigation algorithm is the crux of the whole strategy, and leads to interesting emergent behavior. The bot chooses paths that routes around bullets, since they are lower danger, and attacks the enemy preferentially from behind so as to avoid being attacked. Because the algorithm is stateless, meaning the bot has no memory or prediction of the future, it can switch objectives effortlessly, choosing the objective that is optimal on each turn.

Weaknesses
----------
Parameter tunning is a large issue because the algorithm uses heuristics to judge danger, instead of simulating the future state of the game. Danger levels have to be high enough that the bot won't route through turret fire to avoid a longer path, but low enough that it won't be crippled by too much danger. In addition, parameters are used to tune the ROI of different objectives, critical danger levels before emergency safeguards are activated, and when to fire. This leads to an optimization problem with too many dimensions to solve by hand, especially in 24 hours, resulting in less than optimal performance.

Results
-------
The iteration of our bot submitted to the challenge placed 10th out of 80 submitted bots. Our favorite iteration, however, was discovered 5 minutes after the competition closed, involves setting the 'bloodthirstiness' parameter, responsible for the reward for killing the enemy, way up. While our bot would lose to tower killing bots, bots that did not have good combat abilities would quickly fall prey to our aggressive strategy. In the end, it was a ton of fun to watch. <GIFs coming>
