import numpy as np
import pytest
from numpy.typing import NDArray

from ch06_learning_technique.a_optimization import SGD
from ch06_learning_technique.d_reg_weight_decay import MultiLinearNN
from ch06_learning_technique.d_trainer import NormalTraier
from ch06_learning_technique.test_d_overfit_exp import _plot_accuracy
from dataset.mnist import load_mnist

EPOCHS = 20
HIDDEN_SIZES = (100, 100, 100, 100, 100)


# Use the module scope to load the MNIST data only once, then share it across
@pytest.fixture(scope="module")
def mnist_data() -> tuple[
    tuple[NDArray[np.floating], NDArray[np.floating]],
    tuple[NDArray[np.floating], NDArray[np.floating]],
]:
    """Return the MNIST data.

    Loads the MNIST dataset, normalizes the pixel values, and converts the
    labels to one-hot encoding.
    Returns:
        tuple: Tuple containing training and test data.
    """
    # Load MNIST data, returning a 60000x784 array for x and a nx10 array for t
    ((x_train, t_train), (x_test, t_test)) = load_mnist(normalize=True)
    # Use only 300 samples for testing the overfitting
    return (x_train[:1000], t_train[:1000]), (x_test, t_test)


@pytest.fixture(scope="module")
def overfit_nn(
    mnist_data: tuple[
        tuple[NDArray[np.floating], NDArray[np.floating]],
        tuple[NDArray[np.floating], NDArray[np.floating]],
    ],
) -> NormalTraier:
    """Train a overfitting NN without batch normalization and dropout.

    This is used for comparing the overfitting with weight decay and dropout.
    """
    # returning a 60000x784 array for x and a nx10 array for t
    ((x_train, t_train), (x_test, t_test)) = mnist_data

    # Initialization
    network = MultiLinearNN(
        input_size=784,
        hidden_sizes=HIDDEN_SIZES,
        output_size=10,
    )
    optimizer = SGD(lr=0.01)
    trainer = NormalTraier(
        network=network,
        optimizer=optimizer,
        x_train=x_train,
        t_train=t_train,
        x_test=x_test,
        t_test=t_test,
        epochs=EPOCHS,
        mini_batch_size=100,
    )

    # Train the network
    trainer.train()

    return trainer


def test_batch_normalization(
    overfit_nn: NormalTraier,
    mnist_data: tuple[
        tuple[NDArray[np.floating], NDArray[np.floating]],
        tuple[NDArray[np.floating], NDArray[np.floating]],
    ],
) -> None:
    """Evaluate the batch normalization."""
    # returning a 1000x784 array for x and a nx10 array for t
    ((x_train, t_train), (x_test, t_test)) = mnist_data

    # Initialization
    network = MultiLinearNN(
        input_size=784,
        hidden_sizes=HIDDEN_SIZES,
        output_size=10,
        use_batchnorm=True,
    )
    optimizer = SGD(lr=0.01)
    trainer = NormalTraier(
        network=network,
        optimizer=optimizer,
        x_train=x_train,
        t_train=t_train,
        x_test=x_test,
        t_test=t_test,
        epochs=EPOCHS,
        mini_batch_size=100,
    )

    # Train the network
    trainer.train()

    train_acc_list, test_acc_list = trainer.get_history_accuracy()
    (overfit_train_acc_list, overfit_test_acc_list) = (
        overfit_nn.get_history_accuracy()
    )
    # Set to True to plot the accuracy history for comparison
    plot_data = False
    if plot_data:
        _plot_accuracy(
            train_acc_list,
            test_acc_list,
            overfit_train_acc_list,
            overfit_test_acc_list,
        )
    assert train_acc_list[-1] > overfit_train_acc_list[-1]
    assert test_acc_list[-1] > overfit_test_acc_list[-1]
