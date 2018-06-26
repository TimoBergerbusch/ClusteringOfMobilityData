import itertools
import re
import random
import argparse

FILE_NAME = "BaseDatosMDE.txt"  # the dataset to infer the subsets from

# the header names that should be used
DATA_NAMES = ["origin", "destination", "reason", "MODO", "HMV", "RED", "duration",
              "distance", "strata", "age", "gender", "FEV", "ID"]  # the header names

# the lines that should be neglected in the FILE_NAME-file
IGNORE_LINE_VALUES = ['ORIGEN DESTINO MOTIVO MODO HMV RED DURACION DISTKM EST EDAD SEXO FEV ',
                      " "]

USED_IDS = []

random.seed(7811)


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
        assert not self.isBroken()
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
            if self.data[i] == "-1" or self.data[i] == "#N/A":
                return True
        return False

    def computeID(self):
        """
        computes an ID for this element. The ID is a random number between 1 and 150000.
        This is done, because the value should be just an identifier.
        If the numerical value is used it throws of every clustering and therefore indicate an error

        :return: the ID (int, 1<= value <= 150000)
        """

        guard = True
        while guard:
            id = random.randint(1, 500000)
            if id not in USED_IDS:
                guard = False

        USED_IDS.append(id)
        self.data[12] = id

    def compareTo(self, otherEntry):
        """
        compares a DataEntry to a given other DataEntry.
        The comparison is made based on the strata, gender and age.
        If all those 3 are equal we consider two DataEntries to be from the same person.
        Further logical reasoning could be made, through pathfinding with time and origin-destination constraints

        :param otherEntry: the other DataEntry one should compare to
        :return: a boolean value whether this DataEntry is equal to the given DataEntry
        """
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
        # self.computeIDs()
        if args.debug: print("INFORMATION :: Data Collection: length={}".format(len(self.data_entries)))
        for entry in self.data_entries:
            entry.writeDataEntry()

    # TODO currently first appearing
    # SHOULD: random or decidable
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
                    "ERROR :: Could not find enough elements for strata {} (has:{} should:{})".format(i + 1, buckets[i],
                                                                                                      length))

        newDataSet = DataCollection(equal_data_entries)
        return newDataSet

    def printToFile(self, fileName, mask):
        """
        prints the DataCollection into a file using a mask to indicate, which columns should be represented

        :param fileName: the name to save the items into
        :param mask: the mask to indicate column usage
        :return: -undef-
        """
        # self.computeIDs()
        with open(fileName, "w+") as file:
            file.write(get_used_headers(mask))

            file.write("\n")
            for entry in self.data_entries:
                file.write(''.join(entry.getData(mask)))
                file.write("\n")

    def computeIDs(self):
        # !!!IMPORTANT!!!
        # TODO: what if random Entries?
        # Then two action of the same person, which were consequtive in the original
        # are not neccassarily consequtive in the shrink-generate Set and therefore not be considered from the same person.
        USED_IDS = []
        if len(self.data_entries) == 0:
            if args.debug: print("WARNING :: Can not compute the IDs because the list is empty")
        for i in range(0, len(self.data_entries)):
            if i > 0 and self.data_entries[i].compareTo(self.data_entries[i - 1]):
                self.data_entries[i].data[12] = self.data_entries[i - 1].data[12]
            else:
                self.data_entries[i].computeID()

    def findRandomEntry(self, strata):
        """
        searches for a randomly placed DataEntry in the set, which is in the given strata

        NOTE: if no such element exists an error-message is printed and "None" is returned
        :param strata: the strata the random DataEntry should have
        :return: a random DataEntry of the given strata or None
        """
        start = random.randint(0, len(self.data_entries) - 1)
        index = start
        while (True):
            entry = self.data_entries[index]
            if int(entry.data[8]) == strata:
                return entry
            else:
                index = (index + 1) % len(self.data_entries)
                if index == start:
                    print('ERROR :: found no random element with the strata {}'.format(strata))
                    return None

    def shrink(self, length):
        # the absolute numbers in the original dataset
        # used for checking the ex. of that many elements
        absolute_numbers = [6963, 52265, 49404, 8772, 5536, 2038]
        # absolute_numbers = [6963, 52266, 49404, 8772, 5536, 2038]
        # the distribution in the original dataset
        relative_numbers = []
        for i in range(0, 6):
            relative_numbers.append(absolute_numbers[i] / 124979)
        abs_numbers = []
        new_data_entries = []
        for i in range(0, 6):
            abs_numbers.append(round(length * relative_numbers[i]))  # compute absolute number of values
            # abs_numbers.append(round(length * (relative_numbers[i] / 100)))  # compute absolute number of values
            if args.debug: print("INFORMATION :: Strata {} should contain {} elements".format(i + 1, abs_numbers[i]))

            if abs_numbers[i] > absolute_numbers[i]:  # check availability
                abs_numbers[i] = absolute_numbers[i]
                print("ERROR: Strata {} should contain more entries than there are".format(i + 1))
                # TODO:
                # print("Use max. available number or quit?(use/quit)")
                # read and decide

            # for j in range(0, abs_numbers[i]):
            # check for duplicates
            # new_data_entries.append(self.findRandomEntry(i + 1))
            count = 0
            index = 0
            while count < abs_numbers[i]:
                if index >= len(self.data_entries):
                    print("ERROR       :: index problem")
                    print("ERROR       :: Strata {} has overall less elements ({}) than its supposed to have ({})".format(i+1,count,abs_numbers[i]))
                    exit()
                if self.data_entries[index].data[8] == "{}".format(i + 1):
                    new_data_entries.append(self.data_entries[index])
                    count += 1
                index += 1

        new__data_collection = DataCollection(new_data_entries)
        return new__data_collection


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
            if args.debug: print("WARNING     :: BROKEN ENTITY! for element {}".format(element))
        else:
            data_entries.append(data_entry)
    return data_entries


# TODO: Merge both test set generators
def create_equal_testset(mask, data_collection):
    numbers = [100, 200, 500, 1000, 2000]

    for length in numbers:
        newSetName = "generatedTestSet-{}-{}.txt".format(length, args.distType)
        data_collection_changed = data_collection.equalDistribute(length)
        data_collection_changed.printToFile(newSetName, mask)


def create_shrink_testset(mask, data_collection):
    # numbers = [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 124979]
    numbers = [124979, 100000, 50000, 20000, 10000, 5000, 2000, 1000, 500, 200, 100]

    # if the current data_collection_changed is not empty and has more elements than
    #  currently desired compute based on it.
    for length in numbers:
        if length != 124979:
            newSetName = "generatedTestSet-{}-normal.txt".format(length)
        else:
            newSetName = "generatedTestSet-full-with-ID.txt"
        data_collection_changed = data_collection.shrink(length)
        data_collection_changed.printToFile(newSetName, mask)


# ---------------- START: arguments ----------------
parser = argparse.ArgumentParser(
    description='Create Testsets for of the mobility data using equal or normal distribution.')
# set defaults
parser.set_defaults(size=False)
parser.set_defaults(debug=False)
parser.set_defaults(distType="equal")

# create  exclusive group
size_parser = parser.add_mutually_exclusive_group(required=False)
#  create all testsets considered
size_parser.add_argument('-all', dest='size', action='store_true',
                         help="create all test sets considered to be possibly relevant. This creates for the "
                              "equally distributed version considering the lengths: 100, 200, 500, 1000, 2000 and for "
                              "the normally distributed the lengths: 100, 200, 500, 1000, 2000, 5000, 10000, 20000, "
                              "50000, 100000, 124979")
# create testset of desired size (NOTE: max 2038)
size_parser.add_argument('-size', metavar='size', type=int,
                         help='the size of the new testset (NOTE: for equal distribution a max. value of 2038 is '
                              'possible)')

# debug output flag
parser.add_argument('-debug', dest='debug', action='store_true', help='write (debug) information of current processes')

# mask changing
# create a exclusive flag for every header column
# default are always true except for strata.
# only if rapidminer can set flags

# change the distribution
parser.add_argument('-distType', metavar='distType', help='the type of distribution: (0) equal; (1) normal')
# parse the arguments
args = parser.parse_args()

# if debug flag is set also output the arguments themself
if args.debug: print('Choosen flags: {}'.format(args))
# ---------------- END: arguments ----------------

# ---------------- START: preprocessing ----------------

if args.debug: print("INFORMATION ::  Reading data file ({})".format(FILE_NAME))
# read the whole file named FILE_NAME
linesOfFile = read_file()
# clean the file from empty lines and the header
linesOfContent = clean_up_list(linesOfFile)
# parse into a list of DataEntries structure
dataEntries = parse_lines_of_content(linesOfContent)
# create a new DataCollection
data_collection = DataCollection(dataEntries)

# TODO: create a set based an precomputed IDs
# compute the IDs
if args.debug: print("INFORMATION ::  Compute IDs")
data_collection.computeIDs()

if args.debug: print("INFORMATION ::  Preprocessing finished")

# ---------------- END: preprocessing ----------------

# ---------------- START: mask ----------------
mask = [
    True,  # 0 - origin
    True,  # 1 - destination
    True,  # 2 - reason
    True,  # 3 - mean of transportation
    True,  # 4 - HVM?
    True,  # 5 - average time
    True,  # 6 - duration
    True,  # 7 - distance
    True,  # 8 - strata
    True,  # 9 - age
    True,  # 10 - gender
    True,  # 11 - FEV
    True  # 12 - the ID based on age, gender and strata
]
# ---------------- END: mask ----------------

# create all testsets if all-flag
if args.size == True:
    if args.debug:
        print("INFORMATION :: All-Flag is set")
        print("INFORMATION :: Create equal testsets")
    create_equal_testset(mask, data_collection)  # create all equally distributed
    if args.debug: print("INFORMATION :: Create normal testsets")
    create_shrink_testset(mask, data_collection)  # create all normally distributed
    if args.debug: print("INFORMATION :: Finished creating the sets")
    exit()  # exit, because every standart set is created

if args.debug: print(
    "INFORMATION :: Create a Testset with {} elements using {} distribution. ".format(args.size, args.distType))
newSetName = "generatedTestSet-{}-{}.txt".format(args.size, args.distType)  # the default name of the new set

if args.distType == 'equal':
    # equal distribution
    # TODO: maybe create subsets based on the given number (/6) to
    # have the same behavior in equal and normal distribution
    if args.size > 2038:  # check if max. indiviual value is exceeded
        print("WARNING     :: The maximal value for equal distribution is 2038.")
        print("           This value(2038) is further used.")
        args.size = 2038
    data_collection_changed = data_collection.equalDistribute(args.size)
elif args.distType == "normal":
    # normal distribution
    data_collection_changed = data_collection.shrink(args.size)
else:
    # case not known
    print("ERROR       :: There is no distribution type classed '{}'".format(args.distType))
    print("               The only suitable distribution types are:")
    print("                 - equal    using a fix number for all stratas (max. 2038)")
    print("                 - normal   have a total number of elements with the original distribution")
    exit()

if args.debug: print("INFORMATION :: Start to save into file named: '{}'".format(newSetName))
data_collection_changed.printToFile(newSetName, mask)  # save the new set
if args.debug: print("INFORMATION :: Program successfully finished")
