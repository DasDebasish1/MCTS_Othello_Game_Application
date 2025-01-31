Pre-requisites before running the application: -
1. Make sure you have installed the latest python.
2. Install PQT5 lib by 'pip install PyQt5' in CLI.

Application:-
1. To run the application, please run main.py.
2. The tree plotter is only shown in iteration-based mode.
3. To change thread count or process count for any parallel MCTS, you need to enter the 'variants' folder and then select the parallel MCTS of your choice that you want to run; in the code, you will find the 'num_thread' parameter for multithread parallel and 'n_processes' parameter for parallel Multiprocessing, here you need change the value according to your requirement but make sure that your processor has that potential else it would impact the performance.
4. Once the program execution is completed, a result file will be generated.
5. Also note that parallel MCTS ending with 'PR' in the variant folder means it is parallel Multiprocessing. Example: - MCTSPARALLELROOTPR and without pr means parallel multithreading. Example: - MCTSPARALLELROOT
6. Human vs Human can only be played in 'Graphics mode'. Also, please note that if you want to play human vs human for 1 game, select 2 games instead; otherwise, the application will close just after 1 game is over. Therefore, just add one extra on top of number of games you want to play.
7. Kindly note a glitch in the tree plotter, where you may sometimes find the tree nodes getting overlapped. In this case, zoom in and out or vice versa after selecting the tree plotter area.

Tuned UCT Constant List:-

UCT Constant for AMAF, alpha-AMAF,AMAF Cutoff, Rave, Rave-Max, Killer Rave, MCTS is 1.812
UCT Constant for all multithread parallel MCTS is 1.95
UCT Constant for all Multiprocessing based parallel MCTS is 2.1
UCT constant for all pruning algorithm is 1.8


