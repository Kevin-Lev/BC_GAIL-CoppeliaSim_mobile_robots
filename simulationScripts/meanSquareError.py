from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from simulationScripts.file import readTrainAndTestActions
import sys
import glob


def calculate_mse(expected_actions, predicted_actions):
    loss = mean_squared_error(expected_actions, predicted_actions)

    print("Expected | Predicted")
    for i in range(len(expected_actions)):
        print(str(expected_actions[i]) + " | " + str(predicted_actions[i]))

    print('MSE - mean_squared_error')
    print(loss)

    return loss

def calculate_mae(expected_actions, predicted_actions):
    loss = mean_absolute_error(expected_actions, predicted_actions)

    # print("Expected | Predicted")
    # for i in range(len(expected_actions)):
    #     print(str(expected_actions[i]) + " | " + str(predicted_actions[i]))

    print('MAE - mean_absolute_error')
    print(loss)

    return loss

# expected_actions, predicted_actions = readTrainAndTestActions(sys.argv[1], sys.argv[2])

# 

def mean_loss_simulations(train_path, test_path):
    loss_list = []
    count_files = 0
    sum_loss = 0
    test_directory = test_path.split('pioneer_longTrack_')
    loss_txt = open(test_directory[0] + 'mean_loss_all_simulations.txt', 'w')
    test_files = glob.glob(test_directory[0] + "/pioneer_longTrack_*.txt")
    # test_files = glob.glob("simulationData/pioneerLongTrack/withOrientation/test/17_3_2022/*.txt")

    print('test_files')
    print(test_files)

    for file in test_files:
        expected_actions, predicted_actions = readTrainAndTestActions(train_path, file)

        loss = calculate_mse(expected_actions, predicted_actions)
        print('loss')
        print(loss)
        loss_list.append(loss)
        loss_txt.write(str(loss))
        loss_txt.write('\n')
        sum_loss += loss
        count_files += 1

    mean_loss = sum_loss / count_files
    print('mean_loss')
    print(mean_loss)

    loss_txt.write('-------------------------\n')
    loss_txt.write(str(mean_loss))
    loss_txt.close()

    return mean_loss, loss_list

# mean_loss_simulations()


