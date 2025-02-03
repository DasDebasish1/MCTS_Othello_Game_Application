# Pre-requisites before running the application: -
1. Make sure you have installed the latest python.
2. Install PQT5 lib by 'pip install PyQt5' in CLI.

# Application:-
1. To run the application, please run main.py.
2. The tree plotter is only shown in iteration-based mode.
3. To change thread count or process count for any parallel MCTS, you need to enter the 'variants' folder and then select the parallel MCTS of your choice that you want to run; in the code, you will find the 'num_thread' parameter for multithread parallel and 'n_processes' parameter for parallel Multiprocessing, here you need change the value according to your requirement but make sure that your processor has that potential else it would impact the performance.
4. Once the program execution is completed, a result file will be generated.
5. Also note that parallel MCTS ending with 'PR' in the variant folder means it is parallel Multiprocessing. Example: - MCTSPARALLELROOTPR and without pr means parallel multithreading. Example: - MCTSPARALLELROOT
6. Human vs Human can only be played in 'Graphics mode'. Also, please note that if you want to play human vs human for 1 game, select 2 games instead; otherwise, the application will close just after 1 game is over. Therefore, just add one extra on top of number of games you want to play.
7. Kindly note a glitch in the tree plotter, where you may sometimes find the tree nodes getting overlapped. In this case, zoom in and out or vice versa after selecting the tree plotter area.

# Tuned UCT Constant List:-

UCT Constant for AMAF, alpha-AMAF,AMAF Cutoff, Rave, Rave-Max, Killer Rave, MCTS is 1.812
UCT Constant for all multithread parallel MCTS is 1.95
UCT Constant for all Multiprocessing based parallel MCTS is 2.1
UCT constant for all pruning algorithm is 1.8


# Application Implementation for the Othello game with MCTS enhancements

Othello game with MCTS enhancement application allows user to visually understand the work of MCTS with different enhancements associated with the Othello game. The App’s initial page is shown in Figure 1 below.
In the Application, the User needs to select the type of player from the drop-down menu, as shown below, highlighted in red. Once the type of player is selected and if it is AI, the User can choose different enhancement types, including standard MCTS. There are 14 enhancements, out of which one can be selected for gameplay (Othello) by each player.

![Project Logo](https://github.com/DasDebasish1/MCTS_Othello_Game_Application/blob/main/pic1.png)

* Figure 1: Initial screen of the application

Once the AI mode is selected, the User will get the option to choose the mode of play, which can be time-based or iteration-based, from the drop-down box, as shown in Figure 2. If Time-based is selected, the User can give each player time in seconds per play separately. However, if iteration-based is selected, players can increase or decrease iterations per play for each player. Moreover, users can select a time based for one player and iteration-based for the second player or vice-versa. The ‘Number of Games’ in Figure 2 allows the User to add the number of games it will run for.

![Project Logo](https://github.com/DasDebasish1/MCTS_Othello_Game_Application/blob/main/pic2.png)

* Figure 2: The application’s next screen to select the different modes of the play.

This app also allows users to change the UCT constant for each player, as shown above. The User must select performance or graphics options from the drop-down box highlighted in Figure 3.

![Project Logo](https://github.com/DasDebasish1/MCTS_Othello_Game_Application/blob/main/pic3.png)

* Figure 3: The application’s screen to select graphics or performance options

This application uses more thread and processing power to run in graphics mode, which includes showing the board and game’s process, as shown in Figure 3.
During gameplay (AI vs AI) in graphics mode, users can pause the game during runtime by left-clicking any area inside the tree plotter, as shown in Figure 4 and pressing the space bar. Please note that it may take a few milliseconds to pause the game. Also, users can scroll In and out or vice versa for the tree plotter.

![Project Logo](https://github.com/DasDebasish1/MCTS_Othello_Game_Application/blob/main/pic4.png)

* Figure 4: Showing the Graphical mode for the AI vs AI gameplay

Also, the graphic mode does not work time-based as it needs extra processing time. Due to added processing requirements in graphics mode, the actual performance of different enhancements cannot be justified. Hence, the performance mode is an option that the User can select to show the optimised game results without adding extra overheads. The performance mode works in both iterative-based and time-based modes.
Once the whole execution is completed, a text file will be generated in the program's location. This file will contain the average iteration over all the games executed for each player and their scores. Figure 5 shows the generated result in a text file.

![Project Logo](https://github.com/DasDebasish1/MCTS_Othello_Game_Application/blob/main/pic5.png)

* Figure 5: Generated text-file

Before running any program/application above, kindly go through the ‘Readme’ files in each game's folder inside the ‘code’ folder as shared. Fine-tuned UCT values for different enhancements are shared with the information on how to run it on your computer.
**During Gameplay:** When Human vs AI or Human vs Human is selected during the play, the user can hide possible moves by selecting the ‘hide possible move option’. In the Application, Player 1 holds black discs, whereas Player 2 holds the white discs. The application allows the user to move to the next game by clicking the ‘next button’ after the current game ends.

