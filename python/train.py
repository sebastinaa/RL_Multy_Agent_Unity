###################################
# Import Required Packages
import numpy as np
from agent import AgentABC
from mlagents.envs import UnityEnvironment
import os


def train_wrapper(env_config, wrapper_config):
    """
    Set the Training Parameters
    :param env_config: dictionary, used to pass parameters into the environment
    :param wrapper_config: dictionary of user defined variables.
    """
    # num_episodes (int): maximum number of training episodes
    num_episodes = wrapper_config['num_episodes']

    # scores_average_window (int): the window size employed for calculating the average score
    scores_average_window = wrapper_config['scores_avg_window']

    # solved_score (float): the average score required for the environment to be considered solved
    solved_score = wrapper_config['solved_score']

    # load_weights (bool): whether or not to start training with loaded weights
    load_weights = wrapper_config['load_weights']

    # weights_path: path to the directory containing the weights (same directory to save them)
    weights_path = wrapper_config['weights_path']
    if load_weights and not(os.path.isdir(weights_path)):
        print('weights dir does not exist')
        raise NotADirectoryError

    # save_mem (bool): whether or not to save memory
    save_mem = wrapper_config['save_mem']
    # load_mem (bool): whether or not to continue training with loaded memory
    load_mem = wrapper_config['load_mem']
    # mem_path: path to directory containing the memory to load
    mem_path = wrapper_config['mem_path']
    if load_mem and not(os.path.isdir(mem_path)):
        print('mem dir does not exist')
        raise NotADirectoryError

    # build_path: path to the build of the unity environment.
    build_path = None if wrapper_config['build'] == 'None' else wrapper_config['build']
    if (build_path is not None) and (not os.path.isfile(build_path)):
        print('--build is not a valid path')
        raise FileNotFoundError

    # no_graphics (bool): whether or not to start the environment without graphics (default = True in training)
    no_graphics_in = not wrapper_config['show_graphics']

    # agent_type (DDPG | MDDPG | MADDPG)
    agent_type = wrapper_config['agent']
    if not issubclass(agent_type, AgentABC):
        print('invalid agent type')
        raise TypeError

    # print_Agent_loss (bool): whether or not to print the agent's loss (mse for critic) after every episode
    print_agent_loss = wrapper_config['print_agent_loss']

    # save_log (bool): whether or not to save the episodes score (csv format, default is True)
    save_log = wrapper_config['save_score_log']

    # save_best_weights (bool): save also the best weights of the session (by average score)
    save_best_weights = wrapper_config['save_best_weights']

    # episode_scores (float): list to record the scores obtained from each episode
    episode_scores = []

    """
    Start the Unity Environment
    """
    env = UnityEnvironment(file_name=build_path, no_graphics=no_graphics_in)

    """
    Get The Unity Environment Brain
    Unity ML-Agent applications or Environments contain "BRAINS" which are responsible for deciding 
    the actions an agent or set of agents should take given a current set of environment (state) 
    observations. The Race environment has a single Brain, thus, we just need to access the first brain 
    available (i.e., the default brain). We then set the default brain as the brain that will be controlled.
    """
    # Get the default brain
    brain_name = env.brain_names[0]

    # Assign the default brain as the brain to be controlled
    brain = env.brains[brain_name]

    """
    Determine the size of the Action and State Spaces and the Number of Agents.
    The observation space consists of variables corresponding to Ray Cast in different direction, 
    velocity and direction.  
    Each action is a vector with 2 numbers, corresponding to steer left/right and brake/drive (in this order).
    each action is a number between -1 and 1.
    num_agents will correspond to the number of agent using the same brain -
    (since all cars use the same action / observation space they all use the same brain)
    if in the future one should have different cars use different observation space, 
    one will need to split them into different brains..
    """
    # Set the number of actions or action size
    action_size = brain.vector_action_space_size

    # Set the size of state observations or state size
    state_size = brain.vector_observation_space_size

    # Get number of agents in Environment
    env_info = env.reset(train_mode=True, config=env_config)[brain_name]
    num_agents = len(env_info.agents)
    print('\nNumber of Agents: ', num_agents)

    """
    Create an Agent from the Agent Class in Agent.py
    Any agent initialized with the following parameters.
        ======
        state_size (int): dimension of each state (required)
        action_size (int): dimension of each action (required)
        num_agents (int): number of agents in the unity environment
        seed (int): random seed for initializing training point (default = 0)
    
    Here we initialize an agent using the Unity environments state and action size and number of Agents
    determined above.
    """
    agent: AgentABC = agent_type(state_size=state_size,
                                 action_size=action_size[0], num_agents=num_agents, random_seed=0)

    # Load trained model weights
    if load_weights:
        agent.load_weights(weights_path)
    if load_mem:
        agent.load_mem(mem_path)

    """
    ###################################
    STEP 6: Run the Training Sequence
    The Training Process involves the agent learning from repeated episodes of behaviour 
    to map states to actions the maximize rewards received via environmental interaction.
    
    The agent training process involves the following:
    (1) Reset the environment at the beginning of each episode.
    (2) Obtain (observe) current state, s, of the environment at time t
    (3) Perform an action, a(t), in the environment given s(t)
    (4) Observe the result of the action in terms of the reward received and 
        the state of the environment at time t+1 (i.e., s(t+1))
    (5) Update agent memory and learn from experience (i.e, agent.step)
    (6) Update episode score (total reward received) and set s(t) -> s(t+1).
    (7) If episode is done, break and repeat from (1), otherwise repeat from (3).
    
    Below we also exit the training process early if the environment is solved. 
    That is, if the average score for the previous 100 episodes is greater than solved_score.
    """

    best_score = -np.inf    # used to determine the best average score so far (for saving best_weights)
    # loop from num_episodes
    for i_episode in range(1, num_episodes+1):
        # reset the unity environment at the beginning of each episode
        env_info = env.reset(train_mode=True, config=env_config)[brain_name]

        # get initial state of the unity environment
        states = env_info.vector_observations

        # reset the training agent for new episode
        agent.reset()

        # set the initial episode score to zero.
        agent_scores = np.zeros(num_agents)

        # Run the episode training loop;
        # At each loop step take an action as a function of the current state observations
        # Based on the resultant environmental state (next_state) and reward received update the agent ('step' method)
        # If environment episode is done, exit loop...
        # Otherwise repeat until done == true
        steps = 0
        while True:
            steps = steps+1
            # determine actions for the unity agents from current sate
            actions = agent.act(states)

            # send the actions to the unity agents in the environment and receive resultant environment information
            env_info = env.step(actions)[brain_name]

            next_states = env_info.vector_observations   # get the next states for each unity agent in the environment
            rewards = env_info.rewards                   # get the rewards for each unity agent in the environment
            dones = env_info.local_done           # see if episode has finished for each unity agent in the environment

            # Send (S, A, R, S') info to the training agent for replay buffer (memory) and network updates
            agent.step(states, actions, rewards, next_states, dones)

            # set new states to current states for determining next actions
            states = next_states

            # Update episode score for each unity agent
            agent_scores += rewards

            # If any unity agent indicates that the episode is done,
            # then exit episode loop, to begin new episode
            if np.any(dones):
                break

        # Add episode score to Scores and...
        # Calculate mean score over last 100 episodes
        # Mean score is calculated over current episodes until i_episode > 100
        episode_scores.append(np.mean(agent_scores))
        average_score = np.mean(episode_scores[i_episode-min(i_episode, scores_average_window):i_episode+1])

        # Print current and average score, number of steps in episode.
        print('\nEpisode {}\tEpisode Score: {:.3f}\tAverage Score: {:.3f}\tNumber Of Steps{}'.format(
            i_episode, episode_scores[i_episode-1], average_score, steps), end="")
        if print_agent_loss:
            # print agent's loss (useful for babysitting the training)
            print('\t episode loss: {}'.format(agent.debug_loss))

        if save_log:
            # Save the recorded Scores data (in weights path)
            if not (os.path.isdir(weights_path)):
                os.mkdir(weights_path)
            scores_filename = "Agent_Scores.csv"
            # noinspection PyTypeChecker
            np.savetxt(os.path.join(weights_path, scores_filename), episode_scores, delimiter=",")

        # Save trained  Actor and Critic network weights after each episode
        agent.save_weights(weights_path)
        if save_best_weights:
            if best_score < average_score:
                best_score = average_score
                agent.save_weights(weights_path+'_best')

        if save_mem and (i_episode % 50) == 0:
            agent.save_mem(mem_path)
        # Check to see if the task is solved (i.e,. average_score > solved_score over 100 episodes).
        # If yes, save the network weights and scores and end training.
        if i_episode > scores_average_window*2 and average_score >= solved_score:
            print('\nEnvironment solved in {:d} episodes!\tAverage Score: {:.3f}'.format(i_episode, average_score))
            break
    agent.save_mem(mem_path)

    """
    ###################################
    STEP 7: Everything is Finished -> Close the Environment.
    """
    env.close()

    # END :) #############
