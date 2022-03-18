from sklearn.metrics import mean_squared_error
from file import readTrainAndTestActions
import sys
import glob


def calculate_loss(expected_actions, predicted_actions):
    loss = mean_squared_error(expected_actions, predicted_actions)

    # print("Expected | Predicted")
    # for i in range(len(expected_actions)):
    #     print(str(expected_actions[i]) + " | " + str(predicted_actions[i]))

    print('loss')
    print(loss)

    return loss

# expected_actions, predicted_actions = readTrainAndTestActions(sys.argv[1], sys.argv[2])

# calculate_loss(expected_actions, predicted_actions)

def mean_loss_simulations():
    # loss_list = []
    count_files = 0
    sum_loss = 0
    test_files = glob.glob("simulationData/pioneerLongTrack/withOrientation/test/17_3_2022/*.txt")

    print('test_files')
    print(test_files)

    for file in test_files:
        expected_actions, predicted_actions = readTrainAndTestActions(sys.argv[1], file)

        loss = calculate_loss(expected_actions, predicted_actions)
        print('loss')
        print(loss)
        sum_loss += loss
        count_files += 1
        # loss_list.append(loss)

    # loss_list = sorted(loss_list)
    # print('loss_list')
    # print(loss_list)

    mean_loss = sum_loss / count_files
    print('mean_loss')
    print(mean_loss)

mean_loss_simulations()


