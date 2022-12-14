from .base_critic import BaseCritic
import tensorflow as tf
from infrastructure.tf_utils import build_mlp


class BootstrappedContinuousCritic(BaseCritic):
    def __init__(self, sess, hparams):
        self.sess = sess
        self.ob_dim = hparams['ob_dim']
        self.ac_dim = hparams['ac_dim']
        self.discrete = hparams['discrete']
        self.size = hparams['size']
        self.n_layers = hparams['n_layers']
        self.learning_rate = hparams['learning_rate']
        self.num_target_updates = hparams['num_target_updates']
        self.num_grad_steps_per_target_update = hparams['num_grad_steps_per_target_update']
        self.gamma = hparams['gamma']

        self._build()

    def _build(self):
        
        self.sy_ob_no, self.sy_ac_na, self.sy_adv_n = self.define_placeholders()

        self.critic_prediction = tf.squeeze(build_mlp(
            self.sy_ob_no,
            1,
            "nn_critic",
            n_layers=self.n_layers,
            size=self.size))
        self.sy_target_n = tf.placeholder(shape=[None], name="critic_target", dtype=tf.float32)
        self.critic_loss = tf.losses.mean_squared_error(self.sy_target_n, self.critic_prediction)

        self.critic_update_op = tf.train.AdamOptimizer(self.learning_rate).minimize(self.critic_loss)

    def define_placeholders(self):
        """
            Placeholders for batch batch observations / actions / advantages in actor critic
            loss function.


            returns:
                sy_ob_no: placeholder for observations
                sy_ac_na: placeholder for actions
                sy_adv_n: placeholder for advantages
        """
        sy_ob_no = tf.placeholder(shape=[None, self.ob_dim], name="ob", dtype=tf.float32)
        if self.discrete:
            sy_ac_na = tf.placeholder(shape=[None], name="ac", dtype=tf.int32)
        else:
            sy_ac_na = tf.placeholder(shape=[None, self.ac_dim], name="ac", dtype=tf.float32)
        sy_adv_n = tf.placeholder(shape=[None], name="adv", dtype=tf.float32)
        return sy_ob_no, sy_ac_na, sy_adv_n

    def forward(self, ob):
      
        return self.sess.run(self.critic_prediction, feed_dict={self.sy_ob_no: ob})

    def update(self, ob_no, next_ob_no, re_n, terminal_n):
        """
            Update the parameters of the critic.

            let sum_of_path_lengths be the sum of the lengths of the sampled paths
            let num_paths be the number of sampled paths

            arguments:
                ob_no: shape: (sum_of_path_lengths, ob_dim)
                next_ob_no: shape: (sum_of_path_lengths, ob_dim). The observation after taking one step forward
                re_n: length: sum_of_path_lengths. Each element in re_n is a scalar containing
                    the reward for each timestep
                terminal_n: length: sum_of_path_lengths. Each element in terminal_n is either 1 if the episode ended
                    at that timestep of 0 if the episode did not end

            returns:
                loss
        """



        for _ in range(self.num_target_updates):
            critic = self.forward(next_ob_no)
            target = re_n + self.gamma * critic * (1 - terminal_n)
            for _ in range(self.num_grad_steps_per_target_update):
                loss, _ = self.sess.run([self.critic_loss, self.critic_update_op], feed_dict={self.sy_ob_no: ob_no, self.sy_target_n: target})

        return loss
