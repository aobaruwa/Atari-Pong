import tensorflow as tf
import os

def build_mlp(input_placeholder, output_size, scope, n_layers, size, activation=tf.tanh, output_activation=None):
    output_placeholder = input_placeholder
    with tf.variable_scope(scope):
        for _ in range(n_layers):
            output_placeholder = tf.layers.dense(output_placeholder, size, activation=activation)  
        output_placeholder = tf.layers.dense(output_placeholder, output_size, activation=output_activation)  
    return output_placeholder

def create_tf_session(use_gpu, gpu_frac=0.6, allow_gpu_growth=True, which_gpu=0):
    if use_gpu:
        gpu_options = tf.GPUOptions(
            per_process_gpu_memory_fraction=gpu_frac,
            allow_growth=allow_gpu_growth)

        config = tf.ConfigProto(
            gpu_options=gpu_options,
            log_device_placement=False,
            allow_soft_placement=True,
            inter_op_parallelism_threads=1,
            intra_op_parallelism_threads=1)

        os.environ["CUDA_VISIBLE_DEVICES"] = str(which_gpu)
    else:

        config = tf.ConfigProto(device_count={'GPU': 0})
    sess = tf.Session(config=config)
    return sess

def lrelu(x, leak=0.2):
    f1 = 0.5 * (1 + leak)
    f2 = 0.5 * (1 - leak)
    return f1 * x + f2 * abs(x)
