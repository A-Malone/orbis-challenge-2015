# Orbis Challenge 2015
The 2015 orbis challenge, put on by Orbis Access, was a challenge to create an AI to play a 2D game similar to the classic game, bomberman. 2 bots compete on a 2D grid to gather powerups, destroy turrets, and hunt the other player down, with the winner determined by a point system.

![wa vs sitan](https://cloud.githubusercontent.com/assets/8551479/11615261/06a300ee-9c2a-11e5-9c65-097a47ea80f9.gif)

This bot is the result of a collaboration between [A-Malone](https://github.com/A-Malone) and [Shadowen](https://github.com/Shadowen), created during a 24-hour hackathon.

Our Strategy
------------
Our bot uses potential fields to determine nearby safe spots on the map. Using an A* navigation algorithm with a heuristic weighted by distance, amount of potential danger along the path, and reward available at the end, the bot compares the cost of navigating to different objectives. Once it finds a suitable objective that is safe to accomplish and offers a high score reward, it will make a move towards that objective. Heuristics are then added on top of this to control firing and the activation of powerups.

Strengths
---------
The bot's navigation algorithm is the crux of the whole strategy, which leads to interesting emergent behavior. The bot chooses paths that routes around bullets, since those paths have lower potential. The bot also prefers to attack the enemy from behind because of the directional shape of the enemy's potential field. Because the algorithm is stateless, meaning the bot has no memory or prediction of the future, it can switch objectives effortlessly, choosing the objective that is optimal on each turn.

Weaknesses
----------
Parameter tunning is a large issue because the algorithm uses heuristics to judge danger, instead of simulating the future state of the game. Danger levels have to be high enough that the bot won't route through turret fire to avoid a longer path, but low enough that it won't be crippled by too much danger. In addition, parameters are used to tune the ROI of different objectives, critical danger levels before emergency safeguards are activated, and when to fire. This leads to an optimization problem with too many dimensions to solve by hand, especially in 24 hours, resulting in less than optimal performance.

Next Steps
----------
Because of the stateless nature of the bot, it kept switching between objectives as it moved around the map. As a result, it would move on to its next objective rather than waiting for a laser beam to go away so that it could pass. A future iteration could incorporate a cost for switching objectives so that the bot would be less prone to bouncing between objectives as the game progresses.

Finally, inital planning had a genetic algorithm tuning the necessary parameters. Unfortunately, this was cut from the final product in order to save time. However, a genetic algorithm could prove to be useful in order to optimize the tuning, as it is very difficult to evaluate the performance of the bot manually. However, the in-game score would be very handy for a genetic algorithm to use as a fitness function to maximize, while the several parameters such as bloodthirstiness, laziness, the relative importance of objectives, as well as the threat map shapes and intensities are perfect for a genetic algorithm to tune.

Results
-------
The iteration of our bot submitted to the challenge placed 10th out of 80 submitted bots. Our favorite iteration, however, discovered 5 minutes after the competition closed, involves tripling the 'bloodthirstiness' parameter, responsible for the reward for killing the enemy. While our bot would lose in points on large maps to tower killing bots, we would often be able to surprise combat-shy bots with our aggressive strategy. In the end, it was a ton of fun to watch.

In the following videos, our bot is A1 (orange).

![wa vs johnson_small](https://cloud.githubusercontent.com/assets/8551479/11615256/069187a6-9c2a-11e5-96e2-2ce881029752.gif)
![wa vs sean](https://cloud.githubusercontent.com/assets/8551479/11615257/0695b5f6-9c2a-11e5-9da2-a8069e164abd.gif)
![wa vs sean_small 3](https://cloud.githubusercontent.com/assets/8551479/11615259/069ab68c-9c2a-11e5-936b-5013e2174255.gif)
