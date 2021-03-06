import os

from agent import AgentABC
from ddpg.ddpg_agent import Agent as DDPGAgent
import numpy as np


class Agent(AgentABC):
    """Interacts with and learns from the environment."""

    def __init__(self, state_size, action_size, num_agents, random_seed):
        """
        Initialize multiple DDPG Agent object. this is just a vector of independent ddpg agents
            :param state_size (int): dimension of each state
            :param action_size (int): dimension of each action
            :param num_agents (int): number of agents in environment ot use ddpg
            :param random_seed (int): random seed
        """
        super().__init__(state_size, action_size, num_agents, random_seed)
        self.state_size = state_size
        self.action_size = action_size
        self.num_agents = num_agents
        self.agents = [DDPGAgent(state_size, action_size, 1, random_seed) for i in range(num_agents)]

    def step(self, states, actions, rewards, next_states, dones):
        """ see abstract class """
        for i in range(self.num_agents):
            states_single = states[i].reshape(1, self.state_size)
            actions_single = actions[i].reshape(1, self.action_size)
            next_states_single = next_states[i].reshape(1, self.state_size)
            dones_single = [dones[i]]
            rewards_single = [rewards[i]]
            self.agents[i].step(states_single, actions_single, rewards_single, next_states_single, dones_single)
        self.debug_loss = np.mean([agent.debug_loss for agent in self.agents])

    def act(self, state, add_noise=True):
        """ see abstract class """
        return [self.agents[i].act(state[i].reshape(1,self.state_size), add_noise) for i in range(self.num_agents)]

    def reset(self):
        """ see abstract class """
        for agent in self.agents:
            agent.reset()

    def load_weights(self, directory_path):
        """ see abstract class """
        super().load_weights(directory_path)
        for agent in range(self.num_agents):
            self.agents[agent].load_weights(os.path.join(directory_path, str(agent)))

    def save_weights(self, directory_path):
        """ see abstract class """
        # main directory
        super().save_weights(directory_path)
        for agent in range(self.num_agents):
            # sub directory for each agent
            self.agents[agent].save_weights(os.path.join(directory_path, str(agent)))

    def save_mem(self, directory_path):
        """ see abstract class """
        super().save_weights(directory_path)
        for agent in range(self.num_agents):
            self.agents[agent].save_mem(os.path.join(directory_path, str(agent)))

    def load_mem(self, directory_path):
        """ see abstract class """
        super().load_mem(directory_path)
        for agent in range(self.num_agents):
            self.agents[agent].load_mem(os.path.join(directory_path, str(agent)))

