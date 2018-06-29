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

# a seed to generate pseudo-random numbers
# (mainly for debug reasons)
random.seed(7811)

# the last ID used to enumerate all IDs
LAST_ID = 0

# the deduced different persons
PERSONS = []


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

    def write_data_entry(self):
        """
        simply writes the data to this DataEntry
        :return: -undef-
        """
        print("data = {}".format(self.data))

    def get_data(self, entry_mask):
        """
        masks the data using a list of boolean values to indicate whether or not a column should be used.

        A True value indicates, that the column should be used
        :param entry_mask: a list of boolean values
        :return: a list of the data masked by the values
        """
        assert len(entry_mask) == len(self.data)
        assert not self.is_broken()
        s = ""
        for i in range(0, len(entry_mask)):
            if entry_mask[i]:
                if i != 12:
                    s += "{}".format(self.data[i])
                else:
                    s += "{}".format(self.data[12].get_id())
                s += " "
        return s

    def is_broken(self):
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

    def create_person(self):
        """
        computes an ID for this element. The ID is a random number between 1 and 150000.
        This is done, because the value should be just an identifier.
        If the numerical value is used it throws of every clustering and therefore indicate an error

        :return: the ID (int, 1<= value <= 150000)
        """

        # guard = True
        # while guard:
        #     id = random.randint(1, 500000)
        #     if id not in USED_IDS:
        #         guard = False
        # USED_IDS.append(id)
        global LAST_ID
        LAST_ID += 1
        last = Person(LAST_ID, self.data[8], self.data[9], self.data[10])
        # last.append(self)
        PERSONS.append(last)
        self.data[12] = last

    def compare_to(self, other_entry):
        """
        compares a DataEntry to a given other DataEntry.
        The comparison is made based on the strata, gender and age.
        If all those 3 are equal we consider two DataEntries to be from the same person.
        Further logical reasoning could be made, through pathfinding with time and origin-destination constraints

        :param other_entry: the other DataEntry one should compare to
        :return: a boolean value whether this DataEntry is equal to the given DataEntry
        """
        if self.data[8] == other_entry.data[8] and self.data[9] == other_entry.data[9] and self.data[10] == \
                other_entry.data[10]:
            return True
        return False

    def get_person(self):
        return self.data[12]


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

    def get_data(self, collection_mask):
        """
        gets a list, where every entry is the result of get_data called on every DataEntry using the same mask
        :param collection_mask: the mask indicating which columns shall be used
        :return: a list of strings
        """
        ret = []
        for entry in self.data_entries:
            ret.append(entry.get_data(collection_mask))
        return ret

    def print_data_collection(self, collection_mask):
        """
        writes the information of all DataEntries and the length of the DataCollection
        :return: -undef-
        """
        # self.compute_persons()
        if args.debug:
            print("INFORMATION :: Data Collection: length={}".format(len(self.data_entries)))
        for entry in self.data_entries:
            # entry.write_data_entry()
            print("{}".format(entry.get_data(collection_mask)))

    def equal(self, length):
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

        new_data_set = DataCollection(equal_data_entries)
        return new_data_set

    def save_into_file(self, file_name, collection_mask):
        """
        prints the DataCollection into a file using a mask to indicate, which columns should be represented

        :param file_name: the name to save the items into
        :param collection_mask: the mask to indicate column usage
        :return: -undef-
        """
        # self.compute_persons()
        with open(file_name, "w+") as file:
            file.write(get_used_headers(collection_mask))

            file.write("\n")
            for entry in self.data_entries:
                file.write(''.join(entry.get_data(collection_mask)))
                file.write("\n")

    def compute_persons(self):
        # USED_IDS = []
        if len(self.data_entries) == 0:
            if args.debug:
                print("WARNING :: Can not compute the IDs because the list is empty")
        for i in range(0, len(self.data_entries)):

            curr = self.data_entries[i]
            prev = self.data_entries[i - 1]

            # compare if two adjacent DataEntrys are equal
            if i > 0 and curr.compare_to(prev):
                # if so give them the same ID
                curr.data[12] = prev.get_person()
                # print("{} : current ID = prev ID, so same Person with ID {}".format(i + 1, curr.get_person().get_id()))
                curr.get_person().add(curr)
            else:
                # otherwise it gets a new ID
                curr.create_person()
                # print("New Person with ID:{} and size {}".format(curr.get_person().get_id(),
                #                                                  len(curr.get_person().movements)))
                curr.get_person().add(curr)
                # print("now has size {}".format(len(curr.get_person().movements)))

    @DeprecationWarning
    def find_random_entry_of_strata(self, strata):
        """
        searches for a randomly placed DataEntry in the set, which is in the given strata

        NOTE: if no such element exists an error-message is printed and "None" is returned
        :param strata: the strata the random DataEntry should have
        :return: a random DataEntry of the given strata or None
        """
        start = random.randint(0, len(self.data_entries) - 1)
        index = start
        while True:
            entry = self.data_entries[index]
            if int(entry.data[8]) == strata:
                return entry
            else:
                index = (index + 1) % len(self.data_entries)
                if index == start:
                    print('ERROR :: found no random element with the strata {}'.format(strata))
                    return None

    def shrink(self, length):
        assert len(self.data_entries) >= length - 1

        # if the shrunken set should contain the same number of elements just return a copy
        if len(self.data_entries) == length:
            new__data_collection = DataCollection(self.data_entries)
            return new__data_collection

        # the absolute numbers in the original dataset
        # used for checking the ex. of that many elements
        # WARNING: Only works with the complete set!
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
            # if args.debug: print(
            #     "INFORMATION ::        Strata {} should contain {} elements".format(i + 1, abs_numbers[i]))

            if abs_numbers[i] > absolute_numbers[i]:  # check availability
                abs_numbers[i] = absolute_numbers[i]
                print("ERROR: Strata {} should contain more entries than there are".format(i + 1))
                # TODO:
                # print("Use max. available number or quit?(use/quit)")
                # read and decide

            # for j in range(0, abs_numbers[i]):
            # check for duplicates
            # new_data_entries.append(self.find_random_entry_of_strata(i + 1))
            count = 0
            index = 0
            while count < abs_numbers[i]:
                if index >= len(self.data_entries):
                    print("ERROR       :: index problem")
                    print(
                        "ERROR       :: Strata {} has overall less elements ({}) than its supposed to have ({})".format(
                            i + 1, count, abs_numbers[i]))
                    exit()
                if self.data_entries[index].data[8] == "{}".format(i + 1):
                    new_data_entries.append(self.data_entries[index])
                    count += 1
                index += 1

        new__data_collection = DataCollection(new_data_entries)
        return new__data_collection

    def create_all_test_sets(self, collection_mask):
        """
        creates all possible test sets considered, filtered by a mask.
        All those sets get stored in the corresponding files directly
        :param collection_mask: the mask used within the methods 'equal' and 'shrink'
        :return: -none-
        """
        numbers = [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]

        for length in numbers:
            # equal test sets
            if length <= 2000:  # only possible till 2038 items per strata
                if args.debug:
                    print("INFORMATION :: create equal Testset of length: {}".format(length))
                new_set_name = "generatedTestSet-{}-equal.txt".format(length)
                new_test_set = self.equal(length)
                new_test_set.save_into_file(new_set_name, collection_mask)

            # normal test sets
            new_set_name = "generatedTestSet-{}-normal.txt".format(length)
            if args.debug:
                print("INFORMATION ::    create normal Testset of length: {}".format(length))
            new_test_set = self.shrink(length)
            new_test_set.save_into_file(new_set_name, collection_mask)

        # also create the complete Testset
        if args.debug:
            print("INFORMATION :: save complete Testset of length: 124979")
        data_collection.save_into_file("generatedTestSet-full-with-ID.txt", collection_mask)

        create_person_vector_file()

        # 'Finished'-message
        if args.debug:
            print("INFORMATION :: finished creating all Testsets")
            print("INFORMATION :: Programm finished")


class Person:
    """
    a class to store a separate person defined by the parameters:
        strata, age, and gender
    In this class all movements considered to be from the same person are stored.
    It also provides an ID.
    """

    def __init__(self, pid, strata, age, gender):
        self.pid = pid
        self.movements = []
        self.parameters = [strata, age, gender]

    def add(self, e):
        """
        adds a movement to the person
        :param e: the new movement
        :return: -none-
        """
        self.movements.append(e)

    def print(self):
        """
        prints a String of information about the person using 'get_data'
        :return:
        """
        print(self.get_data())
        # print("Person (id={}): {}".format(self.pid, self.movements))

    def get_id(self):
        return self.pid

    def get_data(self):
        """

        :return:
        """
        return "id = {}; strata = {}; age = {}; gender = {}; |movements| = {}]".format(self.pid, self.parameters[0],
                                                                                       self.parameters[1],
                                                                                       self.parameters[2],
                                                                                       len(self.movements))

    def compute_vector(self):
        """
        The vetor has the form (with # as number):
         #origin1 ... #origin413 #destination1 ... #destination413 AM MD PM MN #reason1 ... #reason7 #MoT1...#MoT7 SD SS G A
        where MoT= mean of transportation
        SD = sum duration
        SS = sum distance
        G = gender
        A = age
        Concluded this has the size 848.
        :return: the vector
        """
        lst = [0] * (2 * 413 + 4 + 7 + 7)
        sum_of_duration = 0
        sum_of_way = 0
        for entry in self.movements:
            sum_of_duration += int(float(entry.data[6]))
            sum_of_way += int(float(entry.data[7]))

            lst[int(float(entry.data[0]))] += 1  # add one to origin count
            lst[413 + int(float(entry.data[1]))] += 1  # add one to destination count

            if entry.data[5] == "AM":
                lst[2 * 413] += 1
            elif entry.data[5] == "MD":
                lst[2 * 413 + 1] += 1
            elif entry.data[5] == "PM":
                lst[2 * 413 + 2] += 1
            elif entry.data[5] == "MN":
                lst[2 * 413 + 3] += 1
            lst[2 * 413 + 4 + int(float(entry.data[2])) - 1] += 1  # reason
            lst[2 * 413 + 4 + 7 + int(float(entry.data[3])) - 1] += 1  # mean of trans

        lst.append(sum_of_duration)  # summe der dauer
        lst.append(sum_of_way)  # summe der strecke
        lst.append(int(float(self.parameters[2])))  # geschlecht
        lst.append(int(float(self.parameters[1])))  # alter

        return lst


def get_used_headers(header_mask):
    """
    returns the items of DATA_NAMES as a string seperated by tabulators

    :param header_mask: the mask, which columns shall be represented
    :return: a string
    """
    s = ""
    for i in itertools.compress(DATA_NAMES, header_mask):
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


def clean_up_list():
    """
    cleans up a list of strings considering the entries in IGNORE_LINE_VALUES. If an entry is contained in that list
    it gets neglected
    :return: the cleaned list of strings
    """
    clean_lines = []
    for line in linesOfFile:
        if line not in IGNORE_LINE_VALUES:
            clean_lines.append(line)
    return clean_lines


def get_data_list(string):
    """
    splits a string based on spaces and ignores empty parts.
    This could happen if the string begins or ends with a space
    :param string: the string to split
    :return: a list of entries contained in the string
    """
    lst = re.split(" ", string)
    if lst[len(lst) - 1] == "":
        del lst[-1]
    return lst


def parse_data_entry(string):
    """
    parses a list of entries into the DataEntry class structure
    :param string: a list of data
    :return: a DataEntry instance
    """
    lst = get_data_list(string)
    lst.append("NO ID")
    return DataEntry(lst)


def parse_lines_of_content():
    """
    parses the cleaned lines of a file and parses them into a DataEntries' list
    :return: a list of DataEntries
    """
    data_entries = []
    if args.debug:
        print_progressbar(0, len(linesOfContent) - 1, prefix='INFORMATION ::', suffix='Complete', length=50)
    for i in range(0, len(linesOfContent)):
        element = linesOfContent[i]
        if args.debug:
            print_progressbar(i, len(linesOfContent) - 1, prefix='INFORMATION ::', suffix='Complete',
                              length=50)
        data_entry = parse_data_entry(element)

        if data_entry.is_broken():
            if args.debug:
                print("WARNING     :: BROKEN ENTITY! for element {}".format(element))
        else:
            data_entries.append(data_entry)
    return data_entries


def create_person_vector_file():
    """
    creates the file 'person_vector_data.txt' with a vector for each person.

    :return: -none-
    """
    if args.debug:
        print("INFORMATION :: Vector Data of Persons")
    file_name = "person_vector_data.txt"
    with open(file_name, "w+") as file:
    
        # generate header 
        header_string = ""
        for i in range(1, 413):
            header_string += "o{} ".format(i)
        for i in range(1, 413):
            header_string += "d{} ".format(i)
        header_string += "AM MD PM MN "
        header_string += "r1 r2 r3 r4 r5 r6 r7"
        header_string += "MoT1 MoT2 MoT3 MoT4 MoT5 MoT6 MoT7"
        header_string += "SD SS G A"
        
        file.write(header_string)
        
        file.write("\n")
        if args.debug:
            print_progressbar(0, len(PERSONS) - 1, prefix='INFORMATION ::', suffix='Complete', length=50)
        # for person in PERSONS:
        for i in range(0, len(PERSONS)):
            person = PERSONS[i]
            if args.debug:
                print_progressbar(i, len(PERSONS) - 1, prefix='INFORMATION ::', suffix='Complete', length=50)
            file.write(" ".join(str(x) for x in person.compute_vector()))
            file.write("\n")


# Print iterations progress
def print_progressbar(iteration, total, prefix='INFORMATION :: ', suffix='', decimals=1, length=100, fill='█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()


# ---------------- START: arguments ----------------
parser = argparse.ArgumentParser(
    description='Create Testsets for of the mobility data using equal or normal distribution.')
# set defaults
parser.set_defaults(size=False)
parser.set_defaults(debug=False)
parser.set_defaults(vector=False)
parser.set_defaults(distType="equal")

# create  exclusive group
size_parser = parser.add_mutually_exclusive_group(required=False)
#  create all testsets considered
size_parser.add_argument('-all', dest='size', action='store_true',
                         help="create all test sets considered to be possibly relevant. This creates for the "
                              "equally distributed version considering the lengths: 100, 200, 500, 1000, 2000 and for "
                              "the normally distributed the lengths: 100, 200, 500, 1000, 2000, 5000, 10000, 20000, "
                              "50000, 100000, 124979. Also it generates a person vector file.")
# create testset of desired size (NOTE: max 2038)
size_parser.add_argument('-size', metavar='size', type=int,
                         help='the size of the new testset (NOTE: for equal distribution a max. value of 2038 is '
                              'possible)')

# vector flag
parser.add_argument('-vector', dest='vector', action='store_true', help='create a vector of person data')

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
if args.debug:
    print('Choosen flags: {}'.format(args))
# ---------------- END: arguments ----------------

# ---------------- START: preprocessing ----------------

if args.debug:
    print("INFORMATION :: Reading data file ({})".format(FILE_NAME))
# read the whole file named FILE_NAME
linesOfFile = read_file()
# clean the file from empty lines and the header
linesOfContent = clean_up_list()
# parse into a list of DataEntries structure
dataEntries = parse_lines_of_content()
# create a new DataCollection
data_collection = DataCollection(dataEntries)

# TODO: create a set based an precomputed IDs
# compute the IDs
if args.debug:
    print("INFORMATION :: Compute IDs")
data_collection.compute_persons()

if args.debug:
    print("INFORMATION :: Preprocessing finished")

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


# data_collection.print_data_collection(mask)

# print(len(PERSONS[0].compute_vector()))
# create_Person_Vector_File()
# for person in PERSONS:
#     print(person.get_data())
# print(person.compute_vector())
# exit()

# create all testsets if all-flag
# (NOTE: has to be checked against True, since it could be a size number and therefore is an int, but
# 'if args.size:' would still be evaluated to True)
if args.size is True:
    if args.debug:
        print("INFORMATION :: All-Flag is set")
        print("INFORMATION :: Create equal testsets")
    data_collection.create_all_test_sets(mask)
    exit()  # exit, because every standard set is created

if args.vector:
    if args.debug:
        print("INFORMATION :: Create Person-Vector set")
    create_person_vector_file()
    if args.debug:
        print("INFORMATION :: Person-Vector set saved in: 'person_vector_data.txt'")

# quit if there is no size
if not args.size:
    if args.debug:
        print("INFORMATION :: No size given")
        print("INFORMATION :: Operation finished")
    exit()

if args.debug:
    print("INFORMATION :: Create a Testset with {} elements using {} distribution. ".format(args.size, args.distType))
newSetName = "generatedTestSet-{}-{}.txt".format(args.size, args.distType)  # the default name of the new set

if args.distType == 'equal':
    # equal distribution
    # TODO: maybe create subsets based on the given number (/6) to
    # have the same behavior in equal and normal distribution
    if args.size > 2038:  # check if max. indiviual value is exceeded
        print("WARNING     :: The maximal value for equal distribution is 2038.")
        print("           This value(2038) is further used.")
        args.size = 2038
    data_collection_changed = data_collection.equal(args.size)
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

if args.debug:
    print("INFORMATION :: Start to save into file named: '{}'".format(newSetName))
# noinspection PyUnboundLocalVariable
data_collection_changed.save_into_file(newSetName, mask)  # save the new set
if args.debug:
    print("INFORMATION :: Program successfully finished")
