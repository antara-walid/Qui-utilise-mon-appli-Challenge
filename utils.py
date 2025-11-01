import csv
import re

from typing import List

import pandas as pd


def extract_features_from_action(phrase) -> tuple:
    """
    Extracts components from a phrase with the pattern:
    action(screen)<configuration>$chaine$

    Returns a tuple of (action, screen, configuration, chaine) where each
    element is None if not present.
    """

    # More flexible pattern to handle optional components
    match = re.match(
        r'^([^(<$1]+)?'  # action (anything before (, <, $, or 1)
        r'(?:\(([^)]+)\))?'  # optional screen in parentheses
        r'(?:<([^>]+)>)?'  # optional configuration in angle brackets
        r'(?:\$([^$]+)\$)?$',  # optional chaine in dollar signs
        phrase.strip()
    )

    if not match:
        return None, None, None, None

    action, screen, configuration, chaine = match.groups()

    # Clean up whitespace
    action = action.strip() if action else None
    screen = screen.strip() if screen else None
    configuration = configuration.strip() if configuration else None
    chaine = chaine.strip().lower() if chaine else None

    # Return None for empty strings
    return (
        action if action and not re.match(r'^t\d+$', str(action)) else None,
        screen if screen else None,
        configuration if configuration else None,
        chaine if chaine else None
    )


def read_csv_file(file_path: str, has_header: bool = True) -> List[List[str]]:
    """
    Reads a CSV file and returns a list of rows.
    Handles files with inconsistent columns.
    """
    rows = []
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)

    if has_header:
        header = rows[0]
        data = rows[1:]
        return [header] + data
    return rows


class CSVDataProcessor:
    """
    Utility class designed to process training and testing CSV files containing user session data.

    Example:
        >>> with CSVDataProcessor("train.csv") as processor:
        >>>     train_dataframe = processor.get_processed_train_data()
        >>>     test_dataframe = processor.get_processed_test_data(test_data_csv_path="test.csv")
    """
    def __init__(self, train_data_csv_path):
        self.train_data_csv_path = train_data_csv_path
        self.data = None
        self.is_training_data = None
        self.headers = None

        self.possible_actions_set = set()
        self.possible_screens_set = set()
        self.possible_configurations_set = set()
        self.possible_chaines_set= set()

    def __enter__(self):
        self._initialise()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _initialise(self):
        """
        Reads the train CSV file and creates the headers
        """
        train_data = read_csv_file(self.train_data_csv_path)
        self.is_training_data = True
        self.data = train_data
        self.headers = self.create_headers()

    def extract_all_possible_features(self):
        """
        Extracts the following features:
        - All unique actions
        - All screens
        - All configurations
        - All chaines
        """
        index = 1
        if self.is_training_data:
            index = 2

        for row in self.data:
            for action in row[index:]:
                trimmed_action, screen, configuration, chaine = extract_features_from_action(action)
                if trimmed_action is not None:
                    self.possible_actions_set.add(trimmed_action)
                if screen is not None:
                    self.possible_screens_set.add(screen)
                if configuration is not None:
                    self.possible_configurations_set.add(configuration)
                if chaine is not None:
                    self.possible_chaines_set.add(chaine)

    def create_headers(self) -> list:
        """
        Creates and returns the csv or dataset headers using the extracted features
        """
        initial_columns = ["navigator", "total_actions", "session_duration", "avg_speed"]
        if self.is_training_data:
            initial_columns.insert(0, "user")
            self.extract_all_possible_features()

        # 1. possible actions features
        possible_actions_str = [f"occurrence of action '{action}' " for action in self.possible_actions_set]

        # 2. possible screens features
        possible_screens_str = [f"occurrence of screen '{screen}' " for screen in self.possible_screens_set]

        # 3. possible configuration features
        possible_configurations_str = [f"occurrence of configuration '{config}' " for config in self.possible_configurations_set]

        # 4. possible chaines features
        possible_chaine_str = [f"occurrence of chaine '{chaine}' " for chaine in self.possible_chaines_set]


        # # # add the headers
        # self.result[0].extend(initial_columns + possible_actions_str + possible_screens_str + possible_configurations_str + possible_chaine_str)

        return initial_columns + possible_actions_str + possible_screens_str + possible_configurations_str + possible_chaine_str

    def extract_data_from_row(self, row) -> list:
        """
        Extracts, computes and returns the following data from each row:
        - user (in the case of train.csv)
        - Navigator
        - Total number of actions in each session
        - Session duration
        - Average speed during the session
        - occurrences of each unique action
        - occurrences of each screen
        - occurrences of each configuration
        - occurrences of each chaine
        """
        result_row = []

        if self.is_training_data:
            result_row.append(row[0]) # 0. add user
            row = row[1:]

        result_row.append(row[0]) # 1. add the navigator

        actions = row[1:]
        all_actions = [action for action in actions if not re.match(r'^t\d+$', str(action)) ] # ignore columns with the form t-number

        total_actions = len(all_actions)
        result_row.append(total_actions) # 2. add total actions


        times = [action for action in actions if re.match(r'^t\d+$', str(action)) ] # get the times (form t-number)

        # get the last time and remove the initial t
        session_duration = times[-1][1:]

        result_row.append(session_duration) # 3. add session duration


        avg_speed = total_actions/int(session_duration) if int(session_duration) > 0 else 0
        result_row.append(avg_speed) # 4. add average speed

        # calculate the nbr of occurrences of all action related features
        possible_actions_occurrences = {}
        screens_occurrences = {}
        configurations_occurrences = {}
        chaines_occurrences = {}

        for action in actions:
            trimmed_action, screen, configuration, chaine = extract_features_from_action(action)
            if trimmed_action is not None:
                possible_actions_occurrences[trimmed_action] = possible_actions_occurrences.get(trimmed_action, 0) +1
            if screen is not None:
                screens_occurrences[screen] = screens_occurrences.get(screen, 0) +1
            if configuration is not None:
                configurations_occurrences[configuration] = configurations_occurrences.get(configuration, 0) + 1
            if chaine is not None:
                chaines_occurrences[chaine] = chaines_occurrences.get(chaine, 0) + 1


        # 4. add occurrences those occurrences to result row (warning the order is important)
        result_row.extend([possible_actions_occurrences.get(possible_action, 0) for possible_action in self.possible_actions_set ])
        result_row.extend([screens_occurrences.get(screen, 0) for screen in self.possible_screens_set ])
        result_row.extend([configurations_occurrences.get(config, 0) for config in self.possible_configurations_set ])
        result_row.extend([chaines_occurrences.get(chaine, 0) for chaine in self.possible_chaines_set ])

        return result_row

    def process_data(self, data=None, is_training_data = True):
        """
        Entry point for processing train or test csv data
        """
        headers = self.headers
        if not is_training_data :
            assert data is not None, "Data can not be None when processing test csv file"
            self.data = data
            headers=self.headers[1:]

        self.is_training_data = is_training_data
        processed_csv_data = [ self.extract_data_from_row(row) for row in self.data]

        return pd.DataFrame(data= processed_csv_data, columns=headers)

    def get_processed_train_data(self):
        """
        returns the processed train data
        """
        if self.data is None or self.headers is None:
            # method was not called inside context manager
            # should initialise before processing
            self._initialise()

        return self.process_data(is_training_data=True)

    def get_processed_test_data(self, test_data_csv_path):
        """
        returns the processed test data
        """
        if self.headers is None:
            self._initialise()

        test_data = read_csv_file(test_data_csv_path)
        self.is_training_data = False

        return self.process_data(data=test_data, is_training_data=False)


