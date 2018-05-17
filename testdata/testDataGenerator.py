import itertools
import re
import random

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
        -1,  # 4 - HVM?
        -1,  # 5 - average time
        -1,  # 6 - duration
        -1,  # 7 - distance
        -1,  # 8 - strata
        -1,  # 9 - age
        -1,  # 10 - gender
        -1,  # 11 - FEV
        "NO ID"  # 12#  - the ID based on age, gender and strata
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

    def computeID(self):
        # self.data[12] = "Age:{};Gender:{};Strata:{}".format(self.data[9], self.data[10], self.data[8])
        self.data[12] = random.randint(1,150000)

    def compareTo(self, otherEntry):
        if self.data[8] == otherEntry.data[8] and self.data[9] == otherEntry.data[9] and self.data[10] == \
                otherEntry.data[10]:
            return True
        return False


class DataCollection:
    """
    A collection of DataEntries used to compute the subsets from
    """

    data_entries = []  # the list of data entries

    def __init__(self, data_entries):
        """
        creates a new DataCollection
        :param data_entries: the DataEntries to store
        """
        self.data_entries = data_entries

    def getData(self, mask):
        """
        gets a list, where every entry is the result of getData called on every DataEntry using the same mask
        :param mask: the mask indicating which columns shall be used
        :return: a list of strings
        """
        ret = []
        for entry in self.data_entries:
            ret.append(entry.getData(mask))
        return ret

    def writeDataCollection(self):
        """
        writes the information of all DataEntries and the length of the DataCollection
        :return: -undef-
        """
        self.computeIDs()
        print("Data Collection: length={}".format(len(self.data_entries)))
        for entry in self.data_entries:
            entry.writeDataEntry()

    def equalDistribute(self, length):
        """
        creates a new DataCollection of DataEntries containing length-many items of every strata.
        NOTE: currently if not enough DataEntries for a strata are found we return simply less items

        :param length: the number of elements of the same strata
        :return: a DataCollection of DataEntries witrh length 0<= length <= 6*length
        """
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

        newDataSet = DataCollection(equal_data_entries)
        return newDataSet

    def printToFile(self, fileName, mask):
        """
        prints the DataCollection into a file using a mask to indicate, which columns should be represented

        :param fileName: the name to save the items into
        :param mask: the mask to indicate column usage
        :return: -undef-
        """
        self.computeIDs()
        with open(fileName, "w+") as file:
            file.write(' '.join(DATA_NAMES))
            file.write("\n")
            for entry in self.data_entries:
                file.write(''.join(entry.getData(mask)))
                file.write("\n")

    def computeIDs(self):
        if len(self.data_entries) == 0:
            print("Can not compute the IDs because the list is empty")
        for i in range(0, len(self.data_entries)):
            if i > 0 and self.data_entries[i].compareTo(self.data_entries[i - 1]):
                self.data_entries[i].data[12] = self.data_entries[i - 1].data[12]
            else:
                self.data_entries[i].computeID()


def get_used_headers(mask):
    """
    returns the items of DATA_NAMES as a string seperated by tabulators

    :param mask: the mask, which columns shall be represented
    :return: a string
    """
    s = ""
    for i in itertools.compress(DATA_NAMES, mask):
        s += i + "\t"
    return s


def read_file():
    """
    opens and reads the file named FILE_NAME line by line and substitutes all tabulator entries with a space
    :return: a list of all lines in the file
    """
    with open(FILE_NAME) as file:
        content = file.readlines()
        return [re.sub('\s+', ' ', x) for x in content]


def clean_up_list(linesOfFile):
    """
    cleans up a list of strings considering the entries in IGNORE_LINE_VALUES. If an entry is contained in that list it's neglected
    :param linesOfFile: the list of strings
    :return: the cleaned list of strings
    """
    cleanLines = []
    for line in linesOfFile:
        if not line in IGNORE_LINE_VALUES:
            cleanLines.append(line)
    return cleanLines


def get_data_list(string):
    """
    splits a string based on spaces and ignores empty parts.
    This could happen if the string begins or ends with a space
    :param string: the string to split
    :return: a list of entries contained in the string
    """
    list = re.split(" ", string)
    if list[len(list) - 1] == "":
        del list[-1]
    return list


def parse_DataEntry(string):
    """
    parses a list of entries into the DataEntry class structure
    :param string: a list of data
    :return: a DataEntry instance
    """
    list = get_data_list(string)
    list.append("NO ID")
    return DataEntry(list)


def parse_lines_of_content(linesOfContent):
    """
    parses the cleaned lines of a file and parses them into a DataEntries' list
    :param linesOfContent: the cleaned lines of data
    :return: a list of DataEntries
    """
    data_entries = []
    for element in linesOfContent:
        data_entry = parse_DataEntry(element)

        if data_entry.isBroken():
            print("BROKEN ENTITY: for element {}".format(element))
        else:
            data_entries.append(data_entry)
    return data_entries


# read the whole file named FILE_NAME
linesOfFile = read_file()
# clean the file from empty lines and the header
linesOfContent = clean_up_list(linesOfFile)
# parse into a list of DataEntries structure
dataEntries = parse_lines_of_content(linesOfContent)
# create a new DataCollection
data_collection = DataCollection(dataEntries)
# ---------------- START: editable part ----------------
# +++ edit the columns generated here +++
mask = [True,  # origin
        True,  # destination
        True,  # reason
        True,  # HMV
        True,  # RED
        True,  # mean of Transportation
        True,  # average Time
        True,  # duration
        True,  # distance
        True,  # age
        True,  # gender
        False,  # strata - NOTE: should stay False in order to test
        True  # denote whether an ID should be created
        ]
# +++ edit the numbers of elements within each strata +++
# (NOTE: currently equal for al strata iff enough available)
length = 2000
# ---------------- END: editable part ----------------


# set the name to save the set in
newSetName = "generatedTestSet-{}.txt".format(length)

# creates a equal distributed set based on the length
data_collection_equal_dist = data_collection.equalDistribute(length)
# saves the new set in the new file
data_collection_equal_dist.printToFile(newSetName, mask)
