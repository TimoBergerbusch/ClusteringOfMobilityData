import itertools
import re

FILE_NAME = "BaseDatosMDE.txt"  # the dataset to infer the subsets from
DATA_NAMES = ["origin", "destination", "reason", "HMV", "RED" "mean of Transportation", "average Time", "duration",
              "distance", "age", "gender", "strata"]  # the header names
IGNORE_LINE_VALUES = ['ORIGEN DESTINO MOTIVO MODO HMV RED DURACION DISTKM EST EDAD SEXO FEV ',
                      " "]  # a list of values that should not be considered as a data containing line


class DataEntry:
    """
    A class to store a single data entry. This is further used to mask the desired columns
    """
    data = [
        -1,  # 0 - origin
        -1,  # 1 - destination
        -1,  # 2 - reason
        -1,  # 3 - mean of transportation
        -1,  # 4 - average time
        -1,  # 5 - duration
        -1,  # 6 - distance
        -1,  # 7 - age
        -1,  # 8 - gender
        -1,  # 9 - strata
    ]

    def __init__(self, data):
        """
        initializes a new DataEntry with the given data
        :param data: the data the entry should contain
        """
        self.data = data

    def writeDataEntry(self):
        """
        simply writes the data to this DataEntry
        :return: -undef-
        """
        print("data = {}".format(self.data))

    def getData(self, mask):
        """
        masks the data using a list of boolean values to indicate whether or not a column should be used.

        A True value indicates, that the column should be used
        :param mask: a list of boolean values
        :return: a list of the data masked by the values
        """
        assert len(mask) == len(self.data)
        s = ""
        for i in range(0, len(mask)):
            if mask[i]:
                s += "{}".format(self.data[i])
                s += " "
        return s

    def isBroken(self):
        """
        tests whether or not a given DataEntry is valid.
        A DataEntry is considered broken if any of it's values is 0.

        NOTE: further testing could be made
        :return: a boolean value indicating if the entry is broken/invalid
        """
        for i in range(0, len(self.data)):
            if self.data[i] == "-1":
                return True
        return False


class DataSet:
    data_entries = []

    def __init__(self, data_entries):
        self.data_entries = data_entries

    def getData(self, mask):
        ret = []
        for entry in self.data_entries:
            ret.append(entry.getData(mask))
        return ret

    def writeDataCollection(self):
        print("Data Collection: length={}".format(len(self.data_entries)))
        for entry in self.data_entries:
            entry.writeDataEntry()

    def equalDistribute(self, length):
        buckets = [0, 0, 0, 0, 0, 0]
        equal_data_entries = []
        for entry in self.data_entries:
            strata = int(entry.data[8]) - 1
            if buckets[strata] < length:
                buckets[strata] = buckets[strata] + 1
                equal_data_entries.append(entry)

        for i in range(0, 6):
            if buckets[i] < length:
                print(
                    "Could not find enough elements for strata {} (has:{} should:{})".format(i + 1, buckets[i], length))

        newDataSet = DataSet(equal_data_entries)
        return newDataSet

    def printToFile(self, fileName, mask):
        with open(fileName, "w+") as file:
            file.write(' '.join(DATA_NAMES))
            for entry in self.data_entries:
                file.write(''.join(entry.getData(mask)))
                file.write("\n")


def getUsedHeaders(mask):
    s = ""
    for i in itertools.compress(DATA_NAMES, mask):
        s += i + "\t"
    return s


def readFile():
    with open(FILE_NAME) as file:
        content = file.readlines()
        return [re.sub('\s+', ' ', x) for x in content]


def file_len(file):
    with open(file) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def cleanUpList(linesOfFile):
    cleanLines = []
    for line in linesOfFile:
        if not line in IGNORE_LINE_VALUES:
            cleanLines.append(line)
    return cleanLines


def getDataList(string):
    list = re.split(" ", string)
    if list[len(list) - 1] == "":
        del list[-1]
    return list


def parseIntoDataEntry(string):
    return DataEntry(getDataList(string))


def parseLinesOfContent(linesOfContent):
    data_entries = []
    for element in linesOfContent:

        # split = getDataList(element)
        # length = len(split)
        # if length != 12:
        #     print("length: {} for element: {}".format(length, split))

        data_entry = parseIntoDataEntry(element)

        if data_entry.isBroken():
            print("BROKEN ENTITY: for element {}".format(element))
        else:
            data_entries.append(data_entry)
    return data_entries


linesOfFile = readFile()
linesOfContent = cleanUpList(linesOfFile)
dataEntries = parseLinesOfContent(linesOfContent)

mask = [True, True, True, True, True, True, True, True, True, True, True, True]
# mask = [True, False, False, False, False, False, False, False, False, False, False, False]
length = 2
newSetName = "generatedTestSet-{}.txt".format(length)
data_collection = DataSet(dataEntries)
# print(data_collection.getData(mask))
# print(len(data_collection.data_entries))
data_collection_equal_dist = data_collection.equalDistribute(length)
# print(len(data_collection_equal_dist.data_entries))
data_collection_equal_dist.printToFile(newSetName, mask)
